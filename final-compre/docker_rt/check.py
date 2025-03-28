import tensorrt as trt
import torch

print(trt.__version__)  # Should show 8.5.3
print(torch.cuda.is_available())  # Should be True
print(torch.version.cuda)  # Should show 11.8