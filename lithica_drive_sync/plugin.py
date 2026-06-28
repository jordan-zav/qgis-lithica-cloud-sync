from pathlib import Path

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsSettings

from .dock import LithicaDriveDock


class LithicaDriveSyncPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = Path(__file__).resolve().parent
        self.action = None
        self.dock = None

    def initGui(self):
        self.action = QAction(
            QIcon(str(self.plugin_dir / "app_logo_no_name.png")),
            "Lithica Cloud Sync",
            self.iface.mainWindow(),
        )
        self.action.triggered.connect(self.show_dock)
        self.iface.addPluginToVectorMenu("Lithica Cloud Sync", self.action)
        self.iface.addToolBarIcon(self.action)

        # Show the dock widget automatically only on first installation/run
        settings = QgsSettings()
        if not settings.value("LithicaDriveSync/has_run_before", False, type=bool):
            self.show_dock()
            settings.setValue("LithicaDriveSync/has_run_before", True)

    def show_dock(self):
        if self.dock is None:
            self.dock = LithicaDriveDock(self.iface, self.plugin_dir)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.show()
        self.dock.raise_()

    def unload(self):
        if self.action is not None:
            self.iface.removePluginVectorMenu("Lithica Cloud Sync", self.action)
            self.iface.removeToolBarIcon(self.action)
        if self.dock is not None:
            self.iface.removeDockWidget(self.dock)
            self.dock.deleteLater()
            self.dock = None
