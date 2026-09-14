#-----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

import os

from qgis.PyQt.QtWidgets import QAction 
from qgis.PyQt.QtGui import QIcon
from .widget import OhsomeExtractionWidget


class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'img', 'icon.png')
        icon = QIcon(icon_path)
        self.action = QAction(icon, '&ohsome', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu('&ohsome', self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu('&ohsome', self.action)
        del self.action

    def run(self):
        self.dialog = OhsomeExtractionWidget(iface=self.iface)
        self.dialog.show()