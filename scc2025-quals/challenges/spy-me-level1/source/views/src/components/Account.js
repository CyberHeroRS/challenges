import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Buffer } from 'buffer';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import VisibilityIcon from '@mui/icons-material/Visibility';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

function Account() {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [userData, setUserData] = useState(null);
  const [error, setError] = useState('');
  const [flag, setFlag] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserInfo = async (targetUserId) => {
      if (!targetUserId) return;
      
      try {
        const encodedId = Buffer.from(JSON.stringify({id: targetUserId})).toString('base64');
        const response = await fetch(`/api/account_info/${encodedId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch user info');
        }
        return await response.json();
      } catch (error) {
        console.error('Error fetching user info:', error);
        throw error;
      }
    };

    const messageHandler = async (event) => {
      if (event.data.type === 'FETCH_USER_INFO') {
        try {
          if (!event.data.userId) throw new Error('No user ID provided');
          const data = await fetchUserInfo(event.data.userId);
          const response = {
            type: 'USER_INFO_RESPONSE',
            data: data,
            error: null
          };
          (event.source || window.opener).postMessage(response, '*');
        } catch (err) {
          const errorResponse = {
            type: 'USER_INFO_RESPONSE',
            data: null,
            error: err.message
          };
          (event.source || window.opener).postMessage(errorResponse, '*');
        }
      } else if (event.data.type === 'USER_INFO_RESPONSE' && event.source === window) {
        if (event.data.error) {
          setError(event.data.error);
          setLoading(false);
        } else {
          setUserData(event.data.data);
          if (event.data.data.username === 'admin' || event.data.data.username === 'icvorovic') {
            try {
              const loginResponse = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                  username: event.data.data.username,
                  secretCode: event.data.data.secret_code
                })
              });
              const loginData = await loginResponse.json();
              if (loginData.flag) {
                setFlag(loginData.flag);
              }
            } catch (err) {
              console.error('Error fetching flag:', err);
            }
          }
          setLoading(false);
        }
      }
    };

    window.addEventListener('message', messageHandler);

    window.postMessage({ type: 'FETCH_USER_INFO', userId: userId }, '*');

    return () => window.removeEventListener('message', messageHandler);
  }, [userId]);


  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 8, textAlign: 'center' }}>
        <Typography color="error">{error}</Typography>
        <Button
          variant="contained"
          onClick={() => navigate('/login')}
          sx={{ mt: 2 }}
        >
          Back to Login
        </Button>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        marginTop: 8,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <Paper
        elevation={6}
        sx={{
          p: 4,
          width: '100%',
          maxWidth: 600,
          backgroundColor: 'background.paper',
          borderRadius: 2,
          border: '1px solid rgba(255, 23, 68, 0.5)',
        }}
      >
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <SecurityIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
          <Typography component="h1" variant="h4" color="primary" gutterBottom>
            AGENT PROFILE
          </Typography>
          <Typography variant="body2" color="text.secondary">
            СТРОГО ПОВЕРЉИВО - STROGO POVERLJIVO
          </Typography>
        </Box>

        {userData && (
          <>
            <Card variant="outlined" sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Agent Information
                </Typography>
                <Typography variant="body1">
                  First Name: {userData.first_name}
                </Typography>
                <Typography variant="body1">
                  Last Name: {userData.last_name}
                </Typography>
                <Typography variant="body1">
                  Username: {userData.username}
                </Typography>
                {flag && (
                  <Box sx={{ mt: 2 }}>
                    <Alert severity="success" icon={<SecurityIcon />}>
                      <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                        {flag}
                      </Typography>
                    </Alert>
                  </Box>
                )}
              </CardContent>
            </Card>


            <Button
              fullWidth
              variant="contained"
              color="secondary"
              onClick={() => navigate('/login')}
            >
              LOGOUT
            </Button>
          </>
        )}
      </Paper>
    </Box>
  );
}

export default Account; 