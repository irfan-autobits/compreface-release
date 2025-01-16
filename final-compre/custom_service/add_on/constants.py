import logging

from custom_service.pyutils import get_env, get_env_split, get_env_bool, Constants

class ENV(Constants):
    ML_PORT = int(get_env('ML_PORT', '3000'))

    FACE_DETECTION_PLUGIN = get_env('FACE_DETECTION_PLUGIN', 'facenet.FaceDetector')
    CALCULATION_PLUGIN = get_env('CALCULATION_PLUGIN', 'facenet.Calculator')
    EXTRA_PLUGINS = get_env_split('EXTRA_PLUGINS', 'facenet.LandmarksDetector,agegender.AgeDetector,agegender.GenderDetector,facenet.facemask.MaskDetector,facenet.PoseEstimator')

    LOGGING_LEVEL_NAME = get_env('LOGGING_LEVEL_NAME', 'debug').upper()
    IS_DEV_ENV = get_env('FLASK_ENV', 'production') == 'development'
    BUILD_VERSION = get_env('APP_VERSION_STRING', 'dev')

    INTEL_OPTIMIZATION = get_env_bool('INTEL_OPTIMIZATION')

LOGGING_LEVEL = logging._nameToLevel[ENV.LOGGING_LEVEL_NAME]
ENV_MAIN = ENV
SKIPPED_PLUGINS = ["insightface.PoseEstimator", "facemask.MaskDetector", "facenet.PoseEstimator"]
