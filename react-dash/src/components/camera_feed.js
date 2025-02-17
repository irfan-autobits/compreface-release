// CameraFeed.js
import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';

const CameraFeed = () => {
    const [cameraFeeds, setCameraFeeds] = useState({});

    useEffect(() => {
        // const socket = io.connect('http://' + window.location.hostname + ':5757');  // Adjust port if needed
        const socket = io();

        socket.on('frame', (data) => {
            const { camera_name, status, image } = data;

            setCameraFeeds((prevFeeds) => {
                return {
                    ...prevFeeds,
                    [camera_name]: { status, image }  // Update camera status and image
                };
            });
        });

        return () => {
            socket.disconnect();
        };
    }, []);

    return (
        <div>
            {/* <div id="camera-status">
                {Object.keys(cameraFeeds).map((cameraName) => (
                    <div key={cameraName}>
                        <h3>{cameraName} - {cameraFeeds[cameraName].status}</h3>
                    </div>
                ))}
            </div> */}

            <div id="camera-feeds">
                <p> feed </p>
                {Object.keys(cameraFeeds).map((cameraName) => (
                    <div key={cameraName} className="camera-feed">
                        <h3>{cameraName}</h3>
                        <img
                            id={'feed_' + cameraName}
                            src={`data:image/jpeg;base64,${cameraFeeds[cameraName].image}`}
                            alt={cameraName}
                        />
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CameraFeed;
