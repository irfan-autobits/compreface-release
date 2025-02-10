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
        """Convert input image to format suitable for RetinaFace with resizing."""
        if isinstance(image, str):
            image = cv2.imread(image, cv2.IMREAD_COLOR)

        img_raw_orig = image.copy()
        h_orig, w_orig = img_raw_orig.shape[:2]

        # Resize image to max dimension 640 while maintaining aspect ratio
        max_dim = max(h_orig, w_orig)
        if max_dim > 640:
            scale = 640.0 / max_dim
            h_resized = int(h_orig * scale)
            w_resized = int(w_orig * scale)
            img_raw_resized = cv2.resize(img_raw_orig, (w_resized, h_resized))
        else:
            img_raw_resized = img_raw_orig.copy()
            h_resized, w_resized = h_orig, w_orig
            scale = 1.0

        # Calculate scale factors
        scale_w = w_orig / w_resized
        scale_h = h_orig / h_resized

        # Preprocess resized image
        img = np.float32(img_raw_resized)
        img -= (104, 117, 123)
        img = img.transpose(2, 0, 1)
        img = torch.from_numpy(img).unsqueeze(0).to(self.device)

        return img, img_raw_orig, scale_w, scale_h, h_resized, w_resized

    def postprocess_detections(self, img_raw_orig, loc, conf, landms, elapsed_time, scale_w, scale_h, h_resized, w_resized):
        """Process RetinaFace outputs considering resizing."""
        im_height, im_width, _ = img_raw_orig.shape

        # Generate prior boxes for resized image dimensions
        priorbox = PriorBox(self.cfg, image_size=(h_resized, w_resized))
        priors = priorbox.forward().to(self.device)
        prior_data = priors.data

        # Decode boxes and landmarks
        boxes = decode(loc.data.squeeze(0), prior_data, self.cfg['variance'])
        landms_decoded = decode_landm(landms.data.squeeze(0), prior_data, self.cfg['variance'])

        # Scale boxes to original image dimensions
        scale_boxes = torch.tensor([scale_w, scale_h, scale_w, scale_h], device=self.device)
        boxes_scaled = boxes * scale_boxes
        boxes_np = boxes_scaled.cpu().numpy()

        # Scale landmarks to original image dimensions
        scale_landms = torch.tensor([scale_w, scale_h] * 5, device=self.device)
        landms_scaled = landms_decoded * scale_landms
        landms_np = landms_scaled.cpu().numpy()

        # Apply confidence threshold
        scores = conf.squeeze(0).data.cpu().numpy()[:, 1]
        inds = np.where(scores > self.confidence_threshold)[0]
        boxes_np = boxes_np[inds]
        landms_np = landms_np[inds]
        scores = scores[inds]

        # Apply NMS
        dets = np.hstack((boxes_np, scores[:, np.newaxis])).astype(np.float32, copy=False)
        keep = py_cpu_nms(dets, self.nms_threshold)
        dets = dets[keep, :]
        landms_np = landms_np[keep]

        return dets, landms_np, elapsed_time

    def format_results(self, dets, landms, elapsed_time):
        """Convert detections to CompreFace-compatible format."""
        compreface_results = []
        
        for i, det in enumerate(dets):
            if det[4] < self.vis_thres:
                continue
            x1, y1, x2, y2, confidence = map(float, det)
            landmarks = {
                "left_eye": [float(landms[i][0]), float(landms[i][1])],
                "right_eye": [float(landms[i][2]), float(landms[i][3])],
                "nose": [float(landms[i][4]), float(landms[i][5])],
                "right_mouth": [float(landms[i][6]), float(landms[i][7])],
                "left_mouth": [float(landms[i][8]), float(landms[i][9])],
            }

            compreface_result = {
                "age": {"probability": None, "high": None, "low": None},
                "gender": {"probability": None, "value": None},
                "mask": {"probability": None, "value": None},
                "embedding": [],
                "box": {
                    "probability": confidence,
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
                "subjects": [],
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
        """Main detection function with memory management."""
        self.call_counter += 1
        if self.call_counter % self.max_call_counter == 0:
            self.libc.malloc_trim(0)
            self.call_counter = 0

        # Preprocess with resizing
        img, img_raw_orig, scale_w, scale_h, h_resized, w_resized = self.preprocess_image(image)
        print(f"RetinaFace processing size: {h_resized}x{w_resized} (Original: {img_raw_orig.shape[0]}x{img_raw_orig.shape[1]})")

        # Run inference
        with torch.no_grad():
            tic = time.time()
            loc, conf, landms = self.net(img)
            elapsed_time = time.time() - tic

        # Postprocess and format results
        dets, landms, elapsed_time = self.postprocess_detections(
            img_raw_orig, loc, conf, landms, elapsed_time,
            scale_w, scale_h, h_resized, w_resized
        )
        return self.format_results(dets, landms, elapsed_time)