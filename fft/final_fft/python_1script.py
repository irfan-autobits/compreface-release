import paho.mqtt.client as mqtt
from struct import *
import json


def construct_metadata_format_string():
    f_string = '<'              # little endian
    f_string += 'c' * 18        # macId
    f_string += 'd'             # timestamp
    f_string += 'i'             # blockSize
    f_string += 'f'             # samplingRate
    f_string += 'i'             # sensitivity
    f_string += 'c'             # axis
    f_string += 'f'  # temp
    return f_string


def get_payload_info(data):

    macId_size = 18
    timestamp_size = 8
    blockSize_size = 4
    sampling_rate_size = 4
    sensitivity_size = 4
    axis_size = 1
    temp_size = 4
    total_metadata_size = macId_size + sensitivity_size + timestamp_size + \
        blockSize_size + sampling_rate_size + axis_size + temp_size

    scaling_factor = 1
    g = 9.8

    f_string = construct_metadata_format_string()
    metadata = data[:total_metadata_size]

    decoded_metadata = unpack(f_string, metadata)

    mac_id = "".join(x.decode('utf-8')
                        for x in decoded_metadata[0: macId_size]).rstrip('\0')
    timestamp = decoded_metadata[-6]
    block_size = decoded_metadata[-5]
    sampling_rate = decoded_metadata[-4]
    sensitivity = decoded_metadata[-3]
    axis = decoded_metadata[-2].decode('utf-8')
    temp = decoded_metadata[-1]

    raw_data_format_string = 'h' * block_size
    decoded_raw_data = unpack(
        raw_data_format_string, data[total_metadata_size:])

    if sensitivity == 8:
        scaling_factor = float(2 ** 12)
    elif sensitivity == 16:
        scaling_factor = float(2 ** 11)
    elif sensitivity == 32:
        scaling_factor = float(2 ** 10)
    elif sensitivity == 64:
        scaling_factor = float(2 ** 9)

    raw_values = list(map(float, decoded_raw_data))
    raw_values = [x / scaling_factor for x in raw_values]

    return {
        'raw_data': raw_values,
        'mac_id': mac_id,
        'timestamp': timestamp,
        'block_size': block_size,
        'sampling_rate': sampling_rate,
        'sensitivity': sensitivity,
        'axis': axis,
        'temp': temp
    }

# Define callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe to a topic when connected
    client.subscribe("wired/rawdata/E4:65:B8:2C:D8:B0")
    # wired/rms/E4:65:B8:2C:D8:B0

def on_message(client, userdata, msg):
    # Decode the payload
    DecodedRawData = get_payload_info(msg.payload)

    with open("DecodedRawData.json", "w") as file:
        # Use json.dump() to save the data into the file
        file.write(json.dumps(str(DecodedRawData)))
        
    # Print the decoded data
    print("data received", 
        DecodedRawData.get('mac_id'), DecodedRawData.get('timestamp'), DecodedRawData.get('block_size'), DecodedRawData.get('sampling_rate'),
        DecodedRawData.get('sensitivity'),  DecodedRawData.get('axis'), DecodedRawData.get('temp'), DecodedRawData.get('raw_data'))



# Create a client instance
client = mqtt.Client()

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect("192.168.1.193", 1883, 60)

# Start the MQTT loop
client.loop_start()


# Keep the program running
try:
    while True:
        pass
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
