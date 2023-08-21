# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessingParameterNumber,
    QgsProcessingAlgorithm,
    QgsProcessingParameterEnum,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDateTime,
    QgsWkbTypes,
)

from ohsomeTools.common import AGGREGATION_SPECS
from .procDialog import run_processing_alg
from qgis.utils import iface


class ElementsAggregation(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    LAYER = "LAYER"
    PARAMETER = "PARAMETER"
    INPUT = "INPUT"
    FILTER = "FILTER"
    check_activate_temporal = "check_activate_temporal"
    check_show_metadata = "check_show_metadata"
    timeout_input = "timeout_input"
    check_clip_geometry = "check_clip_geometry"
    property_groups_check_tags = "property_groups_check_tags"
    property_groups_check_metadata = "property_groups_check_metadata"
    data_aggregation_format = "data_aggregation_format"
    date_start = "date_start"
    date_end = "date_end"
    YEARS = "YEARS"
    MONTHS = "MONTHS"
    DAYS = "DAYS"
    RADIUS = "RADIUS"
    GROUPBY = 'GROUPBY'
    check_keep_geometryless = "check_keep_geometryless"
    check_merge_geometries = "check_merge_geometries"
    group_by_values_line_edit = "group_by_values_line_edit"
    group_by_key_line_edit = "group_by_key_line_edit"
    formats = ["json", "geojson"]
    parameters = [i.split('/')[1] for i in AGGREGATION_SPECS.keys() if 'elements' in i]
    group_by = ['', '/boundary', '/key', '/tag', '/type', '/boundary/groupBy/tag']
    DENSITY = 'DENSITY'
    PERIOD = 'PERIOD'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return ElementsAggregation()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "elementsaggregation"

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr("Elements Aggregation")

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr("Data Aggregation")

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "dataaggregation"

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it.
        """
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.LAYER, self.tr("Query Layer")
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.PARAMETER,
                self.tr("Aggregation Type"),
                options=self.parameters,
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DENSITY,
                self.tr("Density"),
                defaultValue=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.date_start, "Start Date", defaultValue="2007-10-08"
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.date_end, "End Date", defaultValue="2023-07-28"
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.FILTER,
                self.tr("Filter"),
                defaultValue="building=* or (type:way and highway=residential)",
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.RADIUS,
                "Radius [m]",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=100,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.GROUPBY,
                self.tr("Group By"),
                options=self.group_by,
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.timeout_input,
                "Timeout",
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PERIOD,
                "Period (ISO 8601)",
                defaultValue='/P'
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.data_aggregation_format,
                self.tr("Output Format"),
                options=self.formats,
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.group_by_values_line_edit,
                self.tr("Group by Values"),
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.group_by_key_line_edit,
                self.tr("Group by Key"),
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.property_groups_check_metadata,
                self.tr("Metadata"),
                defaultValue=False,
            )
        )

        # Qgis internal
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.check_show_metadata,
                self.tr("Show metadata"),
                defaultValue=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.check_keep_geometryless,
                self.tr("Keep without geometry"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.check_merge_geometries,
                self.tr("Harmonize geometries"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.check_activate_temporal,
                self.tr("Qgis temporal feature"),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.check_clip_geometry,
                self.tr("Clip geometry"),
                defaultValue=True,
            )
        ),
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.property_groups_check_tags,
                self.tr("Tags"),
                defaultValue=True,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        layer = self.parameterAsLayer(parameters, self.LAYER, context)

        if layer.geometryType() == QgsWkbTypes.PointGeometry:
            geom = 1
        elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:
            geom = 2
        else:
            # implement user information
            pass

        if self.parameterAsBool(parameters, self.DENSITY, context):
            density = '/density'
        else:
            density = ''

        preference = self.parameters[self.parameterAsInt(parameters, self.PARAMETER, context)]
        groupBy = self.group_by[self.parameterAsInt(parameters, self.GROUPBY, context)]

        processingParams = {
            "geom": geom,
            "selection": "data-Aggregation",
            "preference": f"elements/{preference}{density}",
            "preference_specification": groupBy,
            "filter": self.parameterAsString(parameters, self.FILTER, context),
            "LAYER": self.parameterAsLayer(parameters, self.LAYER, context),
            "RADIUS": self.parameterAsInt(parameters, self.RADIUS, context),
            "date_start": self.parameterAsDateTime(
                parameters, self.date_start, context
            ),
            "date_end": self.parameterAsDateTime(
                parameters, self.date_end, context
            ),
            "timeout_input": self.parameterAsInt(
                parameters, self.timeout_input, context
            ),
            'preference_specification': '',
            'data_aggregation_format': 'json',
            "check_show_metadata": self.parameterAsBool(
                parameters, self.check_show_metadata, context
            ),
            'timeout_input': self.parameterAsInt(parameters, self.timeout_input, context),
            'period': self.parameterAsString(
            parameters, self.PERIOD, context
            ),
            "data_aggregation_format": self.formats[
                self.parameterAsInt(
                    parameters, self.data_aggregation_format, context
                )
            ],
            "check_clip_geometry": self.parameterAsBool(
                parameters, self.check_clip_geometry, context
            ),
            "property_groups_check_metadata": self.parameterAsBool(
                parameters, self.property_groups_check_metadata, context
            ),
            "group_by_values_line_edit": self.parameterAsString(
                parameters, self.group_by_values_line_edit, context
            ),
            "group_by_key_line_edit": self.parameterAsString(
                parameters, self.group_by_key_line_edit, context
            ),

        }

        run_processing_alg(processingParams, feedback)

        # To run another Processing algorithm as part of this algorithm, you can use
        # processing.run(...). Make sure you pass the current context and feedback
        # to processing.run to ensure that all temporary layer outputs are available
        # to the executed algorithm, and that the executed algorithm can send feedback
        # reports to the user (and correctly handle cancellation and progress reports!)

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {}
