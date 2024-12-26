// Initialize CompreFace
compre_face = CompreFace(host, port, {
    "limit": 0,                                                     // maximum number of faces on the image to be recognized. It recognizes the biggest faces first. 0 = no limit
    "det_prob_threshold": 0.8,                                      // Minimum detection probability threshold for face detection
    "prediction_count": 3,                                          // Number of predictions per face
    "face_plugins": "calculator,age,gender,landmarks,mask",    // "calculator = embedding,age,gender,landmarks,mask", 
    "status": True                                                  // system information like execution_time and plugin_version fields
})

[
  {
    "age": { "probability": 0.9740532636642456, "high": 32, "low": 25 },  //age
    "gender": { "probability": 0.9999998807907104, "value": "female" },  //gender
    "embedding": [  0.0787976086139679, "...", -0.11665412038564682      //calculator
    ],
    "box": {
      "probability": 0.99051,                                            //det_prob_threshold
      "x_max": 594,
      "y_max": 144,
      "x_min": 561,
      "y_min": 112
    },
    "mask": { "probability": 0.9996697902679443, "value": "without_mask" }, //mask
    "subjects": [                                                           //prediction_count
      { "subject": "darsan", "similarity": 0.64482 },
      { "subject": "sagar-sir", "similarity": 0.5918 },
      { "subject": "dev", "similarity": 0.37517 }
    ],
    "landmarks": [                                                        //landmarks
      [577, 124],
      [588, 126],
      [583, 132],
      [574, 135],
      [583, 136]
    ],
    "execution_time": {                                                    //status
      "age": 41.0,
      "gender": 26.0,
      "detector": 123.0,
      "calculator": 54.0,
      "mask": 40.0
    }
  }
]

// ======================= TEST ========================== // 
test=
{
  "result" : 
    [ 
      {
        "age" : {
          "probability": 0.9308982491493225,
          "high": 32,
          "low": 25
        },
        "gender" : {
          "probability": 0.9898611307144165,
          "value": "female"
        },
        "mask" : {
          "probability": 0.9999470710754395,
          "value": "without_mask"
        },
        "embedding" : [ 9.424854069948196E-4, "...", -0.011415496468544006 ],
        "box" : {
          "probability" : 1.0,
          "x_max" : 1420,
          "y_max" : 1368,
          "x_min" : 548,
          "y_min" : 295
        },
        "landmarks" : [ [ 814, 713 ], [ 1104, 829 ], [ 832, 937 ], [ 704, 1030 ], [ 1017, 1133 ] ],
        "subjects" : [ {
          "similarity" : 0.97858,
          "subject" : "subject1"
        } ],
        "execution_time" : {
          "age" : 28.0,
          "gender" : 26.0,
          "detector" : 117.0,
          "calculator" : 45.0,
          "mask": 36.0
        }
      } 
    ]
,
  "plugins_versions" : {
    "age" : "agegender.AgeDetector",
    "gender" : "agegender.GenderDetector",
    "detector" : "facenet.FaceDetector",
    "calculator" : "facenet.Calculator",
    "mask": "facemask.MaskDetector"
  }
}