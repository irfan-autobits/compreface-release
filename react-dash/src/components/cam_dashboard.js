import React, { Fragment, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import CameraFeed from "./camera_feed";
import {
  AddNew,
  CloseSvg,
  PauseButton,
  PlayButton,
  RemoveSVG,
} from "../assets/svgs";
import { io } from "socket.io-client";

const Dashboard = () => {
  const navigate = useNavigate();
  const [camera_name, setCameraName] = React.useState("");
  const [camEnabled, setcamEnabled] = useState({});

  const handle_add_Submit = (camera_name, camera_url) => {
    if (camera_name && camera_url) {
      console.log("camera details are:", { camera_name, camera_url });
      fetch("/api/add_camera", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          camera_name: camera_name,
          camera_url: camera_url,
        }),
      })
        .then(async (response) => {
          const responseData = await response.json(); // Parse JSON response
          if (!response.ok) {
            // Handle HTTP error responses
            throw new Error(responseData.error || "Something went wrong");
          }
          return responseData; // Successful response
        })
        .then((data) => {
          console.log("camera added:", data);
          getCamerasList();
        })
        .catch((error) => {
          console.error("Error adding camera:", error);
        });
    } else {
      alert("Please fill in all fields");
    }
  };

  const handle_remove_Submit = (camera_name) => {
    if (camera_name) {
      console.log("camera details are:", { camera_name });
      fetch("/api/remove_camera", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ camera_name: camera_name }),
      })
        .then(async (response) => {
          const responseData = await response.json(); // Parse JSON response
          if (!response.ok) {
            // Handle HTTP error responses
            throw new Error(responseData.error || "Something went wrong");
          }
          return responseData; // Successful response
        })
        .then((data) => {
          console.log("camera removed:", data);
          getCamerasList();
        })
        .catch((error) => {
          console.error("Error removing camera:", error);
        });
    } else {
      alert("Please fill in all fields");
    }
  };

  const handle_start_Submit = (camera_name) => {
    if (camera_name) {
      console.log("camera details are:", { camera_name });
      fetch("/api/start_feed", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ camera_name: camera_name }),
      })
        .then(async (response) => {
          const responseData = await response.json(); // Parse JSON response
          if (!response.ok) {
            // Handle HTTP error responses
            throw new Error(responseData.error || "Something went wrong");
          }
          return responseData; // Successful response
        })
        .then((data) => {
          console.log("camera started:", data);
        })
        .catch((error) => {
          console.error("Error starting camera:", error);
        });
    } else {
      alert("Please fill in all fields");
    }
  };

  const handle_stop_Submit = (camera_name) => {
    if (camera_name) {
      console.log("camera details are:", { camera_name });
      fetch("/api/stop_feed", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ camera_name: camera_name }),
      })
        .then(async (response) => {
          const responseData = await response.json(); // Parse JSON response
          if (!response.ok) {
            // Handle HTTP error responses
            throw new Error(responseData.error || "Something went wrong");
          }
          return responseData; // Successful response
        })
        .then((data) => {
          console.log("camera stopped:", data);
        })
        .catch((error) => {
          console.error("Error stopping camera:", error);
        });
    } else {
      alert("Please fill in all fields");
    }
  };
  const [cameraList, setcameraList] = useState([]);

  function getCamerasList () {
    fetch("/api/camera_list", {
      method: "GET"
    })
      .then(async (response) => {
        const responseData = await response.json(); // Parse JSON response
        if (!response.ok) {
          // Handle HTTP error responses
          throw new Error(responseData.error || "Something went wrong");
        }
        
        setcameraList(responseData.cameras);
        return responseData; // Successful response
      })
      .then((data) => {
        console.log("camera stopped:", data);
      })
      .catch((error) => {
        console.error("Error stopping camera:", error);
      });
  }

  function getRecoTable () {
    fetch("/api/reco_table", {
      method: "GET"
    })
      .then(async (response) => {
        const responseData = await response.json(); // Parse JSON response
        if (!response.ok) {
          // Handle HTTP error responses
          throw new Error(responseData.error || "Something went wrong");
        }
        
        return responseData; // Successful response
      })
      .then((data) => {
        console.log("reco_table :", data);
      })
      .catch((error) => {
        console.error("Error stopping camera:", error);
      });
  }
  useEffect(() => {
    getCamerasList();
    getRecoTable();
  }, []);

  const [cameraFeeds, setCameraFeeds] = useState({});

  useEffect(() => {
    // const socket = io.connect('http://' + window.location.hostname + ':5757');  // Adjust port if needed
    const socket = io();

    socket.on("frame", (data) => {
      const { camera_name, status, image } = data;

      setCameraFeeds((prevFeeds) => {
        return {
          ...prevFeeds,
          [camera_name]: { status, image, isEnabled: true }, // Update camera status and image
        };
      });
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    Object.keys(cameraFeeds).forEach((camera_name) => {
      if (!camEnabled.hasOwnProperty(camera_name)) {
        setcamEnabled({ ...camEnabled, [camera_name]: true });
      }
    });
  }, [cameraFeeds]);

  return (
    <div className="main-container">
      <div className="dash-header">
        <div className="cont-left">
          <div className="font-sm">Dashboard</div>
        </div>
        <div className="cont-right"></div>
      </div>
      <div className="main-dash-container">
        <div className={`sidebar-column gateways`}>
          <div className="list-container">
            <div className="list-title">Settings</div>
            <div className="list-item">
              <div
                className="search-wrapper"
                style={{
                  display: "flex",
                  alignItems: "center",
                  position: "relative",
                }}
              >
                <input
                  type="text"
                  className="search"
                  name="addNewCamera"
                  id="addNewCamera"
                  placeholder="Camera name"
                  // onChange={onFilterTextBoxChanged}
                  style={{
                    marginRight: "5px",
                  }}
                />
                <input
                  type="text"
                  className="search"
                  name="addNewCameraURL"
                  id="addNewCameraURL"
                  placeholder="Camera URL"
                  // onChange={onFilterTextBoxChanged}
                  style={{
                    marginRight: "5px",
                  }}
                />
                <AddNew
                  svgHeight={"30px"}
                  svgColor={"#fff"}
                  onClick={() =>
                    handle_add_Submit(
                      document.getElementById("addNewCamera").value,
                      document.getElementById("addNewCameraURL").value
                    )
                  }
                />
              </div>
            </div>
            {cameraList.map((cam) => (
              <div className="list-item group-item ">
                <div
                  className="label"
                  onClick={() => {
                    setcamEnabled({ ...camEnabled, [cam.camera_name]: true });
                    handle_start_Submit(cam.camera_name);
                  }}
                >
                  {camEnabled[cam.camera_name] === true? (
                    <span
                      className="group_icon_inner"
                      style={{
                        backgroundColor: "rgb(134, 173, 74)",
                      }}
                      // onClick={() => setGroupProfileVisible(!groupProfileVisible)}
                    ></span>
                  ) : (
                    <span
                      className="group_icon_inner"
                      style={{
                        backgroundColor: "rgb(255, 82, 82)",
                      }}
                      // onClick={() => setGroupProfileVisible(!groupProfileVisible)}
                    ></span>
                  )}
                  <span>{cam.camera_name}</span>
                </div>
                <div className="icons">
                  <div
                    className="add-icon group-icon"
                    onClick={() => handle_remove_Submit(cam.camera_name)}
                  >
                    <RemoveSVG
                      svgHeight={"25px"}
                      svgColor={"#fff"}
                      onClick={null}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="dash-content">
          {Object.keys(cameraFeeds).map((cameraName) => (
            <Fragment>
              {camEnabled[cameraName] === true && (
                <div className="cam-card">
                  <div className="cam-header">
                    <div className="cam-title">
                      {camEnabled[cameraName] === true ? (
                        <span
                          className="group_icon_inner"
                          style={{
                            backgroundColor: "rgb(134, 173, 74)",
                          }}
                          // onClick={() => setGroupProfileVisible(!groupProfileVisible)}
                        ></span>
                      ) : (
                        <span
                          className="group_icon_inner"
                          style={{
                            backgroundColor: "rgb(255, 82, 82)",
                          }}
                          // onClick={() => setGroupProfileVisible(!groupProfileVisible)}
                        ></span>
                      )}
                      <span>{cameraName}</span>
                    </div>
                    <div className="cam-actions">
                      <div className="action-icon">
                        <CloseSvg
                          svgHeight={"15px"}
                          svgColor={"#fff"}
                          onClick={() => {
                            setcamEnabled({
                              ...camEnabled,
                              [cameraName]: false,
                            });
                            handle_stop_Submit(cameraName);
                            }}
                            />
                          </div>
                          </div>
                        </div>
                        <div className="cam-preview" onClick={() => {
                          const imgElement = document.getElementById("feed_" + cameraName);
                          if (imgElement.requestFullscreen) {
                          imgElement.requestFullscreen();
                          } else if (imgElement.mozRequestFullScreen) { // Firefox
                          imgElement.mozRequestFullScreen();
                          } else if (imgElement.webkitRequestFullscreen) { // Chrome, Safari and Opera
                          imgElement.webkitRequestFullscreen();
                          } else if (imgElement.msRequestFullscreen) { // IE/Edge
                          imgElement.msRequestFullscreen();
                          }
                        }}>
                          <img
                          id={"feed_" + cameraName}
                          src={`data:image/jpeg;base64,${cameraFeeds[cameraName].image}`}
                          alt={cameraName}
                          style={{ width: "100%", height: "auto", objectFit: "contain" }}
                          />
                        </div>
                        </div>
                      )}
                      </Fragment>
                    ))}
                    </div>
                  </div>
                  </div>
    // <div>
    //   <h1>Welcome to the Dashboard</h1>
    // <form onSubmit={handle_add_Submit}>
    //   <h1>Camera Feeds</h1>
    //     <div id="camera-manage">
    //     <div id="add-camera">
    //         <h3>Add Camera</h3>
    //         <input
    //           type="text"
    //           placeholder="Enter camera name"
    //           value = {camera_name}
    //           onChange = {(e) => setCameraName(e.target.value)}
    //           required
    //           />
    //         <input
    //           type="text"
    //           placeholder="Enter camera URL"
    //           value = {camera_url}
    //           onChange = {(e) => setCameraUrl(e.target.value)}
    //           required
    //           />
    //         <button id="add_camera" type='submit'>Add Camera</button>
    //       </div>
    //     </div>
    // </form>
    // <form onSubmit={handle_remove_Submit}>
    //   <div id="Remove-camera">
    //     <h3>Remove Camera</h3>
    //     <input
    //       type="text"
    //       placeholder="Enter camera name"
    //       value = {camera_name}
    //       onChange = {(e) => setCameraName(e.target.value)}
    //       required
    //       />

    //     <button id="remove_camera" type='submit'>Remove Camera</button>
    //   </div>
    // </form>
    // <form onSubmit={handle_start_Submit}>
    //   <div id="start-camera">
    //     <h3>start Camera</h3>
    //     <input
    //       type="text"
    //       placeholder="Enter camera name"
    //       value = {camera_name}
    //       onChange = {(e) => setCameraName(e.target.value)}
    //       required
    //       />

    //     <button id="start_camera" type='submit'>start Camera</button>
    //   </div>
    // </form>
    // <form onSubmit={handle_stop_Submit}>
    //   <div id="stop-camera">
    //     <h3>stop Camera</h3>
    //     <input
    //       type="text"
    //       placeholder="Enter camera name"
    //       value = {camera_name}
    //       onChange = {(e) => setCameraName(e.target.value)}
    //       required
    //       />

    //     <button id="stop_camera" type='submit'>stop Camera</button>
    //   </div>
    // </form>
    // <h1>Camera Feeds</h1>
    // <CameraFeed />
    // </div>
  );
};

export default Dashboard;
