def classFactory(iface):
    from .plugin import LithicaDriveSyncPlugin

    return LithicaDriveSyncPlugin(iface)
