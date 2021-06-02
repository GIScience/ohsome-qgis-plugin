# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OhsomeTools
                                 A QGIS plugin to query the ohsome API
                              -------------------
        begin                : 2020-10-01
        copyright            : (C) 2020 by Julian Psotta
        github               : https://github.com/MichaelsJP
 ***************************************************************************/

 This plugin provides access to the various APIs from Ohsome
 (https://ohsome.org).
 The original code for the modules inside the common folder can be found at:
 https://github.com/GIScience/ohsome-py

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
import re
from datetime import date, datetime

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog
from qgis._core import QgsProject, QgsVectorLayer
from qgis.core import Qgis, QgsUnitTypes
from qgis.utils import iface

from .exceptions import OhsomeException

PROFILES = ["data_extraction"]

DIMENSIONS = ["bbox", "centroid", "geometry"]

PREFERENCES = ["fastest", "shortest"]


class QGISHelper(object):
    def __init__(self, dlg: QDialog):
        self._proj = QgsProject.instance()
        self._dlg = dlg
        # Add controls for the general helper buttons
        self._create_controls()

    def get_settings(self, key):
        return self._proj.readEntry("OhsomePlugin", str(key))

    def add_to_settings(self, key, value, append: bool = False):
        key = str(key)
        value = str(value)
        original_entry = self._proj.readEntry("OhsomePlugin", key)
        if append and original_entry[1]:
            if value not in original_entry[0]:
                self._proj.writeEntry(
                    "OhsomePlugin",
                    key,
                    f"{original_entry[0].strip(',').strip()}, {value}",
                )
        else:
            self._proj.writeEntry("OhsomePlugin", str(key), value)

    def remove_key_from_settings(self, key):
        key = str(key)
        self._proj.removeEntry("OhsomePlugin", str(key))

    def remove_value_from_settings(self, key, value):
        key = str(key)
        value = str(value)
        original_entry = self._proj.readEntry("OhsomePlugin", key)
        if original_entry[1]:
            if value in original_entry[0]:
                self._proj.writeEntry(
                    "OhsomePlugin",
                    key,
                    f"{original_entry[0].replace(value, '').strip(',').strip()}",
                )

    def _create_controls(self):
        pass

    def restore_settings(self):
        pass

    def get_layer_geometries(self):
        pass


class ProcessManager(object):
    def __init__(self, dlg: QDialog, settings_helper: QGISHelper):
        self.interval_type = None
        self._dlg = dlg
        self._settings_helper = settings_helper
        self._fully_initialized = False
        try:
            # Customize default values
            today = date.today()
            self._dlg.date_start.setMaximumDate(
                QDate(today.year, today.month, today.day)
            )
            self._dlg.date_end.setMaximumDate(
                QDate(today.year, today.month, today.day)
            )
            # Set initial values
            self._current_widget = self._dlg.requestWidget.currentIndex()
            self._check_activate_temporal = (
                self._dlg.check_activate_temporal.isChecked()
            )
            self._osm_type_node = self._dlg.osm_type_node.isChecked()
            self._osm_type_way = self._dlg.osm_type_way.isChecked()
            self._osm_type_relation = self._dlg.osm_type_relation.isChecked()
            self._filter_input = self._dlg.filter_input.toPlainText()
            self._interval_days = self._dlg.interval_days.value()
            self._interval_months = self._dlg.interval_months.value()
            self._interval_years = self._dlg.interval_years.value()
            self._date_start: QDate = self._dlg.date_start.date()
            self._date_end: QDate = self._dlg.date_end.date()
            # Set trigger
            self._dlg.requestWidget.currentChanged.connect(
                self._set_current_widget
            )
            self._dlg.check_activate_temporal.clicked.connect(
                self._set_check_activate_temporal
            )
            self._dlg.osm_type_node.clicked.connect(self._set_osm_type_node)
            self._dlg.osm_type_way.clicked.connect(self._set_osm_type_way)
            self._dlg.osm_type_relation.clicked.connect(
                self._set_osm_type_relation
            )
            self._dlg.filter_input.textChanged.connect(self._set_filter_input)
            self._dlg.interval_days.valueChanged.connect(
                self._set_intervals_days
            )
            self._dlg.interval_months.valueChanged.connect(
                self._set_intervals_months
            )
            self._dlg.interval_years.valueChanged.connect(
                self._set_intervals_years
            )
            self._dlg.date_start.dateTimeChanged.connect(self._set_date_start)
            self._dlg.date_end.dateTimeChanged.connect(self._set_date_end)
            self._fully_initialized = True
        except Exception as err:
            iface.messageBar().pushMessage(
                "[Process Manager] Error", f"{err}", level=Qgis.Critical
            )
            self._fully_initialized = False

    @property
    def fully_initialized(self):
        return self._fully_initialized

    @property
    def time(self):
        date_start = ""
        date_end = ""
        dates = ""
        if self._date_start.year():
            date_start = "{}-".format(self._date_start.year())
        if self._date_start.month():
            if self._date_start.month() > 9:
                date_start = "{}{}-".format(
                    date_start, self._date_start.month()
                )
            else:
                date_start = "{}0{}-".format(
                    date_start, self._date_start.month()
                )
        if self._date_start.day():
            if self._date_start.day() > 9:
                date_start = "{}{}".format(date_start, self._date_start.day())
            else:
                date_start = "{}0{}".format(date_start, self._date_start.day())
        if self._date_end.year():
            date_end = "{}{}-".format(date_end, self._date_end.year())
        if self._date_end.month():
            if self._date_end.month() > 9:
                date_end = "{}{}-".format(date_end, self._date_end.month())
            else:
                date_end = "{}0{}-".format(date_end, self._date_end.month())
        if self._date_end.day():
            if self._date_end.day() > 9:
                date_end = "{}{}".format(date_end, self._date_end.day())
            else:
                date_end = "{}0{}".format(date_end, self._date_end.day())
        intervals = "P"
        if self._interval_years and self._interval_years > 0:
            intervals = "{}{}Y".format(intervals, self._interval_years)
        if self._interval_months and self._interval_months > 0:
            intervals = "{}{}M".format(intervals, self._interval_months)
        if self._interval_days and self._interval_days > 0:
            intervals = "{}{}D".format(intervals, self._interval_days)
        intervals = re.sub(" +", " ", intervals)
        if date_start == "2007-10-08":
            date_start = "2007-10-08T00:00:01"
        if date_end == "2007-10-08":
            date_end = "2007-10-08T00:00:01"
        if not date_start.__eq__(date_end):
            dates = f"{date_start}/{date_end}"
        else:
            dates = f"/{date_start}"
        if len(intervals) > 1:
            return f"{dates}/{intervals}"
        return dates

    def _set_current_widget(self):
        self._current_widget = self._dlg.requestWidget.currentIndex()

    def _set_check_activate_temporal(self):
        self._check_activate_temporal = (
            self._dlg.check_activate_temporal.isChecked()
        )

    def _set_osm_type_node(self):
        self._osm_type_node = self._dlg.osm_type_node.isChecked()

    def _set_osm_type_way(self):
        self._osm_type_way = self._dlg.osm_type_way.isChecked()

    def _set_osm_type_relation(self):
        self._osm_type_relation = self._dlg.osm_type_relation.isChecked()

    @property
    def _osm_types_combination(self):
        return self._dlg.osm_types_combination.currentText()

    @property
    def _osm_types_combination_2(self):
        return self._dlg.osm_types_combination_2.currentText()

    def _set_filter_input(self):
        self._filter_input = self._dlg.filter_input.toPlainText()

    def _set_date_start(self):
        self._date_start = self._dlg.date_start.date()

    def _set_date_end(self):
        self._date_end = self._dlg.date_end.date()

    def _get_osm_types(self):
        types_string = ""
        if self._osm_type_node:
            types_string = f"type:node"
        if self._osm_type_way:
            if not self._osm_type_node:
                types_string = "type:way"
            else:
                types_string = "{} {} type:way".format(
                    types_string, self._osm_types_combination
                )
        if self._osm_type_relation:
            if not self._osm_type_node and not self._osm_type_way:
                types_string = "type:relation"
            else:
                types_string = "{} {} type:relation".format(
                    types_string, self._osm_types_combination_2
                )
        return re.sub(" +", " ", types_string)

    def _set_intervals_days(self):
        self._interval_days = self._dlg.interval_days.value()

    def _set_intervals_months(self):
        self._interval_months = self._dlg.interval_months.value()

    def _set_intervals_years(self):
        self._interval_years = self._dlg.interval_years.value()

    @property
    def interval_unit(self):
        if self._interval_days > 0:
            return QgsUnitTypes.TemporalUnit.TemporalDays
        elif self._interval_months > 0:
            return QgsUnitTypes.TemporalUnit.TemporalMonths
        elif self._interval_years > 0:
            return QgsUnitTypes.TemporalUnit.TemporalYears
        else:
            return QgsUnitTypes.TemporalUnit.TemporalDays

    @property
    def interval_value(self):
        if self._interval_days > 0:
            return self._interval_days
        elif self._interval_months > 0:
            return self._interval_months
        elif self._interval_years > 0:
            return self._interval_years
        else:
            return 1
        pass

    def _process_results(self, result):
        from ohsome import OhsomeResponse

        result: OhsomeResponse
        if result.status_code == 200:
            from common.utils import convert_mixed_collection

            converted_results = convert_mixed_collection(result.data)
            for feature_type in converted_results:
                try:
                    vlayer: QgsVectorLayer = QgsVectorLayer(
                        json.dumps(converted_results[feature_type]),
                        f"{feature_type}_OhsomeResult_{datetime.now()}",
                        "ogr",
                    )
                    if not vlayer.isValid():
                        iface.messageBar().pushMessage(
                            "[Utils] Error",
                            "Response could'nt be parsed.",
                            level=Qgis.Warning,
                        )
                        raise
                    from common.utils import sort_and_combine_vector_layer

                    sorted_qgs_vector_layer: list = (
                        sort_and_combine_vector_layer(
                            vlayer,
                            activate_temporal=self._check_activate_temporal,
                        )
                    )
                    # vlayer = postprocess_vlayer(vlayer ,self._check_activate_temporal)
                    from common.utils import load_layers_to_canvas

                    load_layers_to_canvas(sorted_qgs_vector_layer)
                except Exception as err:
                    raise OhsomeException(
                        message="[ProcessManager] Error while parsing the results.",
                        params=result.params,
                        url=result.url,
                        error=err,
                    )
        pass

    def accept(self):
        # Add the accept button action here
        pass

    def startup(self):
        # Add the process startup logic here
        pass
