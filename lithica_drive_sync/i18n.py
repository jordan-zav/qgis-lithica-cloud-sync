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
    },
}


class Translator:
    def __init__(self, locale: str):
        self.locale = "es" if str(locale).lower().startswith("es") else "en"

    def text(self, key: str) -> str:
        return TEXT[self.locale].get(key, TEXT["en"].get(key, key))
