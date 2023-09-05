from ohsomeTools.common import client
from ohsomeTools.utils import exceptions, logger, configmanager
from qgis.utils import iface
from ohsomeTools.gui import ohsome_spec

from .procRequest import processing_request


def run_processing_alg(processingParams, feedback):

    # Clean the debug text
    try:
        provider_id = processingParams[
            "provider"
        ]
        provider = configmanager.read_config()["providers"][provider_id]
    except IndexError:
        msg = "Request aborted. No provider available. Please check your provider list.\n"
        logger.log(msg, 1)
        feedback.reportError(msg)
        return

    clnt = client.ProcessingClient(provider, feedback=feedback)

    metadata_check = clnt.check_api_metadata(iface)

    # get preferences from dialog
    preferences = ohsome_spec.ProcessingOhsomeSpec(
        params=processingParams, feedback=feedback
    )

    try:
        if not metadata_check or not preferences.is_valid(False):
            msg = "The request has been aborted!"
            feedback.reportError(msg)
            return

        # if there are no centroids or layers, throw an error message
        geom = processingParams["geom"]
        if processingParams["selection"] == "metadata":
            processing_request(clnt, preferences, feedback, processingParams)

        elif geom == 1:
            layer_preferences = (
                preferences.get_point_layer_request_preferences()
            )
            if not len(layer_preferences):
                return

            for point_layer_preference in layer_preferences:

                processing_request(
                    clnt,
                    preferences,
                    processingParams,
                    feedback,
                    point_layer_preference,
                )

        elif geom == 2:
            layer_preferences = (
                preferences.get_polygon_layer_request_preferences()
            )
            for polygon_layer_preference in layer_preferences:
                processing_request(
                    clnt,
                    preferences,
                    processingParams,
                    feedback,
                    polygon_layer_preference,
                )
        else:
            return

    except exceptions.TooManyInputsFound as e:
        msg = [e.__class__.__name__, str(e)]
        feedback.reportError("{}: {}".format(*msg))
        feedback.reportError("Request aborted. Layer input name is not unique.")
    except Exception as e:
        msg = [e.__class__.__name__, str(e)]
        feedback.reportError("{}: {}".format(*msg))
        feedback.reportError("Request aborted. Check the tool log.")
    finally:
        if not metadata_check:
            return True
        elif not preferences.is_valid(True):
            feedback.reportError(
                "Preferences are not valid. Check the plugin log."
            )
            return
