TEXT = {
    "en": {
        "title": "Lithica Cloud Sync",
        "connect": "Connect",
        "disconnect": "Disconnect",
        "refresh": "Refresh list",
        "download": "Download and open",
        "clear": "Clear cache",
        "connected": "Connected to Google Drive",
        "disconnected": "Not connected",
        "working": "Working...",
        "no_projects": "No Lithica projects are accessible",
        "ready": "Ready",
        "projects_group": "Projects",
        "advanced_group": "Advanced",
        "about_button": "About / Credits",
        "about_title": "About Lithica Cloud Sync",
        "developed_by": "Developed by",
        "website": "Official Website (gisgeo.dev)",
        "download_play": "Download Lithica Explorer on Google Play",
        "linkedin": "LinkedIn Profile (Jordan Zavaleta)",
        "account_group": "Google Drive",
        "auth_expired": "Google authorization expired; reconnect",
        "task_oauth": "Lithica OAuth",
        "task_list": "Lithica Drive list",
        "task_download": "Lithica project download",
    },
    "es": {
        "title": "Lithica Cloud Sync",
        "connect": "Conectar",
        "disconnect": "Desconectar",
        "refresh": "Actualizar lista",
        "download": "Descargar y abrir",
        "clear": "Limpiar caché",
        "connected": "Conectado a Google Drive",
        "disconnected": "Sin conexión",
        "working": "Procesando...",
        "no_projects": "No hay proyectos Lithica accesibles",
        "ready": "Listo",
        "projects_group": "Proyectos",
        "advanced_group": "Avanzado",
        "about_button": "Acerca de / Créditos",
        "about_title": "Acerca de Lithica Cloud Sync",
        "developed_by": "Desarrollado por",
        "website": "Página Web oficial (gisgeo.dev)",
        "download_play": "Descarga Lithica Explorer en Google Play",
        "linkedin": "Perfil en LinkedIn (Jordan Zavaleta)",
        "account_group": "Google Drive",
        "auth_expired": "Autorización de Google expirada; vuelve a conectar",
        "task_oauth": "Lithica OAuth",
        "task_list": "Listar proyectos Lithica",
        "task_download": "Descargar proyecto Lithica",
    },
}


class Translator:
    def __init__(self, locale: str):
        self.locale = "es" if str(locale).lower().startswith("es") else "en"

    def text(self, key: str) -> str:
        return TEXT[self.locale].get(key, TEXT["en"].get(key, key))
