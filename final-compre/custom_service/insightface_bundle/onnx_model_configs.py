import shutil
import onnx
from pathlib import Path
txt_path = Path("models_config")
shutil.rmtree(txt_path, ignore_errors=True)
txt_path.mkdir(parents=True, exist_ok=True)

models = [
    "1k3d68.onnx",
    "2d106det.onnx",
    "det_10g.onnx",
    "genderage.onnx",
    "w600k_r50.onnx",
]

model_dir = "/home/autobits/.insightface/models/buffalo_l"

for model in models:
    model_path = f"{model_dir}/{model}"
    output_file = f"{model}.txt"  # Save output as a text file with the same name as the model
    output_path = txt_path / output_file
    
    onnx_model = onnx.load(model_path)
    graph_text = onnx.helper.printable_graph(onnx_model.graph)
    
    with open(str(output_path), "w") as f:
        f.write(graph_text)
    
    print(f"Saved: {str(output_path)}")
