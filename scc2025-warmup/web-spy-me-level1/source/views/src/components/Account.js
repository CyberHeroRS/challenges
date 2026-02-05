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
  const [manageSpiesOpen, setManageSpiesOpen] = useState(false);
  const [agents, setAgents] = useState([]);
  const [whitelistData, setWhitelistData] = useState(null);
  const [whitelistDialogOpen, setWhitelistDialogOpen] = useState(false);
  const [selectedUsername, setSelectedUsername] = useState('');

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

  const handleManageSpies = async () => {
    try {
      const response = await fetch('/api/agents');
      if (!response.ok) throw new Error('Failed to fetch agents');
      const data = await response.json();

      for (const agent of data) {
        try {
          const filename = `spy_${agent.username}.json`;
          const encodedFilename = Buffer.from(filename).toString('base64');
          const whitelistResponse = await fetch(`/api/read_whitelist/${encodedFilename}?checkStatus=true`);
          if (whitelistResponse.ok) {
            const statusData = await whitelistResponse.json();
            agent.is_allowed_spy = statusData.is_allowed_spy;
          } else {
            agent.is_allowed_spy = false;
          }
        } catch (error) {
          agent.is_allowed_spy = false;
        }
      }

      setAgents(data);
      setManageSpiesOpen(true);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const handleToggleSpy = async (username, isAllowed) => {
    try {
      const response = await fetch('/api/toggle_spy_access', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, isAllowed })
      });

      if (!response.ok) throw new Error('Failed to toggle spy access');
      
      setAgents(prevAgents => prevAgents.map(agent => {
        if (agent.username === username) {
          return { ...agent, is_allowed_spy: isAllowed };
        }
        return agent;
      }));
    } catch (error) {
      console.error('Error toggling spy access:', error);
    }
  };

  const handleViewWhitelist = async (username) => {
    try {
      const filename = `spy_${username}.json`;
      const encodedFilename = Buffer.from(filename).toString('base64');
      const response = await fetch(`/api/read_whitelist/${encodedFilename}`);
      
      if (response.status === 403) {
        setWhitelistData({ error: "Viewing whitelists is only available in developer mode" });
        setSelectedUsername(username);
        setWhitelistDialogOpen(true);
        return;
      }
      
      if (response.ok) {
        const data = await response.json();
        setWhitelistData(data);
        setSelectedUsername(username);
        setWhitelistDialogOpen(true);
      } else {
        console.error('Whitelist file not found');
      }
    } catch (error) {
      console.error('Error reading whitelist:', error);
    }
  };

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

            {userData.is_admin && (
              <Button
                fullWidth
                variant="contained"
                color="warning"
                startIcon={<AdminPanelSettingsIcon />}
                onClick={handleManageSpies}
                sx={{ mb: 2 }}
              >
                Manage Allowed Spies
              </Button>
            )}

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

      {/* Manage Spies Dialog */}
      <Dialog
        open={manageSpiesOpen}
        onClose={() => setManageSpiesOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AdminPanelSettingsIcon color="warning" />
              <Typography variant="h6">Manage Allowed Spies</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">Developer mode:</Typography>
              <Switch
                disabled
                checked={false}
                size="small"
              />
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          <List>
            {agents.map((agent) => (
              <React.Fragment key={agent.id}>
                <ListItem>
                  <ListItemText
                    primary={agent.codename}
                    secondary={`${agent.first_name} ${agent.last_name} (${agent.username})`}
                  />
                  <ListItemSecondaryAction>
                    <Tooltip title="View Whitelist File">
                      <IconButton
                        edge="end"
                        onClick={() => handleViewWhitelist(agent.username)}
                        sx={{ mr: 2 }}
                      >
                        <VisibilityIcon />
                      </IconButton>
                    </Tooltip>
                    <Switch
                      onChange={(e) => handleToggleSpy(agent.username, e.target.checked)}
                      checked={agent.is_allowed_spy || false}
                      edge="end"
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setManageSpiesOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* View Whitelist Dialog */}
      <Dialog
        open={whitelistDialogOpen}
        onClose={() => setWhitelistDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <VisibilityIcon color="primary" />
            <Typography variant="h6">Whitelist File: {selectedUsername}</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box
            component="pre"
            sx={{
              backgroundColor: 'rgba(0, 0, 0, 0.1)',
              p: 2,
              borderRadius: 1,
              overflow: 'auto',
              maxHeight: 400,
            }}
          >
            {whitelistData?.error ? (
              <Typography color="error">{whitelistData.error}</Typography>
            ) : (
              whitelistData ? JSON.stringify(whitelistData, null, 2) : 'No whitelist file found'
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWhitelistDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Account; 