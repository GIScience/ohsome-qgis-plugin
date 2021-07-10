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

from qgis.core import QgsApplication

from .gui import OhsomeQgisDialog
from .proc import provider


class OhsomeQgis:
    """QGIS Plugin Implementation."""

    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.dialog = OhsomeQgisDialog.OhsomeQgisDialogMain(iface)
        self.provider = provider.OhsomeQgisProvider()

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        QgsApplication.processingRegistry().addProvider(self.provider)
        self.dialog.initGui()

    def unload(self):
        """remove menu entry and toolbar icons"""
        QgsApplication.processingRegistry().removeProvider(self.provider)
        self.dialog.unload()
