# final-compre/integrations/custom_service.py
from custom_service.main_run import cstm_ser, find_faces_post, init_model

def cutm_integ(frame):

    results = cstm_ser(frame)
    # results = find_faces_post(frame)

    return results