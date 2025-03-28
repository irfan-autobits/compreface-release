from custom_service.run_tensorrt.rt_inference import TensorRTInference
from config.Paths import INSIGHT_MODELS, model_pack_name, SECRET_KEY
from custom_service.output_formatter import formatter

det_model = INSIGHT_MODELS / model_pack_name / "det_10g.trt"
rec_model = INSIGHT_MODELS / model_pack_name / "w600k_r50.trt"

# initialization with TensorRT engines
detection_trt = TensorRTInference(str(det_model))
recognition_trt = TensorRTInference(str(rec_model))