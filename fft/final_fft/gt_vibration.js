const mqtt = require("mqtt");
const fs = require("fs");
const topic_rms = "wired/rms/E4:65:B8:2C:D8:B0";
const topic = "wired/rawdata/E4:65:B8:2C:D8:B0";

// Helper function to construct the metadata format
function constructMetadataFormatString() {
  return {
    macIdSize: 18,
    timestampSize: 8,
    blockSizeSize: 4,
    samplingRateSize: 4,
    sensitivitySize: 4,
    axisSize: 1,
    tempSize: 4,
    totalMetadataSize: 43, // Sum of all sizes
  };
}

// Function to extract payload info
function getPayloadInfo(data) {
  const metadataInfo = constructMetadataFormatString();
  const {
    macIdSize,
    timestampSize,
    blockSizeSize,
    samplingRateSize,
    sensitivitySize,
    axisSize,
    tempSize,
    totalMetadataSize,
  } = metadataInfo;

  const metadata = data.slice(0, totalMetadataSize);

  if (data.length < totalMetadataSize) {
    throw new RangeError(
      `Buffer too short. Expected at least ${totalMetadataSize} bytes, got ${data.length}.`
    );
  }

  let offset = 0;

  const macId = metadata
    .slice(offset, offset + macIdSize)
    .toString("utf-8")
    .replace(/\0/g, "");
  offset += macIdSize;

  const timestamp = metadata.readDoubleLE(offset);
  offset += timestampSize;

  const blockSize = metadata.readInt32LE(offset);
  offset += blockSizeSize;

  const samplingRate = metadata.readFloatLE(offset);
  offset += samplingRateSize;

  const sensitivity = metadata.readInt32LE(offset);
  offset += sensitivitySize;

  const axis = metadata.slice(offset, offset + axisSize).toString("utf-8");
  offset += axisSize;

  const temp = metadata.readFloatLE(offset);

  const raw_data = [];
  const scalingFactors = {
    8: 2 ** 12,
    16: 2 ** 11,
    32: 2 ** 10,
    64: 2 ** 9,
  };

  const scalingFactor = scalingFactors[sensitivity] || 1;
  const rawDataFormat = data.slice(totalMetadataSize);

  for (let i = 0; i < blockSize; i++) {
    const rawValue = rawDataFormat.readInt16LE(i * 2);
    raw_data.push(rawValue / scalingFactor);
  }

  return {
    raw_data,
    mac_id: macId,
    timestamp,
    block_size: blockSize,
    sampling_rate: samplingRate,
    sensitivity,
    axis,
    temp,
  };
}

// MQTT Callback functions
function onConnect() {
  console.log("Connected to MQTT broker");
  client.subscribe(topic, (err) => {
    if (err) {
      console.error("Failed to subscribe to topic:", err.message);
    } else {
      console.log("Subscribed to topic: " + topic);
    }
  });
}

const path = require("path");

// Directory path for both data types
const dataDir = path.join(__dirname, "data_files");

// Create directory if it doesn't exist
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir);
}

let sens_rawdata = {
  axis_x: {},
  axis_y: {},
  axis_z: {},
};
let sens_rmsdata = {};
let counter = 1;

function onMessage(topic, message) {
  let sensorData = message;
  console.log(sensorData);
  const decodedRawData = getPayloadInfo(message);
  
  // Write to JSON files inside the single data directory
  sens_rawdata.push(decodedRawData);
  if(decodedRawData.axis && decodedRawData.axis === "X") {
    sens_rawdata.axis_x = decodedRawData;
    sens_rawdata.axis_x["entry_ts"] = new Date().getTime();
  } else if(decodedRawData.axis && decodedRawData.axis === "Y") {
    sens_rawdata.axis_y = decodedRawData;
    sens_rawdata.axis_y["entry_ts"] = new Date().getTime();
  } else if(decodedRawData.axis && decodedRawData.axis === "Z") {
    sens_rawdata.axis_z = decodedRawData;
    sens_rawdata.axis_z["entry_ts"] = new Date().getTime();
  }
  fs.writeFileSync(
    path.join(dataDir, `RawData_${counter}.json`),
    JSON.stringify(sens_rawdata, null, 2)
  );
  
  fs.writeFileSync(
    path.join(dataDir, `RMSData_${counter}.json`),
    JSON.stringify(sens_rmsdata, null, 2)
  );
  counter++;
}

// MQTT Callback functions
function onRMSConnect() {
  console.log("Connected to MQTT broker");
  rmsclient.subscribe(topic_rms, (err) => {
    if (err) {
      console.error("Failed to subscribe to topic:", err.message);
    } else {
      console.log("Subscribed to topic: " + topic_rms);
    }
  });
}

function onRMSMessage(topic, message) {
  console.log(JSON.parse(message), "counter : ", counter);
  sens_rmsdata = JSON.parse(message);
}

// Create MQTT client and set callbacks
const client = mqtt.connect("mqtt://192.168.1.193:1883");
console.log("started getting connected!!!!");

client.on("connect", onConnect);
client.on("message", onMessage);

const rmsclient = mqtt.connect("mqtt://192.168.1.193:1883");
console.log("started getting connected!!!!");

rmsclient.on("connect", onRMSConnect);
rmsclient.on("message", onRMSMessage);

// // Keep the script running
// process.on("SIGINT", () => {
//   client.end();
//   console.log("Disconnected from MQTT broker");
// });
