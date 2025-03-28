import numpy as np
np.bool = bool 
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit

class TensorRTInference:
    def __init__(self, engine_path):
        self.logger = trt.Logger(trt.Logger.WARNING)
        self.engine = self.load_engine(engine_path)
        self.context = self.engine.create_execution_context()
        self.inputs, self.outputs, self.bindings, self.stream = self.allocate_buffers()

    def load_engine(self, engine_path):
        with open(engine_path, "rb") as f:
            runtime = trt.Runtime(self.logger)
            return runtime.deserialize_cuda_engine(f.read())
    
    def allocate_buffers(self):
        inputs = []
        outputs = []
        bindings = []
        stream = cuda.Stream()
        
        for binding in self.engine:
            shape = self.engine.get_binding_shape(binding)
            size = trt.volume(shape) * self.engine.max_batch_size
            dtype = trt.nptype(self.engine.get_binding_dtype(binding))
            
            # Allocate host and device buffers
            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)
            
            bindings.append(int(device_mem))
            if self.engine.binding_is_input(binding):
                inputs.append({'host': host_mem, 'device': device_mem, 'shape': shape})
            else:
                outputs.append({'host': host_mem, 'device': device_mem, 'shape': shape})
        
        return inputs, outputs, bindings, stream

    def infer(self, input_data):
        # Copy input to device
        np.copyto(self.inputs[0]['host'], input_data.ravel())
        cuda.memcpy_htod_async(
            self.inputs[0]['device'], self.inputs[0]['host'], self.stream)
        
        # Run inference
        self.context.execute_async_v2(
            bindings=self.bindings,
            stream_handle=self.stream.handle)
        
        # Copy outputs from device
        for out in self.outputs:
            cuda.memcpy_dtoh_async(
                out['host'], out['device'], self.stream)
        
        self.stream.synchronize()
        return [out['host'] for out in self.outputs]