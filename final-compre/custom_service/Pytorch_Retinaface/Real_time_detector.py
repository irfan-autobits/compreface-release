import cv2
import numpy as np
import torch
import time
import ctypes

from custom_service.Pytorch_Retinaface.data import cfg_mnet, cfg_re50
from custom_service.Pytorch_Retinaface.layers.functions.prior_box import PriorBox
from custom_service.Pytorch_Retinaface.utils.nms.py_cpu_nms import py_cpu_nms
from custom_service.Pytorch_Retinaface.utils.box_utils import decode, decode_landm
from custom_service.Pytorch_Retinaface.models.retinaface import RetinaFace

class FaceDetectorRetinaFace:
    def __init__(self, model_path="./weights/Resnet50_Final.pth", network="resnet50", confidence_threshold=0.02, nms_threshold=0.4, max_call_counter=1000, vis_thres = 0.6):
        self.model_path = model_path
        self.network = network
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.max_call_counter = max_call_counter
        self.call_counter = 0
        self.vis_thres = vis_thres

        # Load model config
        self.cfg = cfg_re50 if network == "resnet50" else cfg_mnet

        # Load model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net = RetinaFace(cfg=self.cfg, phase='test')
        self.net = self.load_model(self.net, model_path)
        self.net.eval()
        self.net.to(self.device)
        torch.set_grad_enabled(False)

        # Load libc for malloc_trim
        self.libc = ctypes.CDLL("libc.so.6")        

    def load_model(self, model, pretrained_path):
        pretrained_dict = torch.load(pretrained_path, map_location=self.device)
        if "state_dict" in pretrained_dict.keys():
            pretrained_dict = {k.replace("module.", ""): v for k, v in pretrained_dict["state_dict"].items()}
        else:
            pretrained_dict = {k.replace("module.", ""): v for k, v in pretrained_dict.items()}
        model.load_state_dict(pretrained_dict, strict=False)
        return model

    def preprocess_image(self, image):
        """Convert input image to format suitable for RetinaFace."""
        if isinstance(image, str):  # If input is an image path, load it
            image = cv2.imread(image, cv2.IMREAD_COLOR)

        img_raw = image.copy()
        img = np.float32(image)
        img -= (104, 117, 123)  # Subtract mean
        img = img.transpose(2, 0, 1)  # Convert to CHW format
        img = torch.from_numpy(img).unsqueeze(0).to(self.device)
        return img, img_raw

    def postprocess_detections(self, img_raw, loc, conf, landms, elapsed_time):
        """Process RetinaFace outputs to extract bounding boxes and landmarks."""
        im_height, im_width, _ = img_raw.shape

        scale = torch.Tensor([im_width, im_height, im_width, im_height]).to(self.device)

        # Decode boxes and landmarks
        priorbox = PriorBox(self.cfg, image_size=(im_height, im_width))
        priors = priorbox.forward().to(self.device)
        prior_data = priors.data

        boxes = decode(loc.data.squeeze(0), prior_data, self.cfg['variance'])
        boxes = (boxes * scale).cpu().numpy()
        scores = conf.squeeze(0).data.cpu().numpy()[:, 1]

        landms = decode_landm(landms.data.squeeze(0), prior_data, self.cfg['variance'])
        scale1 = torch.Tensor([im_width, im_height] * 5).to(self.device)
        landms = (landms * scale1).cpu().numpy()

        # Apply confidence threshold
        inds = np.where(scores > self.confidence_threshold)[0]
        boxes, landms, scores = boxes[inds], landms[inds], scores[inds]

        # Apply Non-Maximum Suppression (NMS)
        dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
        keep = py_cpu_nms(dets, self.nms_threshold)
        dets, landms = dets[keep, :], landms[keep]

        return dets, landms, elapsed_time

    def format_results(self, dets, landms, elapsed_time):
        """Convert detections to CompreFace-compatible format."""
        compreface_results = []
        
        for i, det in enumerate(dets):
            if det[4] < self.vis_thres:
                continue
            x1, y1, x2, y2, confidence = map(float, det[:5])  # Use float for precision
            landmarks = {
                "left_eye": [float(landms[i][0]), float(landms[i][1])],
                "right_eye": [float(landms[i][2]), float(landms[i][3])],
                "nose": [float(landms[i][4]), float(landms[i][5])],
                "right_mouth": [float(landms[i][6]), float(landms[i][7])],
                "left_mouth": [float(landms[i][8]), float(landms[i][9])],
            }

            compreface_result = {
                "age": {
                    "probability": None,  # RetinaFace does not predict age
                    "high": None,
                    "low": None
                },
                "gender": {
                    "probability": None,  # No gender prediction
                    "value": None
                },
                "mask": {
                    "probability": None,  # No mask prediction
                    "value": None
                },
                "embedding": [],  # RetinaFace does not provide embeddings
                "box": {
                    "probability": confidence,  # Confidence score
                    "x_min": int(x1),
                    "y_min": int(y1),
                    "x_max": int(x2),
                    "y_max": int(y2)
                },
                "landmarks": [
                    landmarks["left_eye"],
                    landmarks["right_eye"],
                    landmarks["nose"],
                    landmarks["right_mouth"],
                    landmarks["left_mouth"]
                ],
                "subjects": [],  # No subject similarity data from RetinaFace
                "execution_time": {
                    "age": None,
                    "gender": None,
                    "detector": elapsed_time,
                    "calculator": None,
                    "mask": None
                }
            }

            compreface_results.append(compreface_result)

        return compreface_results


    def detect(self, image):
        """Main function to detect faces."""
        self.call_counter += 1  # Increment call counter

        # Memory cleanup
        if self.call_counter % self.max_call_counter == 0:
            self.libc.malloc_trim(0)  # Force memory release
            self.call_counter = 0  # Reset counter

        img, img_raw = self.preprocess_image(image)
        im_height, im_width, _ = img_raw.shape
        print(f"retinaface frame size {im_height}, { im_width}")
        # Run detection
        with torch.no_grad():
            tic = time.time()
            loc, conf, landms = self.net(img)  # forward pass
            elapsed_time = time.time() - tic
            # print('net forward time: {:.4f}'.format(time.time() - tic))            
        dets, landms, elapsed_time = self.postprocess_detections(img_raw, loc, conf, landms, elapsed_time)
        # compreface_results = self.format_results(dets, landms, elapsed_time)
        return dets, landms, elapsed_time
        # return compreface_results
