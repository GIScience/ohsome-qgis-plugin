import json
from datetime import date
from typing import Optional, Any

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QListWidget, QListWidgetItem
from osgeo import ogr
from osgeo.ogr import Geometry
from qgis.core import QgsProject, QgsVectorLayer, QgsMapLayerType, QgsWkbTypes, QgsFeature, QgsGeometry, \
    QgsFeatureIterator, QgsMapLayer, QgsTask

from . import ProcessManager, QGISHelper
from .client import OhsomeClient
from .utils import check_list_duplicates, combine_layer_geometries, get_layers, get_layer_by_name


class DataExtractionQGISHelper(QGISHelper):
    def __init__(self, qgs: QDialog):
        super().__init__(qgs)
        # Fetch layers to the layer selection
        self._fetch_layer_input()

    def get_layer_geometries(self) -> {}:
        feature_collection = {"type": "FeatureCollection",
                              "features": []
                              }
        layers_iterator: iter = iter(self.get_active_layers())
        while layers_iterator.__length_hint__() > 0:
            qgs_layer: QgsMapLayer = next(layers_iterator)
            wkt_geometries = combine_layer_geometries(qgs_layer)
            for wkt_geometry in wkt_geometries:
                feature = {"type": "Feature", "properties": {"id": f"{qgs_layer.name()}"},
                           "geometry": json.loads(ogr.CreateGeometryFromWkt(wkt_geometry).ExportToJson())}
                feature_collection["features"].append(feature)

        return feature_collection

    def _create_controls(self):
        self._dlg.layer_list_add.clicked.connect(self._add_layer)
        self._dlg.layer_list_remove.clicked.connect(self._remove_layer)

    def _add_layer(self, manual_name: str = None, empty: bool = False) -> bool:
        if manual_name:
            current_layer_selection: str = manual_name
        else:
            current_layer_selection: str = self._dlg.layer_input.currentText()
        if len(current_layer_selection) <= 0:
            return False
        if check_list_duplicates(self._dlg.layer_list, current_layer_selection):
            return False

        if not empty:
            layer: QgsVectorLayer = get_layer_by_name(current_layer_selection)
            if layer:
                self._dlg.layer_list.addItem(layer.name())
                self.add_to_settings("layer_list", layer.name(), append=True)
            else:
                return False
        else:
            self._dlg.layer_list.addItem(current_layer_selection)
        self._dlg.layer_input.setCurrentIndex(0)
        return True

    def _remove_layer(self):
        layers: QListWidget = self._dlg.layer_list
        selected_layers: [QListWidgetItem] = layers.selectedItems()
        if not selected_layers:
            return
        element: QListWidgetItem
        for element in selected_layers:
            self._dlg.layer_list.takeItem(self._dlg.layer_list.row(element))
            self.remove_value_from_settings('layer_list', element.text())

    def _get_active_layer_names(self) -> list:
        items = list()
        for index in range(self._dlg.layer_list.count()):
            items.append(self._dlg.layer_list.item(index).text())
        return items

    def restore_settings(self):
        # TODO add settings to be restored as needed
        self._restore_layer_list()

    def get_active_layers(self):
        valid_layer_geometries = list()
        for layer_name in self._get_active_layer_names():
            valid_layer_geometries.append(get_layer_by_name(layer_name))
        return valid_layer_geometries

    def _restore_layer_list(self):
        layer_settings = self.get_settings('layer_list')
        if layer_settings[1]:
            layer_settings_restored = ""
            for layer_name in layer_settings[0].split(","):
                layer_name = layer_name.strip(",").strip()
                restored: bool = self._add_layer(layer_name)
                if not restored:
                    # Remove old layers
                    self.remove_value_from_settings('layer_list', layer_name)

    def _fetch_layer_input(self):
        # Clear the contents of the comboBox from previous runs
        self._dlg.layer_input.clear()
        valid_layers = get_layers()
        self._dlg.layer_input.addItem("")  # Empty first line
        self._dlg.layer_input.addItems([layer.name() for layer in valid_layers])


class DataExtractionProcessManager(ProcessManager):
    def __init__(self, dlg: QDialog):
        super().__init__(dlg, DataExtractionQGISHelper(dlg))

    def accept(self):
        if self._current_widget == 0 and self.fully_initialized:
            # bboxes = "8.67066,49.41423,8.68177,49.4204"
            # bcircles = ""
            bpolys: {} = self._settings_helper.get_layer_geometries()
            types: str = self._get_osm_types()
            if types is not None and len(types) > 0:
                filter_input = f"{self._filter_input} and {types}"
            else:
                filter_input = f"{self._filter_input}"
            time = self.time
            filter2 = "amenity=place_of_worship or highway=pedestrian and type:way or type: node"
            filter3 = "amenity=place_of_worship and building=church and type:node"
            filter4 = "building=yes and type:way"
            time2 = '2016-07-08/2019-10-08/P1M'
            client = OhsomeClient()
            response = client.elements.geometry.post(bpolys=json.dumps(bpolys), time=time, filter=filter_input, showMetadata=False, properties="tags, metadata")
            # del self.client
            self._process_results(response)

    def startup(self):
        # Restore old settings
        self._settings_helper.restore_settings()
