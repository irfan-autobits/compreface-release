import React from 'react';
import { useNavigate } from 'react-router-dom';

const Logout = () => {
    const navigate = useNavigate(); // For navigation
  
  setTimeout(() => {
    localStorage.removeItem('authToken');
    navigate('/');

  }, [100]);
  return (
    <React.Fragment>
      <h1>Log out</h1>
    </React.Fragment>
  );
};

export default Logout;
