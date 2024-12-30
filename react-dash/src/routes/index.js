import React from "react";
import { Navigate } from "react-router-dom";


import Login from "../components/login";
import Dashboard from "../components/cam_dashboard";
import Signup from "../components/sign_up";
import Logout from "../components/logout";

const publiceRoutes = [
    { "path": "/logout", "component": <Logout /> },
    { "path": "/login", "component": <Login /> },
    { "path": "/register", "component": <Signup /> },
    { "path": "*", "component": <Navigate to="/" /> },
];

const privateRoutes = [
    { "path": "/dashboard", "component": <Dashboard /> },
    { "path": "/", "component": <Dashboard /> },
];

export { publiceRoutes, privateRoutes };