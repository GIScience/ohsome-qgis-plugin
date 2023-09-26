# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ohsomeTools
                                 A QGIS plugin
 QGIS client to query the ohsome API
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
import random
import string
import webbrowser

from PyQt5 import QtCore
from PyQt5.QtCore import QSizeF, QPointF
from PyQt5.QtGui import QIcon, QTextDocument
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
from qgis._core import (
    Qgis,
    QgsTask,
    QgsApplication,
)
from qgis.core import (
    QgsProject,
    QgsTextAnnotation,
    QgsMapLayerProxyModel,
)
from qgis.gui import QgsMapCanvasAnnotationItem

from ohsomeTools import (
    RESOURCE_PREFIX,
    PLUGIN_NAME,
    DEFAULT_COLOR,
    __version__,
    __email__,
    __web__,
    __help__,
    __filter_help__,
)
from ohsomeTools.utils import (
    exceptions,
    maptools,
    logger,
    configmanager,
    transform,
)

from . import resources_rc


from ohsomeTools.common import (
    client,
    request_core,
    API_ENDPOINTS,
    EXTRACTION_SPECS,
    AGGREGATION_SPECS,
    DATA_AGGREGATION_FORMAT,
)
from ohsomeTools.gui import ohsome_spec

from .OhsomeToolsDialogUI import Ui_OhsomeToolsDialogBase
from .OhsomeToolsDialogConfig import OhsomeToolsDialogConfigMain
from ..common.request_core import ExtractionTaskFunction
from ..utils.datamanager import check_list_duplicates


def on_config_click(parent):
    """Pop up provider config window. Outside of classes because it's accessed by multiple dialogs.

    :param parent: Sets parent window for modality.
    :type parent: QDialog
    """
    config_dlg = OhsomeToolsDialogConfigMain(parent=parent)
    config_dlg.exec_()


def on_help_click():
    """Open help URL from button/menu entry."""
    webbrowser.open(__help__)


def on_filter_help_click():
    """Open help URL from button/menu entry."""
    webbrowser.open(__filter_help__)


def on_about_click(parent):
    """Slot for click event of About button/menu entry."""

    info = (
        '<b>ohsomeTools</b> provides access to <a href="https://api.ohsome.org" style="color: {0}">ohsome API</a> query functionalities.<br><br>'
        "<center>"
        '<a href="https://heigit.org"><img src=":/plugins/ohsomeTools/img/logo_heigit_300.png"/></a> <br><br>'
        "</center>"
        "Author: HeiGIT gGmbH<br>"
        'Email: <a href="mailto:ohsome <{1}>">{1}</a><br>'
        'Web: <a href="{2}">{2}</a><br>'
        'Repo: <a href="https://github.com/GIScience/ohsome-qgis-plugin">github.com/GIScience/ohsome-qgis-plugin</a><br>'
        "Version: {3}".format(DEFAULT_COLOR, __email__, __web__, __version__)
    )

    QMessageBox.information(parent, "About {}".format(PLUGIN_NAME), info)


class OhsomeToolsDialogMain:
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
            self.dlg = OhsomeToolsDialog(
                self.iface, self.iface.mainWindow()
            )  # setting parent enables modal view
            # Make sure plugin window stays open when OK is clicked by reconnecting the accepted() signal
            self.dlg.global_buttons.accepted.disconnect(self.dlg.accept)
            self.dlg.global_buttons.accepted.connect(self.run_gui_control)
            self.dlg.layer_input.setFilters(QgsMapLayerProxyModel.PolygonLayer)
            self.dlg.point_layer_input.setFilters(
                QgsMapLayerProxyModel.PointLayer
            )
            # TODO RAD
            runtime_config = configmanager.read_config()["runtime"]
            if runtime_config["debug"]:
                self.dlg.ohsome_centroid_location_list.addItem(
                    f"Point 0: 8.67, 49.39 | Radius: 1000"
                )

            self.dlg.filter_input.setPlainText(
                "building=* or (type:way and highway=residential)"
            )

        # Populate provider box on window startup, since can be changed from multiple menus/buttons
        providers = configmanager.read_config()["providers"]
        try:
            self.dlg.provider_combo.currentIndexChanged.disconnect(
                self.dlg.set_temporal_extent
            )
            self.dlg.provider_combo.clear()
            for provider in providers:
                self.dlg.provider_combo.addItem(provider["name"], provider)
            self.dlg.provider_combo.currentIndexChanged.connect(
                self.dlg.set_temporal_extent
            )
        except AttributeError as err:
            logger.log("{}: {}".format(err.__class__.__name__, str(err)), 1)

        self.dlg.set_temporal_extent()
        self.dlg.filter_input.clearFocus()
        self.dlg.show()

    def run_gui_control(self):
        """Slot function for OK button of main dialog."""

        # Associate annotations with map layer, so they get deleted when layer is deleted
        for annotation in self.dlg.annotations:
            # Has the potential to be pretty cool: instead of deleting, associate with mapLayer, you can change order after optimization
            # Then in theory, when the layer is remove, the annotation is removed as well
            # Doesn't work though, the annotations are still there when project is re-opened
            # annotation.setMapLayer(layer_out)
            self.project.annotationManager().removeAnnotation(annotation)
        self.dlg.annotations = []

        # Clean the debug text
        self.dlg.debug_text.setText(f">>> New ohsome API query started <<<")
        try:
            provider_id = self.dlg.provider_combo.currentIndex()
            provider = configmanager.read_config()["providers"][provider_id]
        except IndexError:
            msg = "Request aborted. No provider available. Please check your provider list.\n"
            logger.log(msg, 1)
            self.dlg.debug_text.setText(msg)
            self.iface.messageBar().pushMessage(
                "Warning",
                msg,
                level=Qgis.Warning,
                duration=5,
            )
            return

        if provider["base_url"].startswith("https://api.ohsome.org"):
            msg = "Using the public API. Rate limits may apply."
            logger.log(msg, 0)
            self.dlg.debug_text.append("> " + msg)

        clnt = client.Client(provider)

        metadata_check = clnt.check_api_metadata(self.iface)

        # get preferences from dialog
        preferences = ohsome_spec.OhsomeSpec(self.dlg)

        try:
            letters = string.ascii_lowercase
            task_name = "".join(random.choice(letters) for i in range(10))
            if not metadata_check or not preferences.is_valid(False):
                msg = "The request has been aborted!"
                logger.log(msg, 0)
                self.dlg.debug_text.append("> " + msg)
                return

            # if there are no centroids or layers, throw an error message
            tab_index = self.dlg.request_types_widget.currentIndex()
            if tab_index == 0:
                self.dlg.global_buttons.button(QDialogButtonBox.Ok).setDisabled(
                    True
                )
                globals()[task_name] = ExtractionTaskFunction(
                    iface=self.iface,
                    dlg=self.dlg,
                    description=f"OHSOME task",
                    provider=provider,
                    request_url=preferences.get_request_url(),
                    preferences=preferences.get_bcircles_request_preferences(),
                    activate_temporal=preferences.activate_temporal_feature,
                )
                QgsApplication.taskManager().addTask(globals()[task_name])
            elif tab_index == 1:
                self.dlg.global_buttons.button(QDialogButtonBox.Ok).setDisabled(
                    True
                )
                layer_preferences = (
                    preferences.get_point_layer_request_preferences()
                )
                if not len(layer_preferences):
                    self.dlg.global_buttons.button(
                        QDialogButtonBox.Ok
                    ).setEnabled(True)
                    return
                last_task = None
                for point_layer_preference in layer_preferences:
                    task = ExtractionTaskFunction(
                        iface=self.iface,
                        dlg=self.dlg,
                        description=f"OHSOME task",
                        provider=provider,
                        request_url=preferences.get_request_url(),
                        preferences=point_layer_preference,
                        activate_temporal=preferences.activate_temporal_feature,
                    )
                    if last_task and last_task != globals()[task_name]:
                        # Never add the main task as a dependency!
                        globals()[task_name].addSubTask(
                            task,
                            [last_task],
                            QgsTask.ParentDependsOnSubTask,
                        )
                    elif last_task:
                        globals()[task_name].addSubTask(
                            task, [], QgsTask.ParentDependsOnSubTask
                        )
                    else:
                        globals()[task_name] = task
                    last_task = task
                self.dlg.debug_text.append(f'> cURL: {preferences.cURL(provider)}')
                QgsApplication.taskManager().addTask(globals()[task_name])
            elif tab_index == 2:
                self.dlg.global_buttons.button(QDialogButtonBox.Ok).setDisabled(
                    True
                )
                layer_preferences = (
                    preferences.get_polygon_layer_request_preferences()
                )
                last_task = None
                for point_layer_preference in layer_preferences:
                    task = ExtractionTaskFunction(
                        iface=self.iface,
                        dlg=self.dlg,
                        description=f"OHSOME task",
                        provider=provider,
                        request_url=preferences.get_request_url(),
                        preferences=point_layer_preference,
                        activate_temporal=preferences.activate_temporal_feature,
                    )
                    if last_task and last_task != globals()[task_name]:
                        # Never add the main task as a dependency!
                        globals()[task_name].addSubTask(
                            task,
                            [last_task],
                            QgsTask.ParentDependsOnSubTask,
                        )
                    elif last_task:
                        globals()[task_name].addSubTask(
                            task, [], QgsTask.ParentDependsOnSubTask
                        )
                    else:
                        globals()[task_name] = task
                    last_task = task
                self.dlg.debug_text.append(f'> cURL: {preferences.cURL(provider)}')
                QgsApplication.taskManager().addTask(globals()[task_name])

            else:
                return
        except exceptions.TooManyInputsFound as e:
            msg = [e.__class__.__name__, str(e)]
            logger.log("{}: {}".format(*msg), 2)
            self.dlg.debug_text.append(
                "Request aborted. Layer input name is not unique."
            )
            self.iface.messageBar().pushMessage(
                "Error",
                "Request aborted. Layer input name is not unique.",
                level=Qgis.Critical,
                duration=5,
            )
            self.dlg.global_buttons.button(QDialogButtonBox.Ok).setEnabled(True)
        except Exception as e:
            msg = [e.__class__.__name__, str(e)]
            logger.log("{}: {}".format(*msg), 2)
            self.dlg.debug_text.append(msg)
            self.iface.messageBar().pushMessage(
                "Error",
                "Request aborted. Check the tool log.",
                level=Qgis.Critical,
                duration=5,
            )
            self.dlg.global_buttons.button(QDialogButtonBox.Ok).setEnabled(True)
        finally:
            if not metadata_check:
                return
            elif not preferences.is_valid(True):
                self.iface.messageBar().pushMessage(
                    "Warning",
                    "Preferences are not valid. Check the plugin log.",
                    level=Qgis.Critical,
                    duration=7,
                )
                return


class OhsomeToolsDialog(QDialog, Ui_OhsomeToolsDialogBase):
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
                port=8080,
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

        self._set_preferences()
        self._set_data_aggregation_format()

        # Change OK and Cancel button names
        # self.global_buttons.button(QDialogButtonBox.Ok).setText("Apply")
        self.global_buttons.button(QDialogButtonBox.Ok).setEnabled(True)
        # self.global_buttons.button(QDialogButtonBox.Cancel).setText("Close")

        #### Set up signals/slots ####
        self.buttonGroup_groupby.buttonToggled.connect(
            self._set_data_aggregation_format
        )

        self.group_by_key_line_edit.setVisible(False)
        self.group_by_values_line_edit.setVisible(False)
        self.group_by_keys_label.setVisible(False)
        self.group_by_values_label.setVisible(False)

        # Config/Help dialogs
        self.provider_config.clicked.connect(lambda: on_config_click(self))
        self.help_button.clicked.connect(on_help_click)
        self.filter_help.clicked.connect(on_filter_help_click)

        self.about_button.clicked.connect(
            lambda: on_about_click(parent=self._iface.mainWindow())
        )
        self.provider_refresh.clicked.connect(self._on_prov_refresh_click)
        self.provider_combo.currentIndexChanged.connect(
            self.set_temporal_extent
        )
        # Point Layer tab
        self.point_layer_list_add.clicked.connect(self._add_point_layer)
        self.point_layer_list_remove.clicked.connect(self._remove_point_layer)
        # Polygon Layer tab
        self.layer_list_add.clicked.connect(self._add_polygon_layer)
        self.layer_list_remove.clicked.connect(self._remove_polygon_layer)
        # Centroid tab
        self.centroid_list_point_add.clicked.connect(self._on_linetool_init)
        self.centroid_list_point_clear.clicked.connect(
            self._on_clear_listwidget_click
        )

    # On Spec selection
    def _set_preferences(self):
        self.interval_years.setEnabled(True)
        self.interval_years.setStyleSheet("border: 1px solid green")
        self.interval_months.setEnabled(True)
        self.interval_months.setStyleSheet("border: 1px solid green")
        self.interval_days.setEnabled(True)
        self.interval_days.setStyleSheet("border: 1px solid green")

    def _set_data_aggregation_format(self):
        self.data_aggregation_format.clear()
        current_text = self.buttonGroup_groupby.checkedButton().text()
        # Set the available output formats
        if "boundary" in current_text:
            self.data_aggregation_format.addItems(
                DATA_AGGREGATION_FORMAT.get("groupBy/boundary")
            )
        else:
            self.data_aggregation_format.addItems(
                DATA_AGGREGATION_FORMAT.get("default")
            )
        # Set the available data aggregation settings. They differ a lot for each endpoint.
        # self.group_by_key_line_edit.setEnabled(False)
        self.group_by_key_line_edit.setStyleSheet("border: 1px solid grey")
        # self.group_by_values_line_edit.setEnabled(False)
        self.group_by_values_line_edit.setStyleSheet("border: 1px solid grey")
        if "groupBy/tag" in current_text:
            self.group_by_key_line_edit.setEnabled(True)
            self.group_by_key_line_edit.setStyleSheet("border: 1px solid green")
            self.group_by_values_line_edit.setEnabled(True)
            self.group_by_values_line_edit.setStyleSheet(
                "border: 1px solid green"
            )
        elif "key" in current_text:
            self.group_by_key_line_edit.setEnabled(True)
            self.group_by_key_line_edit.setStyleSheet("border: 1px solid green")

    def set_temporal_extent(self):
        start_date = self.date_start.dateTime()
        end_date = self.date_end.dateTime()
        metadata = None
        try:
            provider_id = self.provider_combo.currentIndex()
            provider = configmanager.read_config()["providers"][provider_id]
            clnt = client.Client(provider)
            metadata = clnt.check_api_metadata(self._iface)
            if (
                metadata.get("extractRegion")
                .get("temporalExtent")
                .get("fromTimestamp")
            ):
                start_date_string = (
                    metadata.get("extractRegion")
                    .get("temporalExtent")
                    .get("fromTimestamp")
                )
                start_date = QtCore.QDateTime.fromString(
                    start_date_string, "yyyy-MM-dd'T'HH:mm:ss'Z'"
                )
                if not start_date.isValid():
                    start_date = QtCore.QDateTime.fromString(
                        start_date_string, "yyyy-MM-dd'T'HH:mm'Z'"
                    )
            else:
                start_date = self.date_start.dateTime()

            if (
                metadata.get("extractRegion")
                .get("temporalExtent")
                .get("toTimestamp")
            ):
                end_date_string = (
                    metadata.get("extractRegion")
                    .get("temporalExtent")
                    .get("toTimestamp")
                )
                end_date = QtCore.QDateTime.fromString(
                    end_date_string, "yyyy-MM-dd'T'HH:mm:ss'Z'"
                )
                if not end_date.isValid():
                    end_date = QtCore.QDateTime.fromString(
                        end_date_string, "yyyy-MM-dd'T'HH:mm'Z'"
                    )
            else:
                end_date = self.date_end.dateTime()
            self.debug_text.setText(
                f"API success: The API {clnt.url} could be reached. Metadata set.\n"
            )
        except IndexError:
            msg = (
                "No providers found. Are providers available in your provider list?\n"
                "Clicking the refresh button could help.\n"
            )
            logger.log(msg, 1)
            self.debug_text.setText(msg)
        except Exception as e:
            if metadata is False:
                msg = (
                    f"API error: The API couldn't be reached. Check your connection.\n"
                    f"Metadata error: Date ranges couldn't be fetched automatically. Defaults are used which may "
                    "not cover the dates correctly.\n"
                )
                self.debug_text.setText(msg)
            else:
                msg = [e.__class__.__name__, str(e)]
                logger.log("{}: {}".format(*msg), 2)
                self.debug_text.setText(msg)
        finally:
            tooltip = f'<html><head/><body><p>Enter your end date. </p><p>All dates from {start_date.toString("yyyy-MM-dd")} until {end_date.toString("yyyy-MM-dd")} are valid.</p></body></html>'
            self.date_end.setDateTime(end_date)
            self.date_end.setMaximumDateTime(end_date)
            self.date_end.setMinimumDateTime(start_date)
            self.date_end.setToolTip(tooltip)
            self.date_start.setDateTime(start_date)
            self.date_start.setMaximumDateTime(end_date)
            self.date_start.setMinimumDateTime(start_date)
            self.date_start.setToolTip(tooltip)

    def _on_prov_refresh_click(self):
        """Populates provider dropdown with fresh list from config.yml"""

        providers = configmanager.read_config()["providers"]
        self.provider_combo.currentIndexChanged.disconnect(
            self.set_temporal_extent
        )
        self.provider_combo.clear()
        for provider in providers:
            self.provider_combo.addItem(provider["name"], provider)
        self.provider_combo.currentIndexChanged.connect(
            self.set_temporal_extent
        )

        self._set_preferences()

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

    def _add_point_layer(self) -> bool:
        layer = self.point_layer_input.currentLayer()
        list_name = (
            f"{layer.name()} | Radius: {self.point_layer_radius_input.value()}"
        )
        if layer and not check_list_duplicates(
            self.point_layer_list, list_name
        ):
            self.point_layer_list.addItem(list_name)
            self.point_layer_input.setCurrentIndex(0)
        else:
            return False
        return True

    def _remove_point_layer(self):
        layers: QListWidget = self.point_layer_list
        selected_layers: [QListWidgetItem] = layers.selectedItems()
        if not selected_layers:
            return
        element: QListWidgetItem
        for element in selected_layers:
            self.point_layer_list.takeItem(self.point_layer_list.row(element))

    def _add_polygon_layer(self) -> bool:
        layer = self.layer_input.currentLayer()
        if layer and not check_list_duplicates(self.layer_list, layer.name()):
            self.layer_list.addItem(layer.name())
            self.layer_input.setCurrentIndex(0)
        else:
            return False
        return True

    def _remove_polygon_layer(self):
        layers: QListWidget = self.layer_list
        selected_layers: [QListWidgetItem] = layers.selectedItems()
        if not selected_layers:
            return
        element: QListWidgetItem
        for element in selected_layers:
            self.layer_list.takeItem(self.layer_list.row(element))
