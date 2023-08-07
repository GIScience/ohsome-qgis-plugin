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
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingParameterNumber,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterDateTime)
from qgis import processing
from ohsomeTools.common import (DATA_AGGREGATION_FORMAT,
                                AGGREGATION_SPECS)
from ...gui.OhsomeToolsDialog import OhsomeToolsDialogMain
from qgis.utils import iface
from ..procDialog import run_processing_alg


class ContributionsCount(QgsProcessingAlgorithm):
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

    LAYER = 'LAYER'
    PARAMETER = 'PARAMETER'
    INPUT = 'INPUT'
    FILTER = 'FILTER'
    check_activate_temporal = 'check_activate_temporal'
    check_show_metadata = 'check_show_metadata'
    timeout_input = 'timeout_input'
    check_clip_geometry = 'check_clip_geometry'
    property_groups_check_tags = 'property_groups_check_tags'
    property_groups_check_metadata = 'property_groups_check_metadata'
    data_aggregation_format = 'data_aggregation_format'
    date_start = 'date_start'
    date_end = 'date_end'
    YEARS = 'YEARS'
    MONTHS = 'MONTHS'
    DAYS = 'DAYS'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ContributionsCount()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'dataaggregationcontributionscount'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Contributions Count')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Data Aggregation')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'dataaggregation'

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
                self.LAYER,
                self.tr('Query Layer')
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.PARAMETER,
                self.tr('Parameter'),
                options=[self.tr(i) for i in AGGREGATION_SPECS['contributions/count']],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.FILTER,
                self.tr('Filter')
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.check_activate_temporal,
                self.tr('Qgis temporal feature'),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.check_show_metadata,
                self.tr('Show metadata'),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.timeout_input,
                'Timeout',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.check_clip_geometry,
                self.tr('Clip geometry'),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.property_groups_check_tags,
                self.tr('Tags'),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.property_groups_check_metadata,
                self.tr('Metadata'),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.data_aggregation_format,
                self.tr('Format'),
                options=['json', 'geojson'],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.date_start,
                'Start Date'
            )
        )

        self.addParameter(
            QgsProcessingParameterDateTime(
                self.date_end,
                'End Date'
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.YEARS,
                'Years',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MONTHS,
                'Months',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DAYS,
                'Days',
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=1
            )
        )



    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        processingParams = {'selection':                        'Data-Extraction',
                            'preference':                       'contributions/count',
                            'filter':                           self.parameterAsString(parameters, self.FILTER, context),
                            'preference_specification':         self.parameterAsString(parameters, self.PARAMETER, context),
                            'geom':                             self.parameterAsSource(parameters, self.INPUT, context),
                            'check_activate_temporal':          self.parameterAsBool(parameters, self.check_activate_temporal, context),
                            'check_show_metadata':              self.parameterAsBool(parameters, self.check_show_metadata, context),
                            'timeout_input':                    self.parameterAsInt(parameters, self.timeout_input, context),
                            'check_clip_geometry':              self.parameterAsBool(parameters, self.check_clip_geometry, context),
                            'property_groups_check_tags':       self.parameterAsBool(parameters, self.property_groups_check_tags, context),
                            'property_groups_check_metadata':   self.parameterAsBool(parameters, self.property_groups_check_metadata, context),
                            'data_aggregation_format':          self.parameterAsString(parameters, self.data_aggregation_format, context),
                            'date_start':                       self.parameterAsDateTime(parameters, self.date_start, context),
                            'date_end':                         self.parameterAsDateTime(parameters, self.date_end, context),
                            'YEARS':                            self.parameterAsInt(parameters, self.YEARS, context),
                            'MONTHS':                           self.parameterAsInt(parameters, self.MONTHS, context),
                            'DAYS':                             self.parameterAsInt(parameters, self.DAYS, context),
                            }

        run_processing_alg(processingParams)

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
        return {self.INPUT: True}
