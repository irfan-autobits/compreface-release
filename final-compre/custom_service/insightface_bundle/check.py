import torch
import torchvision
import onnxruntime as ort
print("ONNX Runtime device:", ort.get_device())  # Should return "CUDA"

print("torch",torch.__version__)
print("cuda.is_available",torch.cuda.is_available())
print("torchvision",torchvision.__version__)
