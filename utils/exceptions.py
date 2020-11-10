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

"""
Defines exceptions that are thrown by the OhsomePlugin client.
"""


class ApiError(Exception):
    """Represents an exception returned by the remote API."""

    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return self.status
        else:
            return "{} ({})".format(self.status, self.message)


class Timeout(Exception):
    """The request timed out."""

    pass


class GenericServerError(Exception):
    """Anything else"""

    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return self.status
        else:
            return "{} ({})".format(self.status, self.message)
