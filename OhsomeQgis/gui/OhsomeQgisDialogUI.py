# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'OhsomeQgis/gui/OhsomeQgisDialogUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_OhsomeQgisDialogBase(object):
    def setupUi(self, OhsomeQgisDialogBase):
        OhsomeQgisDialogBase.setObjectName("OhsomeQgisDialogBase")
        OhsomeQgisDialogBase.resize(412, 868)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            OhsomeQgisDialogBase.sizePolicy().hasHeightForWidth()
        )
        OhsomeQgisDialogBase.setSizePolicy(sizePolicy)
        OhsomeQgisDialogBase.setSizeGripEnabled(True)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(OhsomeQgisDialogBase)
        self.verticalLayout_5.setSizeConstraint(
            QtWidgets.QLayout.SetMinAndMaxSize
        )
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.resources_group = QtWidgets.QGroupBox(OhsomeQgisDialogBase)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.resources_group.sizePolicy().hasHeightForWidth()
        )
        self.resources_group.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.resources_group.setFont(font)
        self.resources_group.setAlignment(QtCore.Qt.AlignCenter)
        self.resources_group.setFlat(False)
        self.resources_group.setObjectName("resources_group")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.resources_group)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.resources_group)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setOpenExternalLinks(True)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(
            self.label_3, 0, QtCore.Qt.AlignHCenter
        )
        self.label_2 = QtWidgets.QLabel(self.resources_group)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setOpenExternalLinks(True)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(
            self.label_2, 0, QtCore.Qt.AlignHCenter
        )
        self.label = QtWidgets.QLabel(self.resources_group)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label, 0, QtCore.Qt.AlignHCenter)
        self.verticalLayout_5.addWidget(self.resources_group)
        self.widget_4 = QtWidgets.QWidget(OhsomeQgisDialogBase)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.widget_4.sizePolicy().hasHeightForWidth()
        )
        self.widget_4.setSizePolicy(sizePolicy)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_15 = QtWidgets.QLabel(self.widget_4)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_7.addWidget(self.label_15)
        self.provider_combo = QtWidgets.QComboBox(self.widget_4)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.provider_combo.sizePolicy().hasHeightForWidth()
        )
        self.provider_combo.setSizePolicy(sizePolicy)
        self.provider_combo.setMinimumSize(QtCore.QSize(150, 25))
        self.provider_combo.setObjectName("provider_combo")
        self.horizontalLayout_7.addWidget(self.provider_combo)
        self.provider_refresh = QtWidgets.QPushButton(self.widget_4)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.provider_refresh.sizePolicy().hasHeightForWidth()
        )
        self.provider_refresh.setSizePolicy(sizePolicy)
        self.provider_refresh.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/plugins/OhsomeQgis/img/icon_refresh.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.provider_refresh.setIcon(icon)
        self.provider_refresh.setObjectName("provider_refresh")
        self.horizontalLayout_7.addWidget(self.provider_refresh)
        self.provider_config = QtWidgets.QPushButton(self.widget_4)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.provider_config.sizePolicy().hasHeightForWidth()
        )
        self.provider_config.setSizePolicy(sizePolicy)
        self.provider_config.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/plugins/OhsomeQgis/img/icon_settings.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.provider_config.setIcon(icon1)
        self.provider_config.setObjectName("provider_config")
        self.horizontalLayout_7.addWidget(self.provider_config)
        self.verticalLayout_5.addWidget(self.widget_4)
        self.tabWidget = QtWidgets.QTabWidget(OhsomeQgisDialogBase)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.tabWidget.sizePolicy().hasHeightForWidth()
        )
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setObjectName("tabWidget")
        self.qwidget = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.qwidget.sizePolicy().hasHeightForWidth()
        )
        self.qwidget.setSizePolicy(sizePolicy)
        self.qwidget.setObjectName("qwidget")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.qwidget)
        self.verticalLayout_7.setSizeConstraint(
            QtWidgets.QLayout.SetDefaultConstraint
        )
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.routing_travel_group = QtWidgets.QWidget(self.qwidget)
        self.routing_travel_group.setObjectName("routing_travel_group")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(
            self.routing_travel_group
        )
        self.horizontalLayout_2.setSizeConstraint(
            QtWidgets.QLayout.SetDefaultConstraint
        )
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.routing_travel_label = QtWidgets.QLabel(self.routing_travel_group)
        self.routing_travel_label.setObjectName("routing_travel_label")
        self.horizontalLayout_2.addWidget(self.routing_travel_label)
        self.routing_travel_combo = QtWidgets.QComboBox(
            self.routing_travel_group
        )
        self.routing_travel_combo.setObjectName("routing_travel_combo")
        self.horizontalLayout_2.addWidget(self.routing_travel_combo)
        self.routing_preference_combo = QtWidgets.QComboBox(
            self.routing_travel_group
        )
        self.routing_preference_combo.setObjectName("routing_preference_combo")
        self.horizontalLayout_2.addWidget(self.routing_preference_combo)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 3)
        self.horizontalLayout_2.setStretch(2, 2)
        self.verticalLayout_7.addWidget(self.routing_travel_group)
        self.widget = QtWidgets.QWidget(self.qwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.widget.sizePolicy().hasHeightForWidth()
        )
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setSizeConstraint(
            QtWidgets.QLayout.SetDefaultConstraint
        )
        self.gridLayout.setObjectName("gridLayout")
        self.routing_fromline_map = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.routing_fromline_map.sizePolicy().hasHeightForWidth()
        )
        self.routing_fromline_map.setSizePolicy(sizePolicy)
        self.routing_fromline_map.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/plugins/OhsomeQgis/img/icon_add.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.routing_fromline_map.setIcon(icon2)
        self.routing_fromline_map.setObjectName("routing_fromline_map")
        self.gridLayout.addWidget(self.routing_fromline_map, 0, 0, 1, 1)
        self.routing_fromline_clear = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.routing_fromline_clear.sizePolicy().hasHeightForWidth()
        )
        self.routing_fromline_clear.setSizePolicy(sizePolicy)
        self.routing_fromline_clear.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(":/plugins/OhsomeQgis/img/icon_clear.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.routing_fromline_clear.setIcon(icon3)
        self.routing_fromline_clear.setObjectName("routing_fromline_clear")
        self.gridLayout.addWidget(self.routing_fromline_clear, 1, 0, 1, 1)
        self.routing_fromline_list = QtWidgets.QListWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.routing_fromline_list.sizePolicy().hasHeightForWidth()
        )
        self.routing_fromline_list.setSizePolicy(sizePolicy)
        self.routing_fromline_list.setMinimumSize(QtCore.QSize(0, 0))
        self.routing_fromline_list.setMaximumSize(
            QtCore.QSize(16777215, 16777215)
        )
        self.routing_fromline_list.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.routing_fromline_list.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection
        )
        self.routing_fromline_list.setResizeMode(QtWidgets.QListView.Fixed)
        self.routing_fromline_list.setObjectName("routing_fromline_list")
        self.gridLayout.addWidget(self.routing_fromline_list, 0, 2, 3, 1)
        self.verticalLayout_7.addWidget(self.widget)
        self.advances_group = QgsCollapsibleGroupBox(self.qwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.advances_group.sizePolicy().hasHeightForWidth()
        )
        self.advances_group.setSizePolicy(sizePolicy)
        self.advances_group.setMaximumSize(QtCore.QSize(16777215, 23))
        self.advances_group.setCheckable(False)
        self.advances_group.setChecked(False)
        self.advances_group.setCollapsed(True)
        self.advances_group.setSaveCollapsedState(False)
        self.advances_group.setObjectName("advances_group")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.advances_group)
        self.verticalLayout_3.setSizeConstraint(
            QtWidgets.QLayout.SetDefaultConstraint
        )
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.optimization_group = QgsCollapsibleGroupBox(self.advances_group)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.optimization_group.sizePolicy().hasHeightForWidth()
        )
        self.optimization_group.setSizePolicy(sizePolicy)
        self.optimization_group.setMinimumSize(QtCore.QSize(0, 0))
        self.optimization_group.setMaximumSize(QtCore.QSize(16777215, 23))
        self.optimization_group.setCheckable(True)
        self.optimization_group.setChecked(False)
        self.optimization_group.setCollapsed(True)
        self.optimization_group.setSaveCollapsedState(False)
        self.optimization_group.setObjectName("optimization_group")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.optimization_group)
        self.gridLayout_2.setSizeConstraint(
            QtWidgets.QLayout.SetDefaultConstraint
        )
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_4 = QtWidgets.QLabel(self.optimization_group)
        self.label_4.setEnabled(False)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 4)
        self.optimize_start = QtWidgets.QRadioButton(self.optimization_group)
        self.optimize_start.setObjectName("optimize_start")
        self.optimize_button_group = QtWidgets.QButtonGroup(
            OhsomeQgisDialogBase
        )
        self.optimize_button_group.setObjectName("optimize_button_group")
        self.optimize_button_group.addButton(self.optimize_start)
        self.gridLayout_2.addWidget(self.optimize_start, 2, 1, 1, 1)
        self.optimize_none = QtWidgets.QRadioButton(self.optimization_group)
        self.optimize_none.setChecked(True)
        self.optimize_none.setObjectName("optimize_none")
        self.optimize_button_group.addButton(self.optimize_none)
        self.gridLayout_2.addWidget(self.optimize_none, 2, 0, 1, 1)
        self.optimize_end = QtWidgets.QRadioButton(self.optimization_group)
        self.optimize_end.setObjectName("optimize_end")
        self.optimize_button_group.addButton(self.optimize_end)
        self.gridLayout_2.addWidget(self.optimize_end, 2, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.optimization_group)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(
            self.label_5, 1, 0, 1, 3, QtCore.Qt.AlignHCenter
        )
        self.verticalLayout_3.addWidget(self.optimization_group)
        self.routing_avoid_tags_group = QgsCollapsibleGroupBox(
            self.advances_group
        )
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.routing_avoid_tags_group.sizePolicy().hasHeightForWidth()
        )
        self.routing_avoid_tags_group.setSizePolicy(sizePolicy)
        self.routing_avoid_tags_group.setCheckable(True)
        self.routing_avoid_tags_group.setChecked(False)
        self.routing_avoid_tags_group.setCollapsed(True)
        self.routing_avoid_tags_group.setSaveCollapsedState(False)
        self.routing_avoid_tags_group.setObjectName("routing_avoid_tags_group")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.routing_avoid_tags_group)
        self.gridLayout_4.setSizeConstraint(
            QtWidgets.QLayout.SetDefaultConstraint
        )
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.routing_avoid_highways_3 = QtWidgets.QCheckBox(
            self.routing_avoid_tags_group
        )
        self.routing_avoid_highways_3.setObjectName("routing_avoid_highways_3")
        self.gridLayout_4.addWidget(self.routing_avoid_highways_3, 0, 0, 1, 1)
        self.routing_avoid_toll_3 = QtWidgets.QCheckBox(
            self.routing_avoid_tags_group
        )
        self.routing_avoid_toll_3.setObjectName("routing_avoid_toll_3")
        self.gridLayout_4.addWidget(self.routing_avoid_toll_3, 0, 1, 1, 1)
        self.routing_avoid_ferries_3 = QtWidgets.QCheckBox(
            self.routing_avoid_tags_group
        )
        self.routing_avoid_ferries_3.setObjectName("routing_avoid_ferries_3")
        self.gridLayout_4.addWidget(self.routing_avoid_ferries_3, 1, 0, 1, 1)
        self.routing_avoid_fords_3 = QtWidgets.QCheckBox(
            self.routing_avoid_tags_group
        )
        self.routing_avoid_fords_3.setObjectName("routing_avoid_fords_3")
        self.gridLayout_4.addWidget(self.routing_avoid_fords_3, 1, 1, 1, 1)
        self.routing_avoid_tracks_3 = QtWidgets.QCheckBox(
            self.routing_avoid_tags_group
        )
        self.routing_avoid_tracks_3.setObjectName("routing_avoid_tracks_3")
        self.gridLayout_4.addWidget(self.routing_avoid_tracks_3, 2, 0, 1, 1)
        self.verticalLayout_3.addWidget(self.routing_avoid_tags_group)
        self.routing_avoid_countries_group = QgsCollapsibleGroupBox(
            self.advances_group
        )
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.routing_avoid_countries_group.sizePolicy().hasHeightForWidth()
        )
        self.routing_avoid_countries_group.setSizePolicy(sizePolicy)
        self.routing_avoid_countries_group.setMaximumSize(
            QtCore.QSize(16777215, 23)
        )
        self.routing_avoid_countries_group.setCheckable(True)
        self.routing_avoid_countries_group.setChecked(False)
        self.routing_avoid_countries_group.setCollapsed(True)
        self.routing_avoid_countries_group.setSaveCollapsedState(False)
        self.routing_avoid_countries_group.setObjectName(
            "routing_avoid_countries_group"
        )
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(
            self.routing_avoid_countries_group
        )
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.countries_text = QgsFilterLineEdit(
            self.routing_avoid_countries_group
        )
        self.countries_text.setProperty("qgisRelation", "")
        self.countries_text.setObjectName("countries_text")
        self.verticalLayout_4.addWidget(self.countries_text)
        self.verticalLayout_3.addWidget(self.routing_avoid_countries_group)
        self.avoidpolygon_group = QgsCollapsibleGroupBox(self.advances_group)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.avoidpolygon_group.sizePolicy().hasHeightForWidth()
        )
        self.avoidpolygon_group.setSizePolicy(sizePolicy)
        self.avoidpolygon_group.setMaximumSize(QtCore.QSize(16777215, 23))
        self.avoidpolygon_group.setCheckable(True)
        self.avoidpolygon_group.setChecked(False)
        self.avoidpolygon_group.setCollapsed(True)
        self.avoidpolygon_group.setSaveCollapsedState(False)
        self.avoidpolygon_group.setObjectName("avoidpolygon_group")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.avoidpolygon_group)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.avoidpolygon_dropdown = QgsMapLayerComboBox(
            self.avoidpolygon_group
        )
        self.avoidpolygon_dropdown.setShowCrs(False)
        self.avoidpolygon_dropdown.setObjectName("avoidpolygon_dropdown")
        self.verticalLayout_6.addWidget(self.avoidpolygon_dropdown)
        self.verticalLayout_3.addWidget(self.avoidpolygon_group)
        self.verticalLayout_7.addWidget(self.advances_group)
        self.tabWidget.addTab(self.qwidget, "")
        self.batch_tab = QtWidgets.QWidget()
        self.batch_tab.setObjectName("batch_tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.batch_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.batch_tab)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.batch_routing_line = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.batch_routing_line.sizePolicy().hasHeightForWidth()
        )
        self.batch_routing_line.setSizePolicy(sizePolicy)
        self.batch_routing_line.setObjectName("batch_routing_line")
        self.horizontalLayout.addWidget(self.batch_routing_line)
        self.batch_routing_point = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.batch_routing_point.sizePolicy().hasHeightForWidth()
        )
        self.batch_routing_point.setSizePolicy(sizePolicy)
        self.batch_routing_point.setObjectName("batch_routing_point")
        self.horizontalLayout.addWidget(self.batch_routing_point)
        self.batch_routing_points = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.batch_routing_points.sizePolicy().hasHeightForWidth()
        )
        self.batch_routing_points.setSizePolicy(sizePolicy)
        self.batch_routing_points.setObjectName("batch_routing_points")
        self.horizontalLayout.addWidget(self.batch_routing_points)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.batch_tab)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.batch_iso_point = QtWidgets.QPushButton(self.groupBox_2)
        self.batch_iso_point.setObjectName("batch_iso_point")
        self.horizontalLayout_4.addWidget(self.batch_iso_point)
        self.batch_iso_layer = QtWidgets.QPushButton(self.groupBox_2)
        self.batch_iso_layer.setObjectName("batch_iso_layer")
        self.horizontalLayout_4.addWidget(self.batch_iso_layer)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.batch_tab)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.batch_matrix = QtWidgets.QPushButton(self.groupBox_3)
        self.batch_matrix.setObjectName("batch_matrix")
        self.horizontalLayout_5.addWidget(self.batch_matrix)
        self.verticalLayout.addWidget(self.groupBox_3)
        spacerItem = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding,
        )
        self.verticalLayout.addItem(spacerItem)
        self.tabWidget.addTab(self.batch_tab, "")
        self.verticalLayout_5.addWidget(self.tabWidget)
        self.ors_log_group = QgsCollapsibleGroupBox(OhsomeQgisDialogBase)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ors_log_group.sizePolicy().hasHeightForWidth()
        )
        self.ors_log_group.setSizePolicy(sizePolicy)
        self.ors_log_group.setMinimumSize(QtCore.QSize(0, 0))
        self.ors_log_group.setMaximumSize(QtCore.QSize(16777215, 23))
        self.ors_log_group.setFlat(True)
        self.ors_log_group.setCollapsed(True)
        self.ors_log_group.setSaveCollapsedState(False)
        self.ors_log_group.setObjectName("ors_log_group")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.ors_log_group)
        self.verticalLayout_2.setSizeConstraint(
            QtWidgets.QLayout.SetDefaultConstraint
        )
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.debug_text = QtWidgets.QTextBrowser(self.ors_log_group)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.debug_text.sizePolicy().hasHeightForWidth()
        )
        self.debug_text.setSizePolicy(sizePolicy)
        self.debug_text.setMinimumSize(QtCore.QSize(0, 80))
        self.debug_text.setMaximumSize(QtCore.QSize(16777215, 80))
        self.debug_text.setAutoFormatting(QtWidgets.QTextEdit.AutoBulletList)
        self.debug_text.setTabStopWidth(80)
        self.debug_text.setOpenExternalLinks(True)
        self.debug_text.setObjectName("debug_text")
        self.verticalLayout_2.addWidget(self.debug_text)
        self.verticalLayout_5.addWidget(self.ors_log_group)
        self.widget_2 = QtWidgets.QWidget(OhsomeQgisDialogBase)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.widget_2.sizePolicy().hasHeightForWidth()
        )
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.help_button = QtWidgets.QPushButton(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.help_button.sizePolicy().hasHeightForWidth()
        )
        self.help_button.setSizePolicy(sizePolicy)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(":/plugins/OhsomeQgis/img/icon_help.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.help_button.setIcon(icon4)
        self.help_button.setObjectName("help_button")
        self.horizontalLayout_8.addWidget(self.help_button)
        self.about_button = QtWidgets.QPushButton(self.widget_2)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(":/plugins/OhsomeQgis/img/icon_about.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.about_button.setIcon(icon5)
        self.about_button.setObjectName("about_button")
        self.horizontalLayout_8.addWidget(self.about_button)
        self.global_buttons = QtWidgets.QDialogButtonBox(self.widget_2)
        self.global_buttons.setOrientation(QtCore.Qt.Horizontal)
        self.global_buttons.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.global_buttons.setObjectName("global_buttons")
        self.horizontalLayout_8.addWidget(self.global_buttons)
        self.verticalLayout_5.addWidget(self.widget_2)
        self.widget_4.raise_()
        self.resources_group.raise_()
        self.widget_2.raise_()
        self.ors_log_group.raise_()
        self.tabWidget.raise_()

        self.retranslateUi(OhsomeQgisDialogBase)
        self.tabWidget.setCurrentIndex(0)
        self.global_buttons.accepted.connect(OhsomeQgisDialogBase.accept)
        self.global_buttons.rejected.connect(OhsomeQgisDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(OhsomeQgisDialogBase)

    def retranslateUi(self, OhsomeQgisDialogBase):
        _translate = QtCore.QCoreApplication.translate
        OhsomeQgisDialogBase.setWindowTitle(
            _translate("OhsomeQgisDialogBase", "ORS Tools")
        )
        self.resources_group.setTitle(
            _translate("OhsomeQgisDialogBase", "Resources")
        )
        self.label_3.setText(
            _translate(
                "OhsomeQgisDialogBase",
                '<html><head/><body><p><a href="https://openrouteservice.org/dev/#/signup"><span style="font-weight: bold; text-decoration: underline; color:#a8b1f5;">Sign Up</span></a></p></body></html>',
            )
        )
        self.label_2.setText(
            _translate(
                "OhsomeQgisDialogBase",
                '<html><head/><body><p><a href="https://openrouteservice.org/dev/#/home"><span style="font-weight: bold; text-decoration: underline; color:#a8b1f5;">Dashboard</span></a></p></body></html>',
            )
        )
        self.label.setText(
            _translate(
                "OhsomeQgisDialogBase",
                '<html><head/><body><p><a href="https://ask.openrouteservice.org/c/sdks/qgis"><span style="font-weight: bold; text-decoration: underline; color:#a8b1f5;">Forum</span></a></p></body></html>',
            )
        )
        self.label_15.setText(_translate("OhsomeQgisDialogBase", "Provider"))
        self.provider_refresh.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                "Refresh the provider list. Needed after a provider was added or deleted.",
            )
        )
        self.provider_config.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                "Shortcut to Web ► ORS Tools ► Provider Settings",
            )
        )
        self.routing_travel_label.setText(
            _translate("OhsomeQgisDialogBase", "Select a spec")
        )
        self.routing_travel_combo.setToolTip(
            _translate("OhsomeQgisDialogBase", "Ohsome Endpoint")
        )
        self.routing_preference_combo.setToolTip(
            _translate("OhsomeQgisDialogBase", "Request preference")
        )
        self.routing_fromline_map.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                "<html><head/><body><p>Add wayoints interactively from the map canvas.</p><p>Double-click will terminate waypoint selection.</p></body></html>",
            )
        )
        self.routing_fromline_clear.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                "<html><head/><body><p>If waypoints are selected in the list, only these will be deleted. Else all waypoints will be deleted.</p></body></html>",
            )
        )
        self.routing_fromline_list.setToolTip(
            _translate("OhsomeQgisDialogBase", "Select waypoints from the map!")
        )
        self.advances_group.setTitle(
            _translate("OhsomeQgisDialogBase", "Advanced Configuration")
        )
        self.optimization_group.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                '<html><head/><body><p>Enabling Traveling Salesman will erase all other advanced configuration and assume the preference to be <span style=" font-weight:600;">fastest</span>.</p></body></html>',
            )
        )
        self.optimization_group.setTitle(
            _translate("OhsomeQgisDialogBase", "Traveling Salesman")
        )
        self.label_4.setText(
            _translate(
                "OhsomeQgisDialogBase",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" padding: 10px; -qt-block-indent:0; text-indent:0px ; background-color:#e7f2fa; color: #999999"><img stype="margin: 10px" src=":/plugins/OhsomeQgis/img/icon_about.png" width=16 height=16 />  All other configuration will be omitted</p></body></html>',
            )
        )
        self.optimize_start.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                "<html><head/><body><p>First waypoint will be optimized.</p></body></html>",
            )
        )
        self.optimize_start.setText(
            _translate("OhsomeQgisDialogBase", "Optimize Start")
        )
        self.optimize_none.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                "<html><head/><body><p>First and last waypoints are not optimized.</p></body></html>",
            )
        )
        self.optimize_none.setText(_translate("OhsomeQgisDialogBase", "None"))
        self.optimize_end.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                "<html><head/><body><p>Last waypoint will be optimized.</p></body></html>",
            )
        )
        self.optimize_end.setText(
            _translate("OhsomeQgisDialogBase", "Optimize End")
        )
        self.label_5.setText(
            _translate(
                "OhsomeQgisDialogBase",
                '<html><head/><body><p><span style=" font-weight:600;">Other Options</span></p></body></html>',
            )
        )
        self.routing_avoid_tags_group.setToolTip(
            _translate("OhsomeQgisDialogBase", "Avoid certain road attributes.")
        )
        self.routing_avoid_tags_group.setTitle(
            _translate("OhsomeQgisDialogBase", "Avoid tags")
        )
        self.routing_avoid_highways_3.setText(
            _translate("OhsomeQgisDialogBase", "highways")
        )
        self.routing_avoid_toll_3.setText(
            _translate("OhsomeQgisDialogBase", "tollways")
        )
        self.routing_avoid_ferries_3.setText(
            _translate("OhsomeQgisDialogBase", "ferries")
        )
        self.routing_avoid_fords_3.setText(
            _translate("OhsomeQgisDialogBase", "fords")
        )
        self.routing_avoid_tracks_3.setText(
            _translate("OhsomeQgisDialogBase", "steps")
        )
        self.routing_avoid_countries_group.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                "<html><head/><body><p>Avoid countries based on alphnumeric ISO 3166 Alpha-2 or Alpha-3 codes.</p><p>Find a list of codes at https://github.com/GIScience/openrouteservice-docs#country-list.</p></body></html>",
            )
        )
        self.routing_avoid_countries_group.setTitle(
            _translate("OhsomeQgisDialogBase", "Avoid countries")
        )
        self.countries_text.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                "<html><head/><body><p>Avoid countries based on ISO 3166 Alpha-2 or Alpha-3 codes.</p></body></html>",
            )
        )
        self.avoidpolygon_group.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                '<html><head/><body><p>Avoid areas by specifying a (Multi-)Polygon layer. </p><p><br/></p><p><span style=" font-weight:600;">Note</span>, only the first feature of the layer will be respected.</p></body></html>',
            )
        )
        self.avoidpolygon_group.setTitle(
            _translate("OhsomeQgisDialogBase", "Avoid polygon(s)")
        )
        self.avoidpolygon_dropdown.setToolTip(
            _translate(
                "OhsomeQgisDialogBase",
                '<html><head/><body><p>Avoid areas by specifying a (Multi-)Polygon layer. </p><p><br/></p><p><span style=" font-weight:600;">Note</span>, only the first feature of the layer will be respected.</p></body></html>',
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.qwidget),
            _translate("OhsomeQgisDialogBase", "Advanced Directions"),
        )
        self.groupBox.setTitle(_translate("OhsomeQgisDialogBase", "Directions"))
        self.batch_routing_line.setText(
            _translate("OhsomeQgisDialogBase", "Polylines Layer")
        )
        self.batch_routing_point.setText(
            _translate("OhsomeQgisDialogBase", "Points (1 Layer)")
        )
        self.batch_routing_points.setText(
            _translate("OhsomeQgisDialogBase", "Points (2 Layer)")
        )
        self.groupBox_2.setTitle(
            _translate("OhsomeQgisDialogBase", "Isochrones")
        )
        self.batch_iso_point.setText(
            _translate("OhsomeQgisDialogBase", "Isochrones from Point")
        )
        self.batch_iso_layer.setText(
            _translate("OhsomeQgisDialogBase", "Isochrones from Layer")
        )
        self.groupBox_3.setTitle(_translate("OhsomeQgisDialogBase", "Matrix"))
        self.batch_matrix.setText(_translate("OhsomeQgisDialogBase", "Matrix"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.batch_tab),
            _translate("OhsomeQgisDialogBase", "Batch Jobs"),
        )
        self.ors_log_group.setTitle(_translate("OhsomeQgisDialogBase", "Log"))
        self.debug_text.setPlaceholderText(
            _translate(
                "OhsomeQgisDialogBase",
                "Queries and errors will be printed here.",
            )
        )
        self.help_button.setText(_translate("OhsomeQgisDialogBase", "  Help"))
        self.about_button.setText(_translate("OhsomeQgisDialogBase", "About"))


from qgscollapsiblegroupbox import QgsCollapsibleGroupBox
from qgsfilterlineedit import QgsFilterLineEdit
from qgsmaplayercombobox import QgsMapLayerComboBox
from . import resources_rc
