import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CameraFeed from './camera_feed';

const Dashboard = () => {
  const navigate = useNavigate();
  const [camera_name,setCameraName] = React.useState('');
  const [camera_url,setCameraUrl] = React.useState(''); 

  const handle_add_Submit = (event) => {
    event.preventDefault();
    if (camera_name && camera_url) {
      console.log('camera details are:', { camera_name, camera_url });
      fetch('/api/add_camera', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ camera_name: camera_name, camera_url: camera_url }),
      })
        .then(async (response) => {
          const responseData = await response.json(); // Parse JSON response
          if (!response.ok) {
            // Handle HTTP error responses
            throw new Error(responseData.error || 'Something went wrong');
          }
          return responseData; // Successful response
        })
        .then((data) => {
          console.log('camera added:', data);
        })
        .catch((error) => {
          console.error('Error adding camera:', error);
        });
    } else {
      alert('Please fill in all fields');
    }
  }  
  
  const handle_remove_Submit = (event) => {
    event.preventDefault();
    if (camera_name && camera_url) {
      console.log('camera details are:', { camera_name, camera_url });
      fetch('/api/start_feed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ camera_name: camera_name, camera_url: camera_url }),
      })
        .then(async (response) => {
          const responseData = await response.json(); // Parse JSON response
          if (!response.ok) {
            // Handle HTTP error responses
            throw new Error(responseData.error || 'Something went wrong');
          }
          return responseData; // Successful response
        })
        .then((data) => {
          console.log('camera added:', data);
        })
        .catch((error) => {
          console.error('Error adding camera:', error);
        });
    } else {
      alert('Please fill in all fields');
    }
  }  
  const handle_start_Submit = (event) => {
    event.preventDefault();
    if (camera_name && camera_url) {
      console.log('camera details are:', { camera_name, camera_url });
      fetch('/api/stop_feed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ camera_name: camera_name, camera_url: camera_url }),
      })
        .then(async (response) => {
          const responseData = await response.json(); // Parse JSON response
          if (!response.ok) {
            // Handle HTTP error responses
            throw new Error(responseData.error || 'Something went wrong');
          }
          return responseData; // Successful response
        })
        .then((data) => {
          console.log('camera added:', data);
        })
        .catch((error) => {
          console.error('Error adding camera:', error);
        });
    } else {
      alert('Please fill in all fields');
    }
  }  
  const handle_stop_Submit = (event) => {
    event.preventDefault();
    if (camera_name && camera_url) {
      console.log('camera details are:', { camera_name, camera_url });
      fetch('/api/remove_camera', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ camera_name: camera_name, camera_url: camera_url }),
      })
        .then(async (response) => {
          const responseData = await response.json(); // Parse JSON response
          if (!response.ok) {
            // Handle HTTP error responses
            throw new Error(responseData.error || 'Something went wrong');
          }
          return responseData; // Successful response
        })
        .then((data) => {
          console.log('camera added:', data);
        })
        .catch((error) => {
          console.error('Error adding camera:', error);
        });
    } else {
      alert('Please fill in all fields');
    }
  }

  return (
    <div>
      <h1>Welcome to the Dashboard</h1>
    <form onSubmit={handle_add_Submit}>
      <h1>Camera Feeds</h1>
        <div id="camera-manage">
        <div id="add-camera">
            <h3>Add Camera</h3>
            <input 
              type="text" 
              placeholder="Enter camera name"
              value = {camera_name} 
              onChange = {(e) => setCameraName(e.target.value)}
              required
              />
            <input 
              type="text" 
              placeholder="Enter camera URL"
              value = {camera_url} 
              onChange = {(e) => setCameraUrl(e.target.value)}
              required
              />
            <button id="add_camera" type='submit'>Add Camera</button>
          </div>
        </div>
    </form>
    <form onSubmit={handle_remove_Submit}>
      <div id="Remove-camera">
        <h3>Remove Camera</h3>
        <input 
          type="text" 
          placeholder="Enter camera name"
          value = {camera_name} 
          onChange = {(e) => setCameraName(e.target.value)}
          required
          />
        <input 
          type="text" 
          placeholder="Enter camera URL"
          value = {camera_url} 
          onChange = {(e) => setCameraUrl(e.target.value)}
          required
          />
        <button id="remove_camera" type='submit'>Remove Camera</button>
      </div>
    </form>    
    <form onSubmit={handle_start_Submit}>
      <div id="start-camera">
        <h3>start Camera</h3>
        <input 
          type="text" 
          placeholder="Enter camera name"
          value = {camera_name} 
          onChange = {(e) => setCameraName(e.target.value)}
          required
          />
        <input 
          type="text" 
          placeholder="Enter camera URL"
          value = {camera_url} 
          onChange = {(e) => setCameraUrl(e.target.value)}
          required
          />
        <button id="start_camera" type='submit'>start Camera</button>
      </div>
    </form>    
    <form onSubmit={handle_stop_Submit}>
      <div id="stop-camera">
        <h3>stop Camera</h3>
        <input 
          type="text" 
          placeholder="Enter camera name"
          value = {camera_name} 
          onChange = {(e) => setCameraName(e.target.value)}
          required
          />
        <input 
          type="text" 
          placeholder="Enter camera URL"
          value = {camera_url} 
          onChange = {(e) => setCameraUrl(e.target.value)}
          required
          />
        <button id="stop_camera" type='submit'>stop Camera</button>
      </div>
    </form>
    <h1>Camera Feeds</h1>
    <CameraFeed />
    </div>
  );
};

export default Dashboard;
