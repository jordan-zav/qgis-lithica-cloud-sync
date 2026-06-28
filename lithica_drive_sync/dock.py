from pathlib import Path

from qgis.PyQt.QtCore import QLocale, Qt
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDockWidget,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qgis.core import QgsApplication, QgsTask

from .cache import ProjectCache
from .config import load_oauth_config
from .credential_store import QgisCredentialStore
from .drive_client import DriveClient
from .flows import connect_and_list
from .i18n import Translator
from .layers import open_project_layers
from .oauth import authorize_interactive, refresh_access_token
from .sync_service import SyncService


class AboutDialog(QDialog):
    def __init__(self, parent=None, plugin_dir=None, tr=None):
        super().__init__(parent)
        self.setWindowTitle(tr.text("about_title"))
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(15)
        
        logo_label = QLabel()
        logo_path = str(plugin_dir / "app_logo_no_name.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaledToHeight(80, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        title = QLabel(f"<h2>{tr.text('title')}</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel(f"{tr.text('developed_by')} <b>GisGeo Dev</b>")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        links = QLabel(
            f"<a href='https://gisgeo.dev' style='text-decoration: none; color: #1976d2;'>{tr.text('website')}</a><br><br>"
            f"<a href='https://play.google.com/store/apps/details?id=com.gisgeodev.lithicaexplorer' style='text-decoration: none; color: #1976d2;'>{tr.text('download_play')}</a><br><br>"
            f"<a href='https://www.linkedin.com/in/jordan-zav/' style='text-decoration: none; color: #1976d2;'>{tr.text('linkedin')}</a>"
        )
        links.setAlignment(Qt.AlignCenter)
        links.setOpenExternalLinks(True)
        layout.addWidget(links)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setStyleSheet("QDialog { background-color: white; } QLabel { color: #333; }")


class LithicaDriveDock(QDockWidget):
    def __init__(self, iface, plugin_dir: Path):
        self.iface = iface
        self.plugin_dir = Path(plugin_dir)
        self.tr = Translator(QLocale.system().name())
        super().__init__(self.tr.text("title"), iface.mainWindow())
        cache_root = (
            Path(QgsApplication.qgisSettingsDirPath())
            / "python"
            / "plugins"
            / "lithica_drive_sync"
            / "cache"
        )
        self.credentials = QgisCredentialStore()
        self.drive = DriveClient()
        self.cache = ProjectCache(cache_root)
        self.sync = SyncService(self.drive, self.cache)
        self.projects = []
        self._build_ui()
        self._update_connection()

    def _build_ui(self):
        body = QWidget(self)
        layout = QVBoxLayout(body)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Logo
        logo_label = QLabel()
        logo_path = str(self.plugin_dir / "app_logo.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaledToHeight(60, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setContentsMargins(0, 0, 0, 10)
            layout.addWidget(logo_label)
        
        # Grupo: Cuenta / Conexión
        group_account = QGroupBox(self.tr.text("account_group"))
        layout_account = QVBoxLayout(group_account)
        layout_account.setSpacing(8)
        self.status = QLabel()
        self.status.setObjectName("statusLabel")
        layout_account.addWidget(self.status)
        
        row_connect = QHBoxLayout()
        self.connect_button = QPushButton(self.tr.text("connect"))
        self.disconnect_button = QPushButton(self.tr.text("disconnect"))
        row_connect.addWidget(self.connect_button)
        row_connect.addWidget(self.disconnect_button)
        layout_account.addLayout(row_connect)
        layout.addWidget(group_account)
        
        # Grupo: Proyectos Lithica
        group_projects = QGroupBox(self.tr.text("projects_group"))
        layout_projects = QVBoxLayout(group_projects)
        layout_projects.setSpacing(10)
        self.refresh_button = QPushButton(self.tr.text("refresh"))
        layout_projects.addWidget(self.refresh_button)
        
        self.project_combo = QComboBox()
        self.project_combo.setMinimumHeight(28)
        layout_projects.addWidget(self.project_combo)
        
        self.download_button = QPushButton(self.tr.text("download"))
        self.download_button.setObjectName("primaryButton")
        layout_projects.addWidget(self.download_button)
        layout.addWidget(group_projects)
        
        # Grupo: Avanzado
        group_advanced = QGroupBox(self.tr.text("advanced_group"))
        layout_advanced = QVBoxLayout(group_advanced)
        self.clear_button = QPushButton(self.tr.text("clear"))
        layout_advanced.addWidget(self.clear_button)
        layout.addWidget(group_advanced)
        
        layout.addStretch()
        
        # Botón de créditos
        self.about_button = QPushButton(self.tr.text("about_button"))
        self.about_button.setObjectName("aboutButton")
        self.about_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.about_button)
        
        self.setWidget(body)
        
        
        self.connect_button.clicked.connect(self.connect_drive)
        self.disconnect_button.clicked.connect(self.disconnect_drive)
        self.refresh_button.clicked.connect(self.refresh_projects)
        self.download_button.clicked.connect(self.download_selected)
        self.clear_button.clicked.connect(self.clear_cache)
        self.about_button.clicked.connect(self.show_about_dialog)

    def _set_busy(self, busy):
        for button in (
            self.connect_button,
            self.disconnect_button,
            self.refresh_button,
            self.download_button,
            self.clear_button,
        ):
            button.setEnabled(not busy)
        if busy:
            self.status.setText(self.tr.text("working"))

    def _update_connection(self):
        connected = self.credentials.load() is not None
        self.status.setText(
            self.tr.text("connected") if connected else self.tr.text("disconnected")
        )
        self.disconnect_button.setEnabled(connected)
        self.refresh_button.setEnabled(connected)
        self.download_button.setEnabled(connected and bool(self.projects))

    def _oauth_config(self):
        return load_oauth_config(self.plugin_dir / "oauth_client.json")

    def _active_token(self):
        token = self.credentials.load()
        if token is None:
            raise RuntimeError(self.tr.text("disconnected"))
        if token.needs_refresh():
            if not token.refresh_token:
                raise RuntimeError(self.tr.text("auth_expired"))
            token = refresh_access_token(self._oauth_config(), token.refresh_token)
            self.credentials.save(token)
        return token.access_token

    def _run_task(self, description, operation, completed):
        self._set_busy(True)

        def execute(task):
            return operation()

        def finished(exception, result=None):
            self._set_busy(False)
            if exception:
                self.status.setText(str(exception))
                return
            completed(result)
            self._update_connection()

        task = QgsTask.fromFunction(description, execute, on_finished=finished)
        QgsApplication.taskManager().addTask(task)

    def connect_drive(self):
        self._run_task(
            self.tr.text("task_oauth"),
            lambda: connect_and_list(
                authorize_interactive,
                self._oauth_config(),
                self.drive,
            ),
            self._connected,
        )

    def _connected(self, result):
        token, projects = result
        self.credentials.save(token)
        self._projects_loaded(projects)

    def disconnect_drive(self):
        self.credentials.clear()
        self.projects = []
        self.project_combo.clear()
        self._update_connection()

    def refresh_projects(self):
        self._run_task(
            self.tr.text("task_list"),
            lambda: self.drive.list_projects(self._active_token()),
            self._projects_loaded,
        )

    def _projects_loaded(self, projects):
        self.projects = projects
        self.project_combo.clear()
        for project in projects:
            label = f"{project.name} — {project.modified_time:%Y-%m-%d %H:%M}"
            self.project_combo.addItem(label)
        if not projects:
            self.status.setText(self.tr.text("no_projects"))

    def download_selected(self):
        index = self.project_combo.currentIndex()
        if index < 0 or index >= len(self.projects):
            return
        remote = self.projects[index]
        self._run_task(
            self.tr.text("task_download"),
            lambda: self.sync.download_project(self._active_token(), remote),
            lambda result: open_project_layers(self.iface, result),
        )

    def clear_cache(self):
        self.cache.clear_path(self.cache.root)
        self.cache.root.mkdir(parents=True, exist_ok=True)
        self.status.setText(self.tr.text("ready"))

    def show_about_dialog(self):
        dialog = AboutDialog(self, self.plugin_dir, self.tr)
        dialog.exec_()
