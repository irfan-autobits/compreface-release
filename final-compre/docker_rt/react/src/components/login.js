import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  // const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate(); // For navigation

  const handleSubmit = (event) => {
    event.preventDefault();
    if (email && password) {
      setLoading(true); // Start loading state
      setError(null); // Reset error state
      // setData(null); // Reset previous data
      console.log('credentials are:', { email, password });
  
      fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email, password: password }),
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
          let expiry = new Date().getTime() + 24 * 60 * 60 * 1000; // 1 day
          // setData(data); // Set the fetched datadatadatag
          setLoading(false); // End loading state
          localStorage.setItem('authToken', JSON.stringify({"token": data.token, expiry: expiry}));
          navigate('/dashboard'); // Redirect to another route
        })
        .catch((error) => {
          setError(error.message || 'An error occurred'); // Set error message
          setLoading(false); // End loading state
          console.error('Error fetching data:', error);
        });
    } else {
      alert('Please fill in all fields');
    }
  };
  

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>

      <div>

        <p>
          Don't have an account?
          <a onClick={() => navigate("/register")}>Sign up</a>
        </p>
        <h2>Responce</h2>
        {loading ? (
          <p>Loading...</p> // Show loading state
        ) : error ? (
          <p style={{ color: 'red' }}>{error}</p> // Show error state
        ) : (
          <p>No data yet</p> // No data state
        )}
      </div>
    </div>
  );
};

export default Login;
