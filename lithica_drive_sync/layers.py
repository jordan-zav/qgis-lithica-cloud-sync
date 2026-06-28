from pathlib import Path


def open_project_layers(iface, extracted):
    from qgis.core import QgsDataProvider, QgsProject, QgsVectorLayer

    project = QgsProject.instance()
    root = project.layerTreeRoot()
    parent = root.findGroup("Lithica Explorer") or root.addGroup("Lithica Explorer")
    old = parent.findGroup(extracted.project_name)
    visible = old.itemVisibilityChecked() if old else True

    path_str = str(Path(extracted.geopackage))
    temp_layer = QgsVectorLayer(path_str, "temp", "ogr")
    if not temp_layer.isValid():
        raise RuntimeError("observations.gpkg is not a valid QGIS vector layer")

    sub_layers = temp_layer.dataProvider().subLayers()
    layers_to_add = []

    if sub_layers:
        for sub in sub_layers:
            parts = sub.split(QgsDataProvider.SUBLAYER_SEPARATOR)
            if len(parts) >= 2:
                name = parts[1]
                uri = f"{path_str}|layername={name}"
                vlayer = QgsVectorLayer(uri, name, "ogr")
                if vlayer.isValid():
                    layers_to_add.append(vlayer)
    else:
        # Fallback if no sublayers are returned
        layers_to_add.append(QgsVectorLayer(path_str, extracted.project_name, "ogr"))

    if not layers_to_add:
        raise RuntimeError("No valid layers found in observations.gpkg")

    if old:
        parent.removeChildNode(old)

    group = parent.addGroup(extracted.project_name)

    for layer in layers_to_add:
        layer.setCustomProperty("lithica/projectId", extracted.project_id)
        project.addMapLayer(layer, False)
        group.addLayer(layer)

    group.setItemVisibilityChecked(visible)
    if iface and layers_to_add:
        iface.setActiveLayer(layers_to_add[0])
    return layers_to_add
