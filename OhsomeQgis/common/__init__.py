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

API_ENDPOINTS = [
    "Data-Extraction",
    "Data-Aggregation",
    "Metadata",
]

SUPPORTED_API_VERSIONS = ["1.4.1"]
EXTRACTION_SPECS = {
    "contributions": [
        "bbox",
        "centroid",
        "geometry",
        "latest/bbox",
        "latest/centroid",
        "latest/geometry",
    ],
    "elements": ["bbox", "centroid", "geometry"],
    "elementsFullHistory": ["bbox", "centroid", "geometry"],
}
AGGREGATION_SPECS = {
    "contributions/count": ["density"],
    "elements/area": [
        "density",
        "density/groupBy/boundary",
        "density/groupBy/boundary/groupBy/tag",
        "density/groupBy/tag",
        "density/groupBy/type",
        "groupBy/boundary",
        "groupBy/boundary/groupBy/tag",
        "groupBy/key",
        "groupBy/tag",
        "groupBy/type",
        "ratio",
        "ratio/groupBy/boundary",
    ],
    "elements/count": [
        "density",
        "density/groupBy/boundary",
        "density/groupBy/boundary/groupBy/tag",
        "density/groupBy/tag",
        "density/groupBy/type",
        "groupBy/boundary",
        "groupBy/boundary/groupBy/tag",
        "groupBy/key",
        "groupBy/tag",
        "groupBy/type",
        "ratio",
        "ratio/groupBy/boundary",
    ],
    "elements/length": [
        "density",
        "density/groupBy/boundary",
        "density/groupBy/boundary/groupBy/tag",
        "density/groupBy/tag",
        "density/groupBy/type",
        "groupBy/boundary",
        "groupBy/boundary/groupBy/tag",
        "groupBy/key",
        "groupBy/tag",
        "groupBy/type",
        "ratio",
        "ratio/groupBy/boundary",
    ],
    "elements/perimeter": [
        "density",
        "density/groupBy/boundary",
        "density/groupBy/boundary/groupBy/tag",
        "density/groupBy/tag",
        "density/groupBy/type",
        "groupBy/boundary",
        "groupBy/boundary/groupBy/tag",
        "groupBy/key",
        "groupBy/tag",
        "groupBy/type",
        "ratio",
        "ratio/groupBy/boundary",
    ],
    "users/count": [
        "density",
        "density/groupBy/boundary",
        "density/groupBy/tag",
        "density/groupBy/type",
        "groupBy/boundary",
        "groupBy/key",
        "groupBy/tag",
        "groupBy/type",
    ],
}
DATA_AGGREGATION_FORMAT = {
    "groupBy/boundary": [
        "geojson",
        "json",
        # Csv not needed for now as (geo)json is enough so far.
        # "csv",
    ],
    "default": [
        "json",
        # Csv not needed for now as (geo)json is enough so far.
        # "csv",
    ],
}
