import React, { createContext, useState, useContext, useEffect } from 'react';
import { Buffer } from 'buffer';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userId, setUserId] = useState(() => {
    const saved = localStorage.getItem('userId');
    return saved ? parseInt(saved) : null;
  });

  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (!userId) {
          setIsAuthenticated(false);
          setIsLoading(false);
          return;
        }

        const id = Buffer.from(JSON.stringify({id: userId})).toString('base64');
        const response = await fetch(`/api/account_info/${id}`);
        if (response.ok) {
          const data = await response.json();
          setUserId(data.id);
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
          setUserId(null);
          localStorage.removeItem('userId');
        }
      } catch (error) {
        setIsAuthenticated(false);
        setUserId(null);
        localStorage.removeItem('userId');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [userId]);

  const login = async (id) => {
    setUserId(id);
    setIsAuthenticated(true);
    localStorage.setItem('userId', id.toString());
  };
  
  const logout = () => {
    setIsAuthenticated(false);
    setUserId(null);
    localStorage.removeItem('userId');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, login, logout, userId }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 