import traceback
from flask import jsonify
import numpy as np
from config.Paths import MODELS_DIR
from config.logger_config import cam_stat_logger , console_logger, exec_time_logger, det_logger
# from custom_service.insightface_bundle.real_time_buffalo import run_buffalo
# from custom_service.run_tensorrt.real_time_trt import run_trtbuffalo

# def insightface_buffalo(frame):
    # try:
    #     compreface_results = run_buffalo(frame)
    # except Exception as e:
    #     print(e)
    #     traceback.print_exc() 

    #     compreface_results = []   
    # return compreface_results

# def tensorrt_buffalo(frame):
#     try:
#         compreface_results = run_trtbuffalo(frame)
#     except Exception as e:
#         print(e)
#         traceback.print_exc() 

#         compreface_results = []   
#     return compreface_results    