from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QPushButton,
    QDateEdit,
    QMessageBox,
    QGroupBox,
)
from qgis.PyQt.QtCore import QDate
from qgis.gui import QgsExtentWidget
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsRectangle,
    QgsSettings,
)
from qgis.utils import iface

from .download_manager import OhsomeDownloadManager, GEOMETRY_TYPES

SETTINGS_GROUP = "ohsome_osm_downloader"
SETTINGS_API_KEY = "api_key"


class OhsomeExtractionWidget(QDialog):
    """Dialog for extracting OSM data via the ohsome API."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ohsome Data Extraction")
        self.manager = OhsomeDownloadManager()

        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # --- API key ---
        api_group = QGroupBox("ohsome API key")
        api_layout = QVBoxLayout(api_group)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText(
            "Optional: enter your ohsome API key"
        )
        api_layout.addWidget(self.api_key_edit)
        layout.addWidget(api_group)

        # --- Extent ---
        extent_group = QGroupBox("Extent")
        extent_layout = QVBoxLayout(extent_group)
        self.extent_widget = QgsExtentWidget(self)
        canvas = iface.mapCanvas() if iface else None
        project_crs = QgsProject.instance().crs()
        if canvas is not None:
            self.extent_widget.setOriginalExtent(
                canvas.extent(), project_crs
            )
            self.extent_widget.setCurrentExtent(canvas.extent(), project_crs)
            self.extent_widget.setMapCanvas(canvas)
        self.extent_widget.setOutputCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        extent_layout.addWidget(self.extent_widget)
        layout.addWidget(extent_group)

        # --- Filter ---
        filter_group = QGroupBox("Filter (ohsome filter syntax)")
        filter_layout = QVBoxLayout(filter_group)
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText(
            'e.g. building=* and geometry:polygon'
        )
        filter_layout.addWidget(self.filter_edit)
        layout.addWidget(filter_group)

        # --- Geometry type ---
        geom_form = QFormLayout()
        self.geometry_type_combo = QComboBox()
        self.geometry_type_combo.addItems(GEOMETRY_TYPES)
        geom_form.addRow("Geometry type:", self.geometry_type_combo)
        layout.addLayout(geom_form)

        # --- Time ---
        time_group = QGroupBox("Time")
        time_layout = QVBoxLayout(time_group)

        self.time_button_group = QButtonGroup(self)
        self.single_time_radio = QRadioButton("Single snapshot")
        self.range_time_radio = QRadioButton("Time range")
        self.single_time_radio.setChecked(True)
        self.time_button_group.addButton(self.single_time_radio)
        self.time_button_group.addButton(self.range_time_radio)

        single_row = QHBoxLayout()
        single_row.addWidget(self.single_time_radio)
        self.single_date_edit = QDateEdit(QDate.currentDate())
        self.single_date_edit.setCalendarPopup(True)
        single_row.addWidget(self.single_date_edit)
        time_layout.addLayout(single_row)

        range_row = QHBoxLayout()
        range_row.addWidget(self.range_time_radio)
        self.start_date_edit = QDateEdit(QDate.currentDate().addYears(-1))
        self.start_date_edit.setCalendarPopup(True)
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        range_row.addWidget(QLabel("Start:"))
        range_row.addWidget(self.start_date_edit)
        range_row.addWidget(QLabel("End:"))
        range_row.addWidget(self.end_date_edit)
        time_layout.addLayout(range_row)

        layout.addWidget(time_group)

        # --- Properties ---
        props_group = QGroupBox("Properties to include")
        props_layout = QVBoxLayout(props_group)
        self.tags_checkbox = QCheckBox("tags")
        self.metadata_checkbox = QCheckBox("metadata")
        self.split_by_timestamp_checkbox = QCheckBox(
            "Create one layer per timestamp"
        )
        props_layout.addWidget(self.tags_checkbox)
        props_layout.addWidget(self.metadata_checkbox)
        props_layout.addWidget(self.split_by_timestamp_checkbox)
        layout.addWidget(props_group)

        # --- Output ---
        output_form = QFormLayout()
        self.output_name_edit = QLineEdit("ohsome_extraction")
        output_form.addRow("Output layer name:", self.output_name_edit)
        layout.addLayout(output_form)

        # --- Buttons ---
        button_row = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.cancel_button = QPushButton("Cancel")
        button_row.addStretch()
        button_row.addWidget(self.run_button)
        button_row.addWidget(self.cancel_button)
        layout.addLayout(button_row)

        self.run_button.clicked.connect(self._on_run)
        self.cancel_button.clicked.connect(self.reject)

    def _load_settings(self):
        settings = QgsSettings()
        api_key = settings.value(
            f"{SETTINGS_GROUP}/{SETTINGS_API_KEY}", "", type=str
        )
        self.api_key_edit.setText(api_key)

    def _save_settings(self):
        settings = QgsSettings()
        settings.setValue(
            f"{SETTINGS_GROUP}/{SETTINGS_API_KEY}", self.api_key_edit.text()
        )

    def _get_aoi(self) -> list[float]:
        extent: QgsRectangle = self.extent_widget.outputExtent()
        return [
            extent.xMinimum(),
            extent.yMinimum(),
            extent.xMaximum(),
            extent.yMaximum(),
        ]

    def _get_properties(self) -> list[str]:
        props = []
        if self.tags_checkbox.isChecked():
            props.append("tags")
        if self.metadata_checkbox.isChecked():
            props.append("metadata")
        return props

    def _get_time_value(self):
        """Return the time value for the request body: either a single
        ISO8601 string, or a dict with start/end for ranges.
        """
        if self.single_time_radio.isChecked():
            return self.single_date_edit.date().toString(
                "yyyy-MM-dd'T00:00:00Z'"
            )
        start = self.start_date_edit.date().toString("yyyy-MM-dd'T00:00:00Z'")
        end = self.end_date_edit.date().toString("yyyy-MM-dd'T00:00:00Z'")
        return {"start": start, "end": end}

    def _on_run(self):
        ohsome_filter = self.filter_edit.text().strip()
        if not ohsome_filter:
            QMessageBox.warning(
                self, "Missing filter", "Please enter an ohsome filter."
            )
            return

        self._save_settings()

        geometry_type = self.geometry_type_combo.currentText()
        aoi = self._get_aoi()
        time = self._get_time_value()
        properties = self._get_properties()
        output_name = self.output_name_edit.text().strip() or "ohsome_extraction"
        split_by_timestamp = self.split_by_timestamp_checkbox.isChecked()
        api_key = self.api_key_edit.text().strip()

        body = self.manager.build_request_body(
            aoi=aoi,
            ohsome_filter=ohsome_filter,
            time=time,
            properties=properties,
        )

        try:
            data = self.manager.fetch_parquet_bytes(
                geometry_type, body, api_key=api_key or None
            )
            layer = self.manager.parquet_bytes_to_layer(data, output_name)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self, "Request failed", f"Could not fetch data:\n{exc}"
            )
            return

        layers = self.manager.split_layer_by_geometry_type(layer, output_name)

        if split_by_timestamp:
            # Further split each geometry-type layer by timestamp
            final_layers = []
            for geom_layer in layers:
                final_layers.extend(
                    self.manager.split_layer_by_timestamp(
                        geom_layer, geom_layer.name()
                    )
                )
            layers = final_layers

        self.manager.add_layers_to_project(layers)

        QMessageBox.information(
            self,
            "Done",
            f"Added {len(layers)} layer(s) to the project.",
        )
        self.accept()