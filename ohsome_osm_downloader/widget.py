import os
import json

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
    QComboBox,
    QCompleter,
)
from qgis.PyQt.QtCore import QDate, Qt, QUrl
from qgis.PyQt.QtSvgWidgets import QSvgWidget
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsRectangle,
    QgsSettings,
    QgsBlockingNetworkRequest,
)
from qgis.gui import QgsExtentWidget, QgsCollapsibleGroupBox, QgsMessageBar
from qgis.utils import iface

from .download_manager import OhsomeDownloadManager

SETTINGS_GROUP = "ohsome_osm_downloader"
SETTINGS_API_KEY = "api_key"

PLUGIN_DIR = os.path.dirname(__file__)
OHSOME_LOGO_PATH = os.path.join(PLUGIN_DIR, "img", "ohsome-logo.svg")

OHSOME_QUALITY_API = "https://api.heigit.org/ohsome-quality-api/v2/metadata/topics"

# Featured topics to show as buttons
FEATURED_TOPICS = ["buildings", "roads", "hospitals", "schools", "parks"]


class OhsomeExtractionWidget(QDialog):
    """Dialog for extracting OSM data via the ohsome API."""

    def __init__(self, iface=None):
        super().__init__(iface.mainWindow() if iface else None)
        self.iface = iface
        self.setWindowTitle("ohsome Data Extraction")
        self.resize(575, 200)
        self.manager = OhsomeDownloadManager()
        self.topics = {}

        self._load_topics()
        self._build_ui()
        self._load_settings()

    def _load_topics(self):
        """Fetch topics from ohsome quality API."""
        try:
            request = QNetworkRequest(QUrl(OHSOME_QUALITY_API))
            request.setRawHeader(b"accept", b"application/json")
            blocking_request = QgsBlockingNetworkRequest()
            error_code = blocking_request.get(request)
            if error_code == QgsBlockingNetworkRequest.ErrorCode.NoError:
                reply = blocking_request.reply()
                data = json.loads(bytes(reply.content()))
                self.topics = data.get("result", {})
        except Exception as e:
            print(f"Failed to load topics: {e}")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.message_bar = self.iface.messageBar() if self.iface else None
        
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

        # --- API key, Extent ---
        main_col = QVBoxLayout()
        main_col.setSpacing(8)
        
        api_key_label = QLabel("<b>API key</b>")
        main_col.addWidget(api_key_label)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("API key")
        main_col.addWidget(self.api_key_edit)
        
        extent_label = QLabel("<b>Extent</b>")
        main_col.addWidget(extent_label)
        self.extent_widget = QgsExtentWidget(self)
        self.extent_widget.setMaximumHeight(25)
        canvas = self.iface.mapCanvas()
        project_crs = QgsProject.instance().crs()
        if canvas is not None:
            self.extent_widget.setOriginalExtent(
                canvas.extent(), project_crs
            )
            self.extent_widget.setCurrentExtent(canvas.extent(), project_crs)
            self.extent_widget.setMapCanvas(canvas)
        self.extent_widget.setOutputCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        main_col.addWidget(self.extent_widget)
        
        layout.addLayout(main_col)

        # --- Topics section ---
        topics_group = QGroupBox("Topic")
        topics_layout = QVBoxLayout(topics_group)
        topics_layout.setSpacing(8)

        # Featured topic buttons
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(6)
        self.topic_buttons = {}
        
        buttons_row.addStretch()
        for topic_id in FEATURED_TOPICS:
            if topic_id in self.topics:
                topic_name = self.topics[topic_id].get("name", topic_id)
                btn = QPushButton(topic_name)
                btn.setCheckable(True)
                btn.clicked.connect(
                    lambda checked, tid=topic_id: self._on_topic_button_clicked(tid)
                )
                self.topic_buttons[topic_id] = btn
                buttons_row.addWidget(btn)
        buttons_row.addStretch()
        topics_layout.addLayout(buttons_row)

        # Extra topics combobox
        extra_row = QHBoxLayout()
        extra_row.setSpacing(6)
        extra_row.addStretch()
        extra_row.addWidget(QLabel("Extra topics:"))
        self.extra_topics_combo = QComboBox()
        self.extra_topics_combo.setEditable(True)
        self.extra_topics_combo.completer().setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )

        for topic_id in sorted(self.topics):
            topic_name = self.topics[topic_id].get("name", topic_id)
            self.extra_topics_combo.addItem(topic_name, topic_id)

        self.extra_topics_combo.addItem("Custom (Specify in filter box)", "custom")
        self.extra_topics_combo.currentIndexChanged.connect(
            self._on_extra_topic_changed
        )
        
        self.extra_topics_combo.setCurrentIndex(-1)
        self.extra_topics_combo.currentIndexChanged.connect(
            self._on_extra_topic_changed
        )
        self.extra_topics_combo.setMaximumWidth(250)
        extra_row.addWidget(self.extra_topics_combo)
        extra_row.addStretch()
        topics_layout.addLayout(extra_row)

        layout.addWidget(topics_group)

        # --- Options (Time + Properties) ---
        options_group = QgsCollapsibleGroupBox("Options")
        options_group.setCollapsed(True)
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)

        # Selected filter display (collapsible)
        self.filter_display = QLineEdit()
        self.filter_display.setReadOnly(True)
        self.filter_display.setPlaceholderText("Select a topic")
        options_layout.addWidget(self.filter_display)

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

    def _on_topic_button_clicked(self, topic_id: str):
        """Select a featured topic and synchronize the combobox."""
        for tid, btn in self.topic_buttons.items():
            btn.setChecked(tid == topic_id)

        combo_index = self.extra_topics_combo.findData(topic_id)
        if combo_index >= 0:
            was_blocked = self.extra_topics_combo.blockSignals(True)
            self.extra_topics_combo.setCurrentIndex(combo_index)
            self.extra_topics_combo.blockSignals(was_blocked)

        self._set_filter_from_topic(topic_id)

    def _on_extra_topic_changed(self):
        """Select a combobox topic and synchronize featured buttons."""
        topic_id = self.extra_topics_combo.currentData()

        if not topic_id:
            return

        if topic_id.lower() == "custom":
            self.filter_display.setReadOnly(False)
        else:
            self.filter_display.setReadOnly(True)

        for tid, btn in self.topic_buttons.items():
            btn.setChecked(tid == topic_id)

        if topic_id:
            self._set_filter_from_topic(topic_id)

    def _set_filter_from_topic(self, topic_id: str):
        """Set filter display from topic ID."""
        if topic_id in self.topics:
            filter_str = self.topics[topic_id].get("filter", "")
            self.filter_display.setText(filter_str)

    def _generate_layer_name(self, timestamp: str) -> str:
        """Generate a layer name from timestamp."""
        return f"ohsome_osm_{timestamp}"

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
        """Return the time value for the request body."""
        if self.single_time_radio.isChecked():
            return self.single_date_edit.date().toString(
                "yyyy-MM-dd'T00:00:00Z'"
            )
        start = self.start_date_edit.date().toString("yyyy-MM-dd'T00:00:00Z'")
        end = self.end_date_edit.date().toString("yyyy-MM-dd'T00:00:00Z'")
        return {"start": start, "end": end}

    def _validate_inputs(self) -> bool:
        """Validate request inputs and show failures in the message bar."""
        self.message_bar.clearWidgets()

        if not self.filter_display.text().strip():
            self.message_bar.pushWarning(
                "Missing topic",
                "Please select a topic before running the extraction.",
            )
            return False

        extent = self.extent_widget.outputExtent()
        if extent.width() <= 0 or extent.height() <= 0:
            self.message_bar.pushWarning(
                "Invalid extent",
                "Please provide an extent with a non-zero width and height.",
            )
            return False

        if (
            self.range_time_radio.isChecked()
            and self.start_date_edit.date() > self.end_date_edit.date()
        ):
            self.message_bar.pushWarning(
                "Invalid time range",
                "The start date must be before or equal to the end date.",
            )
            return False

        return True

    def _on_run(self):
        if not self._validate_inputs():
            return

        self._save_settings()

        ohsome_filter = self.filter_display.text().strip()

        self._save_settings()

        aoi = self._get_aoi()
        time = self._get_time_value()
        properties = self._get_properties()
        split_by_timestamp = self.split_by_timestamp_checkbox.isChecked()
        api_key = self.api_key_edit.text().strip()

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
        except Exception as exc:
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