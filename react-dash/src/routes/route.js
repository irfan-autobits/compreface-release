import React from "react";
import { Navigate } from "react-router-dom";


const AppRoute = (props) => {
    // let res = JSON.parse(localStorage.getItem('token'));
    // if(res !== null){
    //     return (
    //         <Navigate to="/dashboard" />
    //     )
    // }
    // let res = JSON.parse(localStorage.getItem('token'));
    let token = JSON.parse(localStorage.getItem('authToken'));  
    let isExpired = true;
    if(token && token.expiry) {
        isExpired = token.expiry < Date.now();
        // console.log('token:', token);
        // console.log('isExpired:', isExpired);
        // console.log("cond str: ___", `${token.expiry} < ${Date.now()}`)
        // console.log("cond ans: ___", token.expiry < Date.now())
        // console.log("cond subs: ___", token.expiry - Date.now())
    }
    // console.log('now:', Date.now());
    
    if(!token || isExpired) {
        if(token) {
            localStorage.removeItem('authToken');
        }
        return (
            <Navigate to="/login" />
        );
    }
    return <React.Fragment>{props.element}</React.Fragment>
};

export default AppRoute;