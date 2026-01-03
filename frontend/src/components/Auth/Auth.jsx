import React, { useState } from 'react';
import Login from './Login';
import Register from './Register';
import './Auth.css'; // We'll create this CSS file next

const Auth = () => {
  const [isLoginView, setIsLoginView] = useState(true);

  const handleLogin = (result) => {
    console.log('Login successful', result);
    // Redirect or update UI as needed
    window.location.href = '/'; // Redirect to home after login
  };

  const handleRegister = (result) => {
    console.log('Registration successful', result);
    // Switch to login view after successful registration
    setIsLoginView(true);
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-container">
        <div className="auth-toggle">
          <button 
            className={isLoginView ? 'active' : ''} 
            onClick={() => setIsLoginView(true)}
          >
            Login
          </button>
          <button 
            className={!isLoginView ? 'active' : ''} 
            onClick={() => setIsLoginView(false)}
          >
            Register
          </button>
        </div>
        
        {isLoginView ? (
          <Login onLogin={handleLogin} />
        ) : (
          <Register onRegister={handleRegister} />
        )}
      </div>
    </div>
  );
};

export default Auth;