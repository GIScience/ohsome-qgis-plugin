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
        email                : julianpsotta@gmail.com
 ***************************************************************************/

 This plugin provides access to the API from Ohsome
 (https://ohsome.org), developed and
 maintained by GIScience team at University of Heidelberg, Germany.
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import json
import webbrowser

from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QApplication,
    QMenu,
    QMessageBox,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtGui import QIcon, QTextDocument
from PyQt5.QtCore import QSizeF, QPointF

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsTextAnnotation,
    QgsMapLayerProxyModel,
)
from qgis.gui import QgsMapCanvasAnnotationItem
import processing

from . import resources_rc

from OhsomeQgis import (
    RESOURCE_PREFIX,
    PLUGIN_NAME,
    DEFAULT_COLOR,
    __version__,
    __email__,
    __web__,
    __help__,
)
from OhsomeQgis.utils import (
    exceptions,
    maptools,
    logger,
    configmanager,
    convert,
    transform,
)
from OhsomeQgis.common import (
    client,
    directions_core,
    API_ENDPOINTS,
    PREFERENCES,
    EXTRACTION_PREFERENCES,
    AGGREGATION_PREFERENCES,
)
from OhsomeQgis.gui import ohsome_gui

from .OhsomeQgisDialogUI import Ui_OhsomeQgisDialogBase
from .OhsomeQgisDialogConfig import OhsomeQgisDialogConfigMain
from ..utils.datamanager import check_list_duplicates


def on_config_click(parent):
    """Pop up provider config window. Outside of classes because it's accessed by multiple dialogs.

    :param parent: Sets parent window for modality.
    :type parent: QDialog
    """
    config_dlg = OhsomeQgisDialogConfigMain(parent=parent)
    config_dlg.exec_()


def on_help_click():
    """Open help URL from button/menu entry."""
    webbrowser.open(__help__)


def on_about_click(parent):
    """Slot for click event of About button/menu entry."""

    info = (
        '<b>ORS Tools</b> provides access to <a href="https://openrouteservice.org" style="color: {0}">openrouteservice</a> routing functionalities.<br><br>'
        "<center>"
        '<a href="https://heigit.org/de/willkommen"><img src=":/plugins/OhsomeQgis/img/logo_heigit_300.png"/></a> <br><br>'
        "</center>"
        "Author: HeiGIT gGmbH<br>"
        'Email: <a href="mailto:Openrouteservice <{1}>">{1}</a><br>'
        'Web: <a href="{2}">{2}</a><br>'
        'Repo: <a href="https://github.com/GIScience/orstools-qgis-plugin">github.com/GIScience/orstools-qgis-plugin</a><br>'
        "Version: {3}".format(DEFAULT_COLOR, __email__, __web__, __version__)
    )

    QMessageBox.information(parent, "About {}".format(PLUGIN_NAME), info)


class OhsomeQgisDialogMain:
    """Defines all mandatory QGIS things about dialog."""

    def __init__(self, iface):
        """

        :param iface: the current QGIS interface
        :type iface: Qgis.Interface
        """
        self.iface = iface
        self.project = QgsProject.instance()

        self.first_start = True
        # Dialogs
        self.dlg = None
        self.menu = None
        self.actions = None

    def initGui(self):
        """Called when plugin is activated (on QGIS startup or when activated in Plugin Manager)."""

        def create_icon(f):
            """
            internal function to create action icons

            :param f: file name of icon.
            :type f: str

            :returns: icon object to insert to QAction
            :rtype: QIcon
            """
            return QIcon(RESOURCE_PREFIX + f)

        icon_plugin = create_icon("icon_ohsome.png")

        self.actions = [
            QAction(
                icon_plugin,
                PLUGIN_NAME,  # tr text
                self.iface.mainWindow(),  # parent
            ),
            # Config dialog
            QAction(
                create_icon("icon_settings.png"),
                "Provider Settings",
                self.iface.mainWindow(),
            ),
            # About dialog
            QAction(
                create_icon("icon_about.png"), "About", self.iface.mainWindow()
            ),
            # Help page
            QAction(
                create_icon("icon_help.png"), "Help", self.iface.mainWindow()
            ),
        ]

        # Create menu
        self.menu = QMenu(PLUGIN_NAME)
        self.menu.setIcon(icon_plugin)
        self.menu.addActions(self.actions)

        # Add menu to Web menu and make sure it exsists and add icon to toolbar
        self.iface.addPluginToWebMenu("_tmp", self.actions[2])
        self.iface.webMenu().addMenu(self.menu)
        self.iface.removePluginWebMenu("_tmp", self.actions[2])
        self.iface.addWebToolBarIcon(self.actions[0])

        # Connect slots to events
        self.actions[0].triggered.connect(self._init_gui_control)
        self.actions[1].triggered.connect(
            lambda: on_config_click(parent=self.iface.mainWindow())
        )
        self.actions[2].triggered.connect(
            lambda: on_about_click(parent=self.iface.mainWindow())
        )
        self.actions[3].triggered.connect(on_help_click)

    def unload(self):
        """Called when QGIS closes or plugin is deactivated in Plugin Manager"""

        self.iface.webMenu().removeAction(self.menu.menuAction())
        self.iface.removeWebToolBarIcon(self.actions[0])
        QApplication.restoreOverrideCursor()
        del self.dlg

    def _init_gui_control(self):
        """Slot for main plugin button. Initializes the GUI and shows it."""

        # Only populate GUI if it's the first start of the plugin within the QGIS session
        # If not checked, GUI would be rebuilt every time!
        if self.first_start:
            self.first_start = False
            self.dlg = OhsomeQgisDialog(
                self.iface, self.iface.mainWindow()
            )  # setting parent enables modal view
            # Make sure plugin window stays open when OK is clicked by reconnecting the accepted() signal
            self.dlg.global_buttons.accepted.disconnect(self.dlg.accept)
            self.dlg.global_buttons.accepted.connect(self.run_gui_control)
            self.dlg.layer_input.setFilters(QgsMapLayerProxyModel.PolygonLayer)

        # Populate provider box on window startup, since can be changed from multiple menus/buttons
        providers = configmanager.read_config()["providers"]
        self.dlg.provider_combo.clear()
        for provider in providers:
            self.dlg.provider_combo.addItem(provider["name"], provider)

        self.dlg.show()

    def run_gui_control(self):
        """Slot function for OK button of main dialog."""

        layer_out = QgsVectorLayer(
            "LineString?crs=EPSG:4326", "Time_OHSOME    ", "memory"
        )
        layer_out.dataProvider().addAttributes(directions_core.get_fields())
        layer_out.updateFields()

        # Associate annotations with map layer, so they get deleted when layer is deleted
        for annotation in self.dlg.annotations:
            # Has the potential to be pretty cool: instead of deleting, associate with mapLayer, you can change order after optimization
            # Then in theory, when the layer is remove, the annotation is removed as well
            # Doesng't work though, the annotations are still there when project is re-opened
            # annotation.setMapLayer(layer_out)
            self.project.annotationManager().removeAnnotation(annotation)
        self.dlg.annotations = []

        provider_id = self.dlg.provider_combo.currentIndex()
        provider = configmanager.read_config()["providers"][provider_id]

        # if there are no centroids or layers, throw an error message
        tab_index = self.dlg.request_types_widget.currentIndex()
        if (
            tab_index == 0
            and not self.dlg.ohsome_centroid_location_list.count()
        ):
            QMessageBox.critical(
                self.dlg,
                "Missing Centroid locations",
                """
                Did you forget to set centroids?<br><br>

                Use the 'Add Centroid' button to add centroids.
                """,
            )
            return
        elif tab_index == 1 and not self.dlg.layer_list.count():
            QMessageBox.critical(
                self.dlg,
                "Missing layers",
                """
                Did you forget to set one?<br><br>

                Use the 'Add Layers' button to add multiple layers.
                """,
            )
            return
        elif tab_index != 0 and tab_index != 1:
            return
            # if no API key is present, when ORS is selected, throw an error message
        if provider["base_url"].startswith("https://api.ohsome.org/"):
            QMessageBox.information(
                self.dlg,
                "Using the public API. Rate limits may apply.",
            )

        clnt = client.Client(provider)
        clnt_msg = ""

        specification = ohsome_gui.Spec(self.dlg)
        params = None
        try:
            params = specification.get_parameters()
            if self.dlg.optimization_group.isChecked():
                if (
                    len(params["jobs"]) <= 1
                ):  # Start/end locations don't count as job
                    QMessageBox.critical(
                        self.dlg,
                        "Wrong number of waypoints",
                        """At least 3 or 4 waypoints are needed to perform routing optimization.

Remember, the first and last location are not part of the optimization.
                        """,
                    )
                    return
                response = clnt.request("/optimization", {}, post_json=params)
                feat = directions_core.get_output_features_optimization(
                    response, params["vehicles"][0]["profile"]
                )
            else:
                params["coordinates"] = specification.get_request_line_feature()
                profile = self.dlg.ohsome_spec_selection_combo.currentText()
                # abort on empty avoid polygons layer
                if (
                    "options" in params
                    and "avoid_polygons" in params["options"]
                    and params["options"]["avoid_polygons"] == {}
                ):
                    QMessageBox.warning(
                        self.dlg,
                        "Empty layer",
                        """
The specified avoid polygon(s) layer does not contain any features.
Please add polygons to the layer or uncheck avoid polygons.
                        """,
                    )
                    msg = "The request has been aborted!"
                    logger.log(msg, 0)
                    self.dlg.debug_text.setText(msg)
                    return
                response = clnt.request(
                    "/v2/directions/" + profile + "/geojson",
                    {},
                    post_json=params,
                )
                feat = directions_core.get_output_feature_directions(
                    response,
                    profile,
                    params["preference"],
                    specification.options,
                )

            layer_out.dataProvider().addFeature(feat)

            layer_out.updateExtents()
            self.project.addMapLayer(layer_out)

        except exceptions.Timeout:
            msg = "The connection has timed out!"
            logger.log(msg, 2)
            self.dlg.debug_text.setText(msg)
            return

        except (
            exceptions.ApiError,
            exceptions.InvalidKey,
            exceptions.GenericServerError,
        ) as e:
            msg = (e.__class__.__name__, str(e))

            logger.log("{}: {}".format(*msg), 2)
            clnt_msg += "<b>{}</b>: ({})<br>".format(*msg)
            raise

        except Exception as e:
            msg = [e.__class__.__name__, str(e)]
            logger.log("{}: {}".format(*msg), 2)
            clnt_msg += "<b>{}</b>: {}<br>".format(*msg)
            raise

        finally:
            # Set URL in debug window
            if params:
                clnt_msg += (
                    '<a href="{0}">{0}</a><br>Parameters:<br>{1}'.format(
                        clnt.url, json.dumps(params, indent=2)
                    )
                )
            self.dlg.debug_text.setHtml(clnt_msg)


class OhsomeQgisDialog(QDialog, Ui_OhsomeQgisDialogBase):
    """Define the custom behaviour of Dialog"""

    def __init__(self, iface, parent=None):
        """
        :param iface: QGIS interface
        :type iface: QgisInterface

        :param parent: parent window for modality.
        :type parent: QDialog/QApplication
        """

        runtime_config = configmanager.read_config()["runtime"]
        if runtime_config["debug"]:
            import pydevd_pycharm

            pydevd_pycharm.settrace(
                "127.0.0.1",
                port=53101,
                stdoutToServer=True,
                stderrToServer=True,
            )
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._iface = iface
        self.project = QgsProject.instance()  # invoke a QgsProject instance
        self.map_crs = self._iface.mapCanvas().mapSettings().destinationCrs()

        # Set things around the custom map tool
        self.point_tool = None
        self.last_maptool = self._iface.mapCanvas().mapTool()
        self.annotations = []

        # Populate combo boxes
        self.ohsome_spec_selection_combo.clear()
        self.ohsome_spec_selection_combo.addItems(API_ENDPOINTS)
        self._set_preferences()

        # Change OK and Cancel button names
        self.global_buttons.button(QDialogButtonBox.Ok).setText("Apply")
        self.global_buttons.button(QDialogButtonBox.Cancel).setText("Close")

        #### Set up signals/slots ####

        # Update preferences on api selection
        self.ohsome_spec_selection_combo.currentIndexChanged.connect(
            self._set_preferences
        )

        # Config/Help dialogs
        self.provider_config.clicked.connect(lambda: on_config_click(self))
        self.help_button.clicked.connect(on_help_click)
        self.about_button.clicked.connect(
            lambda: on_about_click(parent=self._iface.mainWindow())
        )
        self.provider_refresh.clicked.connect(self._on_prov_refresh_click)

        # Layer tab
        self.layer_list_add.clicked.connect(self._add_layer)
        self.layer_list_remove.clicked.connect(self._remove_layer)
        # Routing tab
        self.centroid_list_point_add.clicked.connect(self._on_linetool_init)
        self.centroid_list_point_clear.clicked.connect(
            self._on_clear_listwidget_click
        )

        # Batch
        self.batch_routing_points.clicked.connect(
            lambda: processing.execAlgorithmDialog(
                "{}:directions_from_points_2_layers".format(PLUGIN_NAME)
            )
        )
        self.batch_routing_point.clicked.connect(
            lambda: processing.execAlgorithmDialog(
                "{}:directions_from_points_1_layer".format(PLUGIN_NAME)
            )
        )
        self.batch_routing_line.clicked.connect(
            lambda: processing.execAlgorithmDialog(
                "{}:directions_from_polylines_layer".format(PLUGIN_NAME)
            )
        )
        self.batch_iso_point.clicked.connect(
            lambda: processing.execAlgorithmDialog(
                "{}:isochrones_from_point".format(PLUGIN_NAME)
            )
        )
        self.batch_iso_layer.clicked.connect(
            lambda: processing.execAlgorithmDialog(
                "{}:isochrones_from_layer".format(PLUGIN_NAME)
            )
        )
        self.batch_matrix.clicked.connect(
            lambda: processing.execAlgorithmDialog(
                "{}:matrix_from_layers".format(PLUGIN_NAME)
            )
        )

    # On Spec selection
    def _set_preferences(self):
        if self.ohsome_spec_selection_combo.currentText() == API_ENDPOINTS[0]:
            self.ohsome_spec_preference_combo.clear()
            self.ohsome_spec_preference_combo.addItems(EXTRACTION_PREFERENCES)
        else:
            self.ohsome_spec_preference_combo.clear()
            self.ohsome_spec_preference_combo.addItems(AGGREGATION_PREFERENCES)

    def _on_prov_refresh_click(self):
        """Populates provider dropdown with fresh list from config.yml"""

        providers = configmanager.read_config()["providers"]
        self.provider_combo.clear()
        for provider in providers:
            self.provider_combo.addItem(provider["name"], provider)

    def _on_clear_listwidget_click(self):
        """Clears the contents of the QgsListWidget and the annotations."""
        items = self.ohsome_centroid_location_list.selectedItems()
        if items:
            # if items are selected, only clear those
            for item in items:
                row = self.ohsome_centroid_location_list.row(item)
                self.ohsome_centroid_location_list.takeItem(row)
                if self.annotations:
                    self.project.annotationManager().removeAnnotation(
                        self.annotations.pop(row)
                    )
        else:
            # else clear all items and annotations
            self.ohsome_centroid_location_list.clear()
            self._clear_annotations()

    def _linetool_annotate_point(self, point, idx):
        annotation = QgsTextAnnotation()

        c = QTextDocument()
        html = "<strong>" + str(idx) + "</strong>"
        c.setHtml(html)

        annotation.setDocument(c)

        annotation.setFrameSize(QSizeF(27, 20))
        annotation.setFrameOffsetFromReferencePoint(QPointF(5, 5))
        annotation.setMapPosition(point)
        annotation.setMapPositionCrs(self.map_crs)

        return QgsMapCanvasAnnotationItem(
            annotation, self._iface.mapCanvas()
        ).annotation()

    def _clear_annotations(self):
        """Clears annotations"""
        for annotation in self.annotations:
            if annotation in self.project.annotationManager().annotations():
                self.project.annotationManager().removeAnnotation(annotation)
        self.annotations = []

    def _on_linetool_init(self):
        """Inits line maptool and add items to point list box."""
        self.ohsome_centroid_location_list.clear()
        # Remove all annotations which were added (if any)
        self._clear_annotations()

        self.point_tool = maptools.PointTool(self._iface.mapCanvas())
        self._iface.mapCanvas().setMapTool(self.point_tool)
        self.point_tool.pointDrawn.connect(
            lambda point, idx: self._on_linetool_map_click(
                point, idx, self.centroid_radius_input.value()
            )
        )
        self.point_tool.doubleClicked.connect(self._on_linetool_map_deactivate)

    def _on_linetool_map_click(self, point, idx, radius):
        """Adds an item to QgsListWidget and annotates the point in the map canvas"""

        transformer = transform.transformToWGS(self.map_crs)
        point_wgs = transformer.transform(point)
        self.ohsome_centroid_location_list.addItem(
            f"Point {idx}: {point_wgs.x():.6f}, {point_wgs.y():.6f} | Radius: {radius}"
        )

        annotation = self._linetool_annotate_point(point, idx)
        self.annotations.append(annotation)
        self.project.annotationManager().addAnnotation(annotation)

    def _on_linetool_map_deactivate(self):
        """
        Populate line list widget with coordinates, end line drawing and show dialog again.

        :param points_num: number of points drawn so far.
        :type points_num: int
        """

        self.point_tool.pointDrawn.disconnect()
        self.point_tool.doubleClicked.disconnect()
        QApplication.restoreOverrideCursor()
        self._iface.mapCanvas().setMapTool(self.last_maptool)
        self.show()

    def _add_layer(self) -> bool:
        layer = self.layer_input.currentLayer()
        if layer and not check_list_duplicates(self.layer_list, layer.name()):
            self.layer_list.addItem(layer.name())
            self.layer_input.setCurrentIndex(0)
            # self.add_to_settings("layer_list", layer.name(), append=True)
        else:
            return False
        return True

    def _remove_layer(self):
        layers: QListWidget = self.layer_list
        selected_layers: [QListWidgetItem] = layers.selectedItems()
        if not selected_layers:
            return
        element: QListWidgetItem
        for element in selected_layers:
            self.layer_list.takeItem(self.layer_list.row(element))
            # self.remove_value_from_settings("layer_list", element.text())
