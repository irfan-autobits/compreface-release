import torch
import torch.nn as nn
from torchvision import transforms
import cv2
import numpy as np
from insightface.utils import face_align

class ArcFacePyTorch(nn.Module):
    """PyTorch implementation of ArcFace model"""
    def __init__(self, backbone_net):
        super().__init__()
        self.backbone = backbone_net
        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.backbone(x)
        return x

class Calculator(InsightFaceMixin, mixins.CalculatorMixin, base.BasePlugin):
    ml_models = (
        # (model_name, model_id, (mean, std), input_size)
        ('arcface_mobilefacenet', '1ltcJChTdP1yQWF9e1ESpTNYAVwxLSNLP', (1.22507105, 7.321198934), 112),
        # Add other models with their parameters
    )

    def calc_embedding(self, face_img: Array3D) -> Array3D:
        # Convert to RGB if needed
        if face_img.shape[2] == 3:
            rgb_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        else:
            rgb_img = face_img
            
        # Preprocess image
        input_tensor = self._preprocess(rgb_img)
        
        # Move to GPU if available
        if torch.cuda.is_available():
            input_tensor = input_tensor.to(f'cuda:{self._CTX_ID}')
        
        # Run inference
        with torch.no_grad():
            embedding = self._calculation_model(input_tensor)
        
        return embedding.cpu().numpy().flatten()

    @cached_property
    def _calculation_model(self):
        # Load PyTorch model architecture and weights
        model = self._load_pytorch_model()
        model.eval()
        
        # Move to GPU if available
        if torch.cuda.is_available():
            model = model.to(f'cuda:{self._CTX_ID}')
        
        return model

    def _preprocess(self, img: np.ndarray) -> torch.Tensor:
        """Preprocess image to match original model's normalization"""
        # Convert to tensor and normalize
        mean, std = self.ml_model[2]
        preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[mean], std=[std])
        ])
        return preprocess(img).unsqueeze(0)  # Add batch dimension

    def _load_pytorch_model(self):
        """Load converted PyTorch weights for ArcFace model"""
        # Example for mobilefacenet
        from models import MobileFaceNet  # Assume you have a PyTorch MobileFaceNet implementation
        
        # Initialize model
        backbone = MobileFaceNet()
        model = ArcFacePyTorch(backbone)
        
        # Load converted weights
        model_path = self.get_converted_model_path()
        model.load_state_dict(torch.load(model_path))
        
        return model

    def get_converted_model_path(self):
        """Return path to converted PyTorch weights"""
        # Implement model weight conversion logic here
        # You'll need to convert original MXNet weights to PyTorch format
        return "converted_weights.pth"

# Example MobileFaceNet implementation
class MobileFaceNet(nn.Module):
    def __init__(self):
        super().__init__()
        # Add actual MobileFaceNet architecture layers here
        self.features = nn.Sequential(
            # Example layers - replace with actual architecture
            nn.Conv2d(3, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.PReLU(64),
            # ... rest of the layers
        )
        
    def forward(self, x):
        return self.features(x)