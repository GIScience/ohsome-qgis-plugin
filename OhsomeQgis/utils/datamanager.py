from PyQt5.QtWidgets import QListWidget


def check_list_duplicates(list_widget: QListWidget, item_name: str) -> bool:
    for i in range(list_widget.count()):
        if list_widget.item(i).text().__eq__(item_name):
            return True
    return False


from OhsomeQgis.utils import transform


def _get_layer_polygons(layer):
    """
    Extract polygon geometries from the selected polygon layer.

    :param layer: The polygon layer
    :type layer: QgsMapLayer
    :returns: GeoJSON object
    :rtype: dict
    """
    polygons = None
    transformer = transform.transformToWGS(layer.sourceCrs())
    features = layer.getFeatures()

    # iterate over all other features
    for feature in features:
        if feature.hasGeometry():
            geom = feature.geometry()
            geom.transform(transformer)
            if polygons is None:
                polygons = geom
            else:
                polygons = polygons.combine(geom)

    if not polygons:
        return json.loads("{}")
    else:
        return json.loads(polygons.asJson())
