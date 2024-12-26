# final-compre/config/logger_config.py
import logging
from config.Paths import DET_LOG_FILE_PATH, CAM_STAT_LOG_FILE_PATH

# File paths for different log files
det_log_path = DET_LOG_FILE_PATH
cam_stat_log_path = CAM_STAT_LOG_FILE_PATH

# Function to configure a logger for detection logs
def create_detection_logger():
    det_logger = logging.getLogger('detection_logger')
    det_logger.setLevel(logging.DEBUG)

    # File handler for detection logs
    det_file_handler = logging.FileHandler(str(det_log_path))
    det_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    det_logger.addHandler(det_file_handler)

    # Optionally, add console logging for detection logs
    det_console_handler = logging.StreamHandler()
    det_console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # det_logger.addHandler(det_console_handler)

    return det_logger


# Function to configure a logger for other logs
def create_cam_stat_logger():
    cam_stat_logger = logging.getLogger('cam_stat_logger')
    cam_stat_logger.setLevel(logging.DEBUG)

    # File handler for other logs
    cam_stat_file_handler = logging.FileHandler(str(cam_stat_log_path))
    cam_stat_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    cam_stat_logger.addHandler(cam_stat_file_handler)

    # Optionally, add console logging for other logs
    cam_stat_console_handler = logging.StreamHandler()
    cam_stat_console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # cam_stat_logger.addHandler(cam_stat_console_handler)

    return cam_stat_logger

# Function to configure a logger for other logs
def create_console_logger():
    console_logger = logging.getLogger('console_logger')
    console_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    console_logger.addHandler(console_handler)

    return console_logger


# Create and configure loggers
det_logger = create_detection_logger()
cam_stat_logger = create_cam_stat_logger()
console_logger = create_console_logger()

# Example log messages
# logging.debug('This is a debug message.')
# logging.info('This is an info message.')
# logging.warning('This is a warning message.')
# logging.error('This is an error message.')
# logging.critical('This is a critical message.')