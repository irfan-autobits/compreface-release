import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
    const navigate = useNavigate(); // For navigation
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    // Basic validation (for demonstration purposes)
    if (email && password) {
      setLoading(true); // Start loading state
      setError(null); // Reset error state
      console.log('User created successfully:', { email, password });
      
      fetch('/api/sign', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email, password: password }),
      })
        .then((response) => response.json())
        .then((data) => {
          setData(data); // Set the fetched data
          setLoading(false); // End loading state
        })
        .catch((error) => {
          setError('An error occurred while fetching data'); // Set error state
          setLoading(false); // End loading state
          console.error('Error fetching data:', error);
        });
    } else {
      alert('Please fill in all fields');
    }
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
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
        <button type="submit">Sign Up</button>
      </form>

      <div>

        <p>
          Already have an account?
          <a onClick={() => navigate("/login")}>Login</a>
        </p>
        <h2>Responce</h2>
        {loading ? (
          <p>Loading...</p> // Show loading state
        ) : error ? (
          <p style={{ color: 'red' }}>{error}</p> // Show error state
        ) : data ? (
          <div>
            <p>{data.message}</p>
          </div>
        ) : (
          <p>No data yet</p> // No data state
        )}
      </div>
    </div>
  );
};

export default Signup;
