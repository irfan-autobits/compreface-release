# fft/final_fft/index.py
import json
from pathlib import Path
# from process_rms import calc_rms
from process_plot import calc_rms, send_to_socket
# from check_iso_std import calc_rms
# Load JSON data
# json_path = Path("data_files/RawData.json")
# with open(json_path, "r") as file:
#     DecodedRawData = json.load(file)
def process_live(DecodedRawData):
    print(f"data: {DecodedRawData}")

    formatted_res = {
        "fft": {
            "velocity": {
                "x_axis": [],
                "y_axis": [],
                "z_axis": []
            },
            "acceleration": {
                "x_axis": [],
                "y_axis": [],
                "z_axis": []
            },
            "displacement": {
                "x_axis": [],
                "y_axis": [],
                "z_axis": []
            },
            "frequency_bin": []
        },
        "rms": {
            "velocity": {
                "x_axis": [],
                "y_axis": [],
                "z_axis": []
            },
            "acceleration": {
                "x_axis": [],
                "y_axis": [],
                "z_axis": []
            }
        }
    }
    for i in DecodedRawData:
        plot_data = calc_rms(i)
        key = f"{i['axis'].lower()}_axis"
        formatted_res["fft"]["velocity"][key] = plot_data["fft"]['velocity']
        formatted_res["fft"]["acceleration"][key] = plot_data["fft"]['acceleration']
        formatted_res["fft"]["displacement"][key] = plot_data["fft"]['displacement']
        formatted_res["fft"]["frequency_bin"] = plot_data["fft"]['freq_bin']
    return formatted_res


# Load JSON data
json_path = Path("data_files/RMSData.json")
with open(json_path, "r") as file:
    DecodedRMSData = json.load(file)

# Extract RMS values
rms_keys = {
    'aRMSx': 'acceleration.x_axis',
    'aRMSy': 'acceleration.y_axis',
    'aRMSz': 'acceleration.z_axis',
    'vRMSx': 'velocity.x_axis',
    'vRMSy': 'velocity.y_axis',
    'vRMSz': 'velocity.z_axis'
}

for key, path in rms_keys.items():
    axis = path.split('.')
    formatted_res['rms'][axis[0]][axis[1]] = DecodedRMSData[key]

with open("socket_sent.json", "w") as file:
    # Use json.dump() to save the data into the file
    file.write(json.dumps(formatted_res))
send_to_socket(formatted_res)

print("Actual RMS values:")
for key in rms_keys:
    print(f"{key}: {DecodedRMSData[key]}")
