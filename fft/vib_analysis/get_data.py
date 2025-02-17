import json
from pathlib import Path
# from process_rms import calc_rms
from process_rms_check import calc_rms
# from check_iso_std import calc_rms

# Load JSON data
json_path = Path("data_files/RawData.json")
with open(json_path, "r") as file:
    DecodedRawData = json.load(file)

for i in DecodedRawData:
    calc_rms(i)

# Load JSON data
json_path = Path("data_files/RMSData.json")
with open(json_path, "r") as file:
    DecodedRMSData = json.load(file)

# Extract RMS values
rms_keys = ['aRMSx', 'aRMSy', 'aRMSz', 'vRMSx', 'vRMSy', 'vRMSz']

print("Actual RMS values:")
for key in rms_keys:
    print(f"{key}: {DecodedRMSData[key]}")
