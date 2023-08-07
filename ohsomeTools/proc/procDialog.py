from ohsomeTools.utils import (
    exceptions,
    maptools,
    logger,
    configmanager,
    transform,
)

from qgis._core import (
    Qgis,
    QgsTask,
    QgsApplication,
)

from ohsomeTools.common import (
    client,
    request_core,
    API_ENDPOINTS,
    EXTRACTION_SPECS,
    AGGREGATION_SPECS,
    DATA_AGGREGATION_FORMAT,
)

from qgis.utils import iface

from ohsomeTools.gui import ohsome_spec

import string
import random

from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QApplication,
    QMenu,
    QMessageBox,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
)

from ..common.request_core import ExtractionTaskFunction, processingExtractionTaskFunction

def run_processing_alg(processingParams):

    # Clean the debug text
    try:
        provider_id = 'https://api.ohsome.org/v1'
        provider = configmanager.read_config()["providers"][provider_id]
    except IndexError:
        msg = "Request aborted. No provider available. Please check your provider list.\n"
        logger.log(msg, 1)
        iface.messageBar().pushMessage(
            "Warning",
            msg,
            level=Qgis.Warning,
            duration=5,
        )
        return

    clnt = client.Client(provider)

    metadata_check = clnt.check_api_metadata(iface)

    # get preferences from dialog
    preferences = ohsome_spec.ProcessingOhsomeSpec(params=processingParams)
    try:
        letters = string.ascii_lowercase
        task_name = "".join(random.choice(letters) for i in range(10))
        if not metadata_check or not preferences.is_valid(False):
            msg = "The request has been aborted!"
            logger.log(msg, 0)
            return

        # if there are no centroids or layers, throw an error message
        geom = processingParams['geom']
        print(geom)
        if (
                processingParams['selection']
                == "metadata"
        ):
            globals()[task_name] = processingExtractionTaskFunction(
                iface=iface,
                description=f"OHSOME task",
                provider=provider,
                request_url=preferences.get_request_url(),
                preferences=None,
            )
            QgsApplication.taskManager().addTask(globals()[task_name])
        elif geom == 0: # geometry type of input layer
            globals()[task_name] = processingExtractionTaskFunction(
                iface=iface,
                processingParams=processingParams,
                description=f"OHSOME task",
                provider=provider,
                request_url=preferences.get_request_url(),
                preferences=preferences.get_bcircles_request_preferences(),
                activate_temporal=preferences.activate_temporal_feature,
            )
            QgsApplication.taskManager().addTask(globals()[task_name])
        elif geom == 1:
            layer_preferences = (
                preferences.get_point_layer_request_preferences()
            )
            if not len(layer_preferences):
                return
            last_task = None
            for point_layer_preference in layer_preferences:
                task = ExtractionTaskFunction(
                    iface=iface,
                    processingParams=processingParams,
                    description=f"OHSOME task",
                    provider=provider,
                    request_url=preferences.get_request_url(),
                    preferences=point_layer_preference,
                    activate_temporal=preferences.activate_temporal_feature,
                )
                if last_task and last_task != globals()[task_name]:
                    # Never add the main task as a dependency!
                    globals()[task_name].addSubTask(
                        task,
                        [last_task],
                        QgsTask.ParentDependsOnSubTask,
                    )
                elif last_task:
                    globals()[task_name].addSubTask(
                        task, [], QgsTask.ParentDependsOnSubTask
                    )
                else:
                    globals()[task_name] = task
                last_task = task
            QgsApplication.taskManager().addTask(globals()[task_name])
        elif geom == 2:

            layer_preferences = (
                preferences.get_polygon_layer_request_preferences()
            )
            last_task = None
            for point_layer_preference in layer_preferences:
                task = processingExtractionTaskFunction(
                    iface=iface,
                    processingParams=processingParams,
                    description=f"OHSOME task",
                    provider=provider,
                    request_url=preferences.get_request_url(),
                    preferences=point_layer_preference,
                    activate_temporal=preferences.activate_temporal_feature,
                )
                if last_task and last_task != globals()[task_name]:
                    # Never add the main task as a dependency!
                    globals()[task_name].addSubTask(
                        task,
                        [last_task],
                        QgsTask.ParentDependsOnSubTask,
                    )
                elif last_task:
                    globals()[task_name].addSubTask(
                        task, [], QgsTask.ParentDependsOnSubTask
                    )
                else:
                    globals()[task_name] = task
                last_task = task
            QgsApplication.taskManager().addTask(globals()[task_name])

        else:
            return
    except exceptions.TooManyInputsFound as e:
        msg = [e.__class__.__name__, str(e)]
        logger.log("{}: {}".format(*msg), 2)
        iface.messageBar().pushMessage(
            "Error",
            "Request aborted. Layer input name is not unique.",
            level=Qgis.Critical,
            duration=5,
        )
    except Exception as e:
        msg = [e.__class__.__name__, str(e)]
        logger.log("{}: {}".format(*msg), 2)
        iface.messageBar().pushMessage(
            "Error",
            "Request aborted. Check the tool log.",
            level=Qgis.Critical,
            duration=5,
        )
    finally:
        if not metadata_check:
            return
        elif not preferences.is_valid(True):
            iface.messageBar().pushMessage(
                "Warning",
                "Preferences are not valid. Check the plugin log.",
                level=Qgis.Critical,
                duration=7,
            )
            return