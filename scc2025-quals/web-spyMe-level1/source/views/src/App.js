import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container } from '@mui/material';

import Login from './components/Login';
import Register from './components/Register';
import Account from './components/Account';
import AgentIndex from './components/AgentIndex';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#ff1744',
    },
    secondary: {
      main: '#b71c1c',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: '"Roboto Mono", monospace',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Container component="main" maxWidth="lg">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route 
                path="/agents" 
                element={
                  <ProtectedRoute>
                    <AgentIndex />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/account" 
                element={
                  <ProtectedRoute>
                    <Account />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/" 
                element={
                  <ProtectedRoute>
                    <Navigate to="/agents" replace />
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </Container>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App; 