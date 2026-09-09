import os

from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QPushButton,
    QDateEdit,
    QMessageBox,
    QGroupBox,
)
from qgis.PyQt.QtCore import QDate
from qgis.PyQt.QtSvgWidgets import QSvgWidget
from qgis.gui import QgsExtentWidget, QgsCollapsibleGroupBox
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsRectangle,
    QgsSettings,
)
from qgis.utils import iface

from .download_manager import OhsomeDownloadManager

SETTINGS_GROUP = "ohsome_osm_downloader"
SETTINGS_API_KEY = "api_key"

PLUGIN_DIR = os.path.dirname(__file__)
OHSOME_LOGO_PATH = os.path.join(PLUGIN_DIR, "img", "ohsome-logo.svg")


class OhsomeExtractionWidget(QDialog):
    """Dialog for extracting OSM data via the ohsome API."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ohsome Data Extraction")
        self.resize(575, 200)
        self.manager = OhsomeDownloadManager()

        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # --- Logo header ---
        if os.path.exists(OHSOME_LOGO_PATH):
            logo_row = QHBoxLayout()
            logo_widget = QSvgWidget(OHSOME_LOGO_PATH)
            logo_widget.setFixedHeight(40)
            logo_widget.setFixedWidth(
                int(
                    40
                    * logo_widget.renderer().defaultSize().width()
                    / max(logo_widget.renderer().defaultSize().height(), 1)
                )
            )
            logo_row.addStretch()
            logo_row.addWidget(logo_widget)
            logo_row.addStretch()
            layout.addLayout(logo_row)

        # --- API key, Extent, Filter in one column ---
        main_col = QVBoxLayout()
        main_col.setSpacing(8)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("API key")
        main_col.addWidget(self.api_key_edit)
        
        self.extent_widget = QgsExtentWidget(self)
        self.extent_widget.setMaximumHeight(25)
        canvas = iface.mapCanvas() if iface else None
        project_crs = QgsProject.instance().crs()
        if canvas is not None:
            self.extent_widget.setOriginalExtent(
                canvas.extent(), project_crs
            )
            self.extent_widget.setCurrentExtent(canvas.extent(), project_crs)
            self.extent_widget.setMapCanvas(canvas)
        self.extent_widget.setOutputCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        main_col.addWidget(self.extent_widget)
        
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter")
        main_col.addWidget(self.filter_edit)
        
        layout.addLayout(main_col)

        # --- Options (Time + Properties) ---
        options_group = QgsCollapsibleGroupBox("Options")
        options_group.setCollapsed(True)
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)

        # Time section
        self.time_button_group = QButtonGroup(self)
        self.single_time_radio = QRadioButton("Single snapshot")
        self.range_time_radio = QRadioButton("Time range")
        self.single_time_radio.setChecked(True)
        self.time_button_group.addButton(self.single_time_radio)
        self.time_button_group.addButton(self.range_time_radio)

        single_row = QHBoxLayout()
        single_row.setSpacing(6)
        single_row.addWidget(self.single_time_radio)
        self.single_date_edit = QDateEdit(QDate.currentDate())
        self.single_date_edit.setCalendarPopup(True)
        single_row.addWidget(self.single_date_edit)
        single_row.addStretch()
        options_layout.addLayout(single_row)

        range_row = QHBoxLayout()
        range_row.setSpacing(6)
        range_row.addWidget(self.range_time_radio)
        self.start_date_edit = QDateEdit(QDate.currentDate().addYears(-1))
        self.start_date_edit.setCalendarPopup(True)
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        range_row.addWidget(QLabel("Start:"))
        range_row.addWidget(self.start_date_edit)
        range_row.addWidget(QLabel("End:"))
        range_row.addWidget(self.end_date_edit)
        range_row.addStretch()
        options_layout.addLayout(range_row)

        # Properties section
        props_row = QHBoxLayout()
        props_row.setSpacing(10)
        self.tags_checkbox = QCheckBox("tags")
        self.metadata_checkbox = QCheckBox("metadata")
        self.split_by_timestamp_checkbox = QCheckBox("one layer per timestamp")
        props_row.addWidget(self.tags_checkbox)
        props_row.addWidget(self.metadata_checkbox)
        props_row.addWidget(self.split_by_timestamp_checkbox)
        props_row.addStretch()
        options_layout.addLayout(props_row)

        layout.addWidget(options_group)

        # --- Buttons ---
        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        self.run_button = QPushButton("Run")
        self.cancel_button = QPushButton("Cancel")
        self.run_button.setMinimumWidth(80)
        self.cancel_button.setMinimumWidth(80)
        button_row.addStretch()
        button_row.addWidget(self.run_button)
        button_row.addWidget(self.cancel_button)
        layout.addLayout(button_row)

        self.run_button.clicked.connect(self._on_run)
        self.cancel_button.clicked.connect(self.reject)

    def _generate_layer_name(self, ohsome_filter: str, timestamp: str) -> str:
        """Generate a layer name from filter and timestamp."""
        timestamp_short = timestamp.replace("T00:00:00Z", "").replace("T", "_")
        return f"{ohsome_filter}_{timestamp_short}"

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
    
    def _generate_layer_name(self, timestamp: str) -> str:
        """Generate a layer name from timestamp."""
        return f"ohsome_osm_{timestamp}"
    
    def _on_run(self):
        ohsome_filter = self.filter_edit.text().strip()
        if not ohsome_filter:
            QMessageBox.warning(
                self, "Missing filter", "Please enter an ohsome filter."
            )
            return
    
        self._save_settings()
    
        aoi = self._get_aoi()
        time = self._get_time_value()
        properties = self._get_properties()
        split_by_timestamp = self.split_by_timestamp_checkbox.isChecked()
        api_key = self.api_key_edit.text().strip()
    
        # Generate timestamp string for naming
        if self.single_time_radio.isChecked():
            timestamp_str = self.single_date_edit.date().toString("yyyy-MM-dd")
        else:
            start = self.start_date_edit.date().toString("yyyy-MM-dd")
            end = self.end_date_edit.date().toString("yyyy-MM-dd")
            timestamp_str = f"{start}_to_{end}"
    
        output_name = self._generate_layer_name(timestamp_str)
    
        body = self.manager.build_request_body(
            aoi=aoi,
            ohsome_filter=ohsome_filter,
            time=time,
            properties=properties,
        )
    
        try:
            data = self.manager.fetch_parquet_bytes(
                body, api_key=api_key or None
            )
            layer = self.manager.parquet_bytes_to_layer(data, output_name)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self, "Request failed", f"Could not fetch data:\n{exc}"
            )
            return
    
        layers = self.manager.split_layer_by_geometry_type(layer, output_name)
    
        if split_by_timestamp:
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