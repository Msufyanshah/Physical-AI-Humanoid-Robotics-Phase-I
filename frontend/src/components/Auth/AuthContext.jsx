import React, { createContext, useContext, useState, useEffect } from 'react';
import AuthService from '../../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in when app loads
    const checkAuthStatus = async () => {
      try {
        if (AuthService.getInstance().isAuthenticated()) {
          const userId = AuthService.getInstance().getCurrentUserId();
          const userEmail = AuthService.getInstance().getCurrentUserEmail();
          const username = AuthService.getInstance().getUsername();
          
          setUser({
            id: userId,
            email: userEmail,
            username: username
          });
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Error checking auth status:', error);
        // Clear any invalid tokens
        AuthService.getInstance().logout();
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (credentials) => {
    try {
      const result = await AuthService.getInstance().login(credentials);
      setUser({
        id: result.user_id,
        email: result.email,
        username: result.username
      });
      setIsAuthenticated(true);
      return result;
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const result = await AuthService.getInstance().register(userData);
      setUser({
        id: result.user_id,
        email: result.email,
        username: result.username
      });
      setIsAuthenticated(true);
      return result;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    AuthService.getInstance().logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};