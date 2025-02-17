# fft/final_fft/subs.py
import paho.mqtt.client as mqtt
import json
import os
from struct import unpack
from datetime import datetime
from index import process_live
# Define topics
TOPIC_RAW = "wired/rawdata/E4:65:B8:2C:D8:B0"
TOPIC_RMS = "wired/rms/E4:65:B8:2C:D8:B0"

# Directory for saving data files
DATA_DIR = "data_files"
os.makedirs(DATA_DIR, exist_ok=True)

# Global variables
sens_rawdata = {"axis_x": {}, "axis_y": {}, "axis_z": {}}
sens_rmsdata = {}
counter = 1


def construct_metadata_format_string():
    return {
        "macIdSize": 18,
        "timestampSize": 8,
        "blockSizeSize": 4,
        "samplingRateSize": 4,
        "sensitivitySize": 4,
        "axisSize": 1,
        "tempSize": 4,
        "totalMetadataSize": 43,  # Sum of all sizes
    }


def get_payload_info(data):
    metadata_info = construct_metadata_format_string()
    macId_size = metadata_info["macIdSize"]
    timestamp_size = metadata_info["timestampSize"]
    blockSize_size = metadata_info["blockSizeSize"]
    samplingRate_size = metadata_info["samplingRateSize"]
    sensitivity_size = metadata_info["sensitivitySize"]
    axis_size = metadata_info["axisSize"]
    temp_size = metadata_info["tempSize"]
    total_metadata_size = metadata_info["totalMetadataSize"]

    # Ensure the buffer size is sufficient
    if len(data) < total_metadata_size:
        raise ValueError(f"Data too short. Expected at least {total_metadata_size} bytes, got {len(data)} bytes.")

    offset = 0
    mac_id = data[offset:offset + macId_size].decode("utf-8").replace("\0", "")
    offset += macId_size

    timestamp = unpack("<d", data[offset:offset + timestamp_size])[0]
    offset += timestamp_size

    block_size = unpack("<i", data[offset:offset + blockSize_size])[0]
    offset += blockSize_size

    sampling_rate = unpack("<f", data[offset:offset + samplingRate_size])[0]
    offset += samplingRate_size

    sensitivity = unpack("<i", data[offset:offset + sensitivity_size])[0]
    offset += sensitivity_size

    axis = data[offset:offset + axis_size].decode("utf-8")
    offset += axis_size

    temp = unpack("<f", data[offset:offset + temp_size])[0]

    raw_data_format_string = f"<{block_size}h"
    raw_data = unpack(raw_data_format_string, data[total_metadata_size:])

    scaling_factors = {8: 2 ** 12, 16: 2 ** 11, 32: 2 ** 10, 64: 2 ** 9}
    scaling_factor = scaling_factors.get(sensitivity, 1)

    raw_values = [x / scaling_factor for x in raw_data]

    return {
        "raw_data": raw_values,
        "mac_id": mac_id,
        "timestamp": timestamp,
        "block_size": block_size,
        "sampling_rate": sampling_rate,
        "sensitivity": sensitivity,
        "axis": axis,
        "temp": temp,
    }


# Callback for raw data topic
def on_raw_message(client, userdata, msg):
    global sens_rawdata, counter, send_raw

    try:
        decoded_raw_data = get_payload_info(msg.payload)
        axis = decoded_raw_data["axis"]

        # Update the appropriate axis in sens_rawdata
        if axis == "X":
            sens_rawdata["axis_x"] = {**decoded_raw_data, "entry_ts": datetime.now().timestamp()}
        elif axis == "Y":
            sens_rawdata["axis_y"] = {**decoded_raw_data, "entry_ts": datetime.now().timestamp()}
        elif axis == "Z":
            sens_rawdata["axis_z"] = {**decoded_raw_data, "entry_ts": datetime.now().timestamp()}

        # Save the data to JSON
        raw_data_file = os.path.join(DATA_DIR, f"New_RawData_{counter}.json")
        with open(raw_data_file, "w") as file:
            json.dump(sens_rawdata, file, indent=2)
        send_raw = raw_data_file
        print(f"Saved raw data to {raw_data_file}")

    except Exception as e:
        print(f"Error processing raw message: {e}")


# Callback for RMS data topic
def on_rms_message(client, userdata, msg):
    global sens_rmsdata, counter

    try:
        # Parse the RMS data
        sens_rmsdata = json.loads(msg.payload.decode("utf-8"))
        plots = process_live(sens_rmsdata)
        # Save the RMS data to JSON
        rms_data_file = os.path.join(DATA_DIR, f"New_RMSData_{counter}.json")
        with open(rms_data_file, "w") as file:
            json.dump(sens_rmsdata, file, indent=2)
        print(f"Saved RMS data to {rms_data_file}")

        counter += 1

    except Exception as e:
        print(f"Error processing RMS message: {e}")


# Callback for connection to raw data topic
def on_connect(client, userdata, flags,extra, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(TOPIC_RAW)

# def on_connect(client, userdata, flags, rc):
# def on_message(client, userdata, msg):
# Callback for connection to RMS data topic
def on_rms_connect(client, userdata, flags,extra, rc):
    print(f"Connected to MQTT broker for RMS data with result code {rc}")
    client.subscribe(TOPIC_RMS)


# Initialize MQTT clients
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
rms_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_message = on_raw_message

rms_client.on_connect = on_rms_connect
rms_client.on_message = on_rms_message

# Connect to MQTT broker
BROKER = "192.168.1.213"
PORT = 1883

client.connect(BROKER, PORT, 60)
rms_client.connect(BROKER, PORT, 60)

client.loop_start()
rms_client.loop_start()

# Keep script running
try:
    while True:
        pass
except KeyboardInterrupt:
    client.loop_stop()
    rms_client.loop_stop()
    client.disconnect()
    rms_client.disconnect()
