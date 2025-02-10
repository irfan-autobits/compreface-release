from typing import Tuple

# Define your environment values
GPU_IDX = 0
CUDA = '11.8'  # Use string format to avoid conversion later

def get_tensorflow(version='2.2.0') -> Tuple[str, ...]:
    return tuple([f'tensorflow=={version}'])

def get_mxnet() -> Tuple[str, ...]:
    cuda_version = CUDA.replace('.', '')  # Remove dots from CUDA version
    mxnet_lib = 'mxnet-'
    if GPU_IDX > -1 and cuda_version:
        mxnet_lib += f"cu{117 if 117 < int(cuda_version) else cuda_version}"
    else:
        mxnet_lib = 'mxnet'  # Fallback to non-GPU version
    return (f'{mxnet_lib}==1.9.1',)

req = get_mxnet()
print("req:", req)