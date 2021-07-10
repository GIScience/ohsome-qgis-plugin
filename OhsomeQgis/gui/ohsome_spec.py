# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OhsomeQgis
                                 A QGIS plugin
 QGIS client to query the ohsome api
                              -------------------
        begin                : 2021-05-01
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Julian Psotta
        email                : julian.psotta@heigit.org
 ***************************************************************************/

 This plugin provides access to the ohsome API (https://api.ohsome.org),
 developed and maintained by the Heidelberg Institute for Geoinformation
 Technology, HeiGIT gGmbH, Heidelberg, Germany.
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import json

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMessageBox, QDialog
from qgis._core import (
    QgsProject,
    QgsJsonExporter,
    QgsWkbTypes,
)

from OhsomeQgis.utils import exceptions
from OhsomeQgis.utils.datamanager import (
    convert_point_features_to_ohsome_bcircles,
)


class OhsomeSpec:
    """Extended functionality for all endpoints for the GUI."""

    def __init__(self, dlg: QDialog):
        """
        :param dlg: Main GUI dialog.
        :type dlg: QDialog
        """
        self.dlg: QDialog = dlg

    @property
    def _api_spec(self):
        return self.dlg.ohsome_spec_selection_combo.currentText()

    @property
    def activate_temporal_feature(self):
        if self.dlg.check_activate_temporal.isChecked():
            return True
        return False

    @property
    def _show_metadata(self) -> bool:
        # Get all parameters
        if self.dlg.check_show_metadata.isChecked():
            return True
        return False

    @property
    def _request_timeout(self) -> int:
        value = 0
        if self.dlg.timeout_input.value():
            value: int = int(self.dlg.timeout_input.value())
        return value

    @property
    def _data_extraction_clip_geometry(self) -> bool:
        if self.dlg.check_clip_geometry.isChecked():
            return True
        return False

    @property
    def _property_groups(self) -> str:
        properties = ""
        if self.dlg.property_groups_check_tags.isChecked():
            properties = "tags"
        if self.dlg.property_groups_check_metadata.isChecked():
            properties = (
                f"{properties},metadata" if properties == "tags" else "metadata"
            )
        return properties

    @property
    def _data_aggregation_format(self) -> str:
        return self.dlg.data_aggregation_format.currentText()

    @property
    def _group_by_key(self):
        return self.dlg.group_by_key_line_edit.text()

    @property
    def _group_by_values(self):
        return self.dlg.group_by_values_line_edit.text()

    @property
    def _request_bcircles_coordinates(self) -> str:
        coordinate_string = ""
        layers_list = self.dlg.ohsome_centroid_location_list
        for idx in range(layers_list.count()):
            item: str = layers_list.item(idx).text()
            param_cords, radius = item.rsplit(" | Radius: ")
            _, coordinates = param_cords.split(": ")

            if len(coordinate_string) <= 0:
                coordinate_string = f"id{idx}:{coordinates},{radius}"
            else:
                coordinate_string = (
                    f"{coordinate_string}|id{idx}:{coordinates},{radius}"
                )
        return coordinate_string

    @property
    def _request_filter(self) -> str:
        return self.dlg.filter_input.toPlainText()

    @property
    def _request_filter2(self) -> str:
        return self.dlg.filter2_input.text()

    @property
    def _request_url(self):
        # Construct request url
        if (
            self.dlg.ohsome_spec_selection_combo.currentText().lower()
            == "metadata"
        ):
            return (
                f"{self.dlg.ohsome_spec_selection_combo.currentText().lower()}"
            )
        else:
            return (
                f"{self.dlg.ohsome_spec_preference_combo.currentText()}/"
                f"{self.dlg.ohsome_spec_preference_specification.currentText()}"
            )

    @property
    def _request_date_string(self) -> str:
        date_string = self.__prepare_ohsome_time_parameter(
            self.dlg.date_start.date(),
            self.dlg.date_end.date(),
            self.dlg.interval_years.value(),
            self.dlg.interval_months.value(),
            self.dlg.interval_days.value(),
        )
        return date_string

    def is_valid(self, warn: bool = False) -> bool:
        if (
            self.dlg.ohsome_spec_selection_combo.currentText().lower()
            == "metadata"
        ):
            return True
        tab_index = self.dlg.request_types_widget.currentIndex()
        msg = ""
        if (
            tab_index == 0
            and not self.dlg.ohsome_centroid_location_list.count()
        ):
            msg = (
                f"{msg}> Missing Centroid locations, did you forget to set centroids?\n"
                "Use the green plus button to add centroids.\n"
            )
        if tab_index == 1 and not self.dlg.point_layer_list.count():
            msg = (
                f"{msg}> Missing point layers, did you forget to set one?\n"
                "Use the green plus button to add multiple layers.\n"
            )
        if tab_index == 2 and not self.dlg.layer_list.count():
            msg = (
                f"{msg}> Missing polygon layers, did you forget to set one?\n"
                "Use the green plus button to add multiple layers.\n"
            )
        if any(
            groupby in self._request_url.lower()
            for groupby in ["groupby/key", "groupby/tag"]
        ) and not len(self._group_by_key):
            msg = f"{msg}> For `groupBy/tag` and `groupBy/key` endpoints provide at least one `groupByKey` tag in the data aggregation settings.\n"
        if "ratio" in self._request_url.lower() and not len(
            self._request_filter2
        ):
            msg = f"{msg}> For `ratio` endpoints provide the `Filter 2` under the data aggregation settings.\n"
        if len(self._request_filter) <= 0:
            if warn:
                QMessageBox.critical(
                    self.dlg, "Filter error", "Set a filter query."
                )
            msg = f"{msg}> Request filter needs to be set.\n"
        if len(self._request_url) <= 3:
            msg = f"{msg}> Request url needs to be set.\n"
        if len(self._request_date_string) <= 0:
            msg = f"{msg}> Request date needs to be set.\n"
        if len(msg) and warn:
            self.dlg.debug_text.append(msg)
        if len(msg):
            return False
        return True

    def __prepare_ohsome_time_parameter(
        self,
        start_date: QDate,
        end_date: QDate,
        years: int,
        months: int,
        days: int,
    ) -> str:
        """
        Prepare a valid ohsome time string to include into the API query.

        @return Returns a valid date parameter or raises a QGIS Warning and returns an empty string.
        @rtype: str
        """
        date_start = start_date.toString("yyyy-MM-dd")
        date_end = end_date.toString("yyyy-MM-dd")
        intervals = "/P"

        if years and years > 0:
            intervals = f"{intervals}{years}Y"
        if months and months > 0:
            intervals = f"{intervals}{months}M"
        if days and days > 0:
            intervals = f"{intervals}{days}D"

        # If it's the default date the API will reject all requests that are not equal or greater than the first second.
        if date_start == "2007-10-08":
            date_start = "2007-10-08T00:00:01"
        if date_end == "2007-10-08":
            date_end = "2007-10-08T00:00:01"

        # Check if intervals is misconstructed.
        if self._api_spec.lower() == "data-aggregation" and len(intervals) >= 3:
            dates = f"{date_start}/{date_end}{intervals}"
        else:
            dates = f"{date_start},{date_end}"
        return dates

    def __get_selected_polygon_layers_geometries(self) -> []:
        layer_list = []
        polygon_layer_list = self.dlg.layer_list
        for idx in range(polygon_layer_list.count()):
            item: str = polygon_layer_list.item(idx).text()
            layers = QgsProject.instance().mapLayersByName(item)
            layers = [
                layer
                for layer in layers
                if layer.geometryType() == QgsWkbTypes.PolygonGeometry
            ]
            if len(layers) > 1:
                raise exceptions.TooManyInputsFound(
                    str("error"),
                    # error,
                    "Found too many input layers with the same name. Use unique names for your layers.",
                )
            layer_list.extend(layers)
        geojsons = [
            QgsJsonExporter(lyr)
            .exportFeatures(lyr.getFeatures())
            .replace('"properties":null', '"properties":{"":""}')
            for lyr in layer_list
        ]
        return geojsons

    def __get_selected_point_layers_geometries(self) -> {}:
        ordered_layer_radii = []
        ordered_list_of_features = []
        point_layers_list = self.dlg.point_layer_list
        for idx in range(point_layers_list.count()):
            item: str = point_layers_list.item(idx).text()
            file_name, radius = item.rsplit(" | Radius: ")
            ordered_layer_radii.append(int(radius))
            layers = QgsProject.instance().mapLayersByName(file_name)
            layers = [
                layer
                for layer in layers
                if layer.geometryType() == QgsWkbTypes.PointGeometry
            ]
            if len(layers) > 1:
                raise exceptions.TooManyInputsFound(
                    str("error"),
                    # error,
                    "Found too many input layers with the same name. Use unique names for your layers.",
                )
            features = [
                layer.getFeatures()
                for layer in layers
                if layer.geometryType() == QgsWkbTypes.PointGeometry
            ]
            ordered_list_of_features.extend(features)
        list_of_coordinates = convert_point_features_to_ohsome_bcircles(
            ordered_list_of_features, ordered_layer_radii
        )
        return list_of_coordinates

    def __prepare_request_properties(self):
        """
        Builds parameters across different api specification combinations. Not all api endpoints support the same set of parameters.

        @return: All parameter mappings according the endpoint restrictions.
        @rtype: dict
        """
        properties = {}
        if self._api_spec.lower() == "metadata":
            return properties
        elif self._api_spec.lower() == "data-extraction":
            properties[
                "clipGeometry"
            ] = self._data_extraction_clip_geometry.__str__().lower()
            if len(self._property_groups) > 0:
                properties["properties"] = self._property_groups
        elif self._api_spec.lower() == "data-aggregation":
            properties["format"] = self._data_aggregation_format
            if any(
                groupby in self._request_url.lower()
                for groupby in ["groupby/key", "groupby/tag"]
            ):
                properties["groupByKey"] = self._group_by_key
            if "groupby/tag" in self._request_url.lower() and len(
                self._group_by_values
            ):
                properties["groupByValues"] = self._group_by_values
            if "ratio" in self._request_url.lower() and len(
                self._request_filter2
            ):
                properties["filter2"] = self._request_filter2
        properties["showMetadata"] = self._show_metadata.__str__().lower()
        properties["filter"] = self._request_filter
        properties["time"] = self._request_date_string
        if self._request_timeout > 0:
            # Use API specific timout of less or equal to 0
            properties["timeout"] = self._request_timeout.__str__()

        return properties

    def get_bcircles_request_preferences(self) -> {}:
        endpoint_specific_request_properties = (
            self.__prepare_request_properties()
        )
        endpoint_specific_request_properties[
            "bcircles"
        ] = self._request_bcircles_coordinates
        return endpoint_specific_request_properties

    def get_point_layer_request_preferences(self) -> []:
        endpoint_specific_request_properties = []
        request_properties = self.__prepare_request_properties()
        list_of_bcircles = self.__get_selected_point_layers_geometries()
        for bcircles in list_of_bcircles:
            request_properties["bcircles"] = bcircles
            endpoint_specific_request_properties.append(
                request_properties.copy()
            )
        return endpoint_specific_request_properties

    def get_polygon_layer_request_preferences(self) -> []:
        endpoint_specific_request_properties = []
        request_properties = self.__prepare_request_properties()
        geojsons = self.__get_selected_polygon_layers_geometries()
        for geojson_geometry in geojsons:
            request_properties["bpolys"] = geojson_geometry
            endpoint_specific_request_properties.append(
                request_properties.copy()
            )
        return endpoint_specific_request_properties

    def get_request_url(self) -> str:
        return self._request_url

    def __dict__(self) -> dict:
        return {
            "api_spec": self._api_spec,
            "activate_temporal_feature": self.activate_temporal_feature,
            "show_metadata": self._show_metadata,
            "request_timeout": self._request_timeout,
            "data_extraction_clip_geometry": self._data_extraction_clip_geometry,
            "property_groups": self._property_groups,
            "data_aggregation_format": self._data_aggregation_format,
            "request_bcircles_coordinates": self._request_bcircles_coordinates,
            "request_filter": self._request_filter,
            "request_url": self._request_url,
            "request_date_string": self._request_date_string,
            "et_request_url": self.get_request_url,
        }
