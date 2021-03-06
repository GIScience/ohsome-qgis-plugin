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

"""
Defines exceptions that are thrown by the ohsome API client.
"""


class OhsomeBaseException(Exception):
    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return self.status
        else:
            return "{} ({})".format(self.status, self.message)


class GeometryError(OhsomeBaseException):
    """Represents an exception returned by the geometry processing tools."""

    pass


class PluginError(OhsomeBaseException):
    """Represents an exception returned by the plugin in general."""

    pass


class GenericClientError(OhsomeBaseException):
    """Represents an exception returned by the remote API."""

    pass


class GenericServerError(OhsomeBaseException):
    """Represents an exception returned by the remote API."""

    pass


class Unauthorized(OhsomeBaseException):
    """Signifies that the request failed because the client exceeded its query rate limit."""

    pass


class BadRequest(OhsomeBaseException):
    """Signifies that the request failed because the client exceeded its query rate limit."""

    pass


class NotFound(OhsomeBaseException):
    """Signifies that the request failed because the client exceeded its query rate limit."""

    pass


class MethodNotAllowed(OhsomeBaseException):
    """Signifies that the request failed because the client exceeded its query rate limit."""

    pass


class PayloadTooLarge(OhsomeBaseException):
    """Signifies that the request failed because the client exceeded its query rate limit."""

    pass


class InternalServerError(OhsomeBaseException):
    """Signifies that the request failed because the client exceeded its query rate limit."""

    pass


class NotImplemented(OhsomeBaseException):
    """Signifies that the request failed because the client exceeded its query rate limit."""

    pass


class ServiceUnavailable(OhsomeBaseException):
    """Signifies that the request failed because the client exceeded its query rate limit."""

    pass


class Timeout(OhsomeBaseException):
    """The request timed out."""

    pass


class TooManyInputsFound(OhsomeBaseException):
    """The layer selection found multiple input layers with the same name."""

    pass


class GenericServerError(OhsomeBaseException):
    """Anything else"""

    pass
