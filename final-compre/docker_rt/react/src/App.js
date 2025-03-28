import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import { privateRoutes, publiceRoutes } from './routes';
import AppRoute from './routes/route';

function App() {

  return (
    <div className="App">
      <React.Fragment>
        <Router> 
          <Routes>
            {publiceRoutes.map((route, idx) => (
              <Route 
                path={route.path}
                element={route.component}
                key={idx}
                exact={true}
              />
            ))}
            {privateRoutes.map((route, idx) => (
              <Route 
                path={route.path}
                element={
                  <AppRoute element={route.component} />
                }
                key={idx}
                exact={true}
              />
            ))}
          </Routes>
        </Router>
      </React.Fragment>
    </div>
  );
}

export default App;
