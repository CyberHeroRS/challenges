import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Buffer } from 'buffer';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  IconButton,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import SecurityIcon from '@mui/icons-material/Security';
import PersonSearchIcon from '@mui/icons-material/PersonSearch';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';

function AgentIndex() {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agents, setAgents] = useState([]);
  const [spyDialogOpen, setSpyDialogOpen] = useState(false);
  const [spyUrl, setSpyUrl] = useState('');
  const [spyStatus, setSpyStatus] = useState({ message: '', type: '' });
  const [error, setError] = useState('');
  const [isAuthorized, setIsAuthorized] = useState(false);

  const checkAuthorization = async () => {
    if (!userId) {
      setIsAuthorized(false);
      return;
    }

    try {
      const encodedId = Buffer.from(JSON.stringify({id: userId})).toString('base64');
      const response = await fetch(`/api/account_info/${encodedId}`);
      if (response.ok) {
        const data = await response.json();
        const testResponse = await fetch('/api/spy_on', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: '' })
        });
        setIsAuthorized(testResponse.status === 400);
      }
    } catch (error) {
      console.error('Error checking authorization:', error);
      setIsAuthorized(false);
    }
  };

  useEffect(() => {
    fetchAgents();
    checkAuthorization();
  }, [userId]);

  const fetchAgents = async () => {
    try {
      const response = await fetch('/api/agents');
      if (!response.ok) throw new Error('Failed to fetch agents');
      const data = await response.json();
      setAgents(data);
    } catch (error) {
      console.error('Error fetching agents:', error);
      setError('Failed to load agents');
    }
  };

  const handleAgentClick = (agent) => {
    setSelectedAgent(agent);
  };

  const handleSpySubmit = async () => {
    try {
      const response = await fetch('/api/spy_on', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: spyUrl })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSpyStatus({ message: data.message, type: 'success' });
        setTimeout(() => {
          setSpyDialogOpen(false);
          setSpyUrl('');
          setSpyStatus({ message: '', type: '' });
        }, 2000);
      } else {
        setSpyStatus({ message: data.error, type: 'error' });
      }
    } catch (error) {
      setSpyStatus({ message: 'Failed to submit URL', type: 'error' });
    }
  };

  return (
    <Box sx={{ py: 4 }}>
      <Paper
        elevation={6}
        sx={{
          p: 4,
          backgroundColor: 'background.paper',
          borderRadius: 2,
          border: '1px solid rgba(255, 23, 68, 0.5)',
        }}
      >
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            {isAuthorized && (
              <Button
                variant="contained"
                color="secondary"
                startIcon={<TrackChangesIcon />}
                onClick={() => setSpyDialogOpen(true)}
                sx={{ mr: 2 }}
              >
                Spy On Someone
              </Button>
            )}
            <Button
              variant="outlined"
              color="primary"
              startIcon={<AccountCircleIcon />}
              onClick={() => navigate('/account')}
              sx={!isAuthorized ? { ml: 'auto' } : {}}
            >
              My Account
            </Button>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <SecurityIcon color="primary" sx={{ fontSize: 48, mb: 2 }} />
            <Typography component="h1" variant="h4" color="primary" gutterBottom>
              BALKAN INTELLIGENCE BUREAU
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              СТРОГО ПОВЕРЉИВО - STROGO POVERLJIVO
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Active Field Agents Database
            </Typography>
          </Box>
        </Box>

        {error ? (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {agents.map((agent) => (
              <Grid item xs={12} sm={6} md={4} key={agent.id}>
                <Card 
                  variant="outlined" 
                  sx={{ 
                    height: '100%',
                    cursor: 'pointer',
                    '&:hover': {
                      border: '1px solid rgba(255, 23, 68, 0.5)',
                    }
                  }}
                  onClick={() => handleAgentClick(agent)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" component="div">
                        {agent.codename}
                      </Typography>
                      <IconButton size="small">
                        <PersonSearchIcon />
                      </IconButton>
                    </Box>
                    <Typography color="text.secondary" gutterBottom>
                      {agent.specialization}
                    </Typography>
                    <Chip 
                      label={agent.status}
                      color={agent.status === 'Active' ? 'success' : agent.status === 'Under Investigation' ? 'error' : 'warning'}
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {selectedAgent && (
          <Paper 
            elevation={3} 
            sx={{ 
              mt: 4, 
              p: 3,
              backgroundColor: 'rgba(0, 0, 0, 0.2)',
              border: '1px solid rgba(255, 23, 68, 0.3)',
            }}
          >
            <Typography variant="h5" gutterBottom color="primary">
              Agent Details
            </Typography>
            <Typography variant="body1" paragraph>
              <strong>Real Name:</strong> {selectedAgent.first_name} {selectedAgent.last_name}
            </Typography>
            <Typography variant="body1" paragraph>
              <strong>Specialization:</strong> {selectedAgent.specialization}
            </Typography>
            <Typography variant="body1" paragraph>
              <strong>Status:</strong> {selectedAgent.status}
            </Typography>
            <Typography variant="body1">
              <strong>Notes:</strong> {selectedAgent.notes}
            </Typography>
          </Paper>
        )}

        {/* Spy Dialog */}
        <Dialog 
          open={spyDialogOpen} 
          onClose={() => {
            setSpyDialogOpen(false);
            setSpyUrl('');
            setSpyStatus({ message: '', type: '' });
          }}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrackChangesIcon color="primary" />
              <Typography variant="h6">Spy On Someone</Typography>
            </Box>
          </DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Submit a URL for the admin bot to investigate
            </Typography>
            <TextField
              autoFocus
              margin="dense"
              label="Target URL"
              type="url"
              fullWidth
              variant="outlined"
              value={spyUrl}
              onChange={(e) => setSpyUrl(e.target.value)}
              placeholder="https://example.com"
            />
            {spyStatus.message && (
              <Alert severity={spyStatus.type} sx={{ mt: 2 }}>
                {spyStatus.message}
              </Alert>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSpyDialogOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleSpySubmit} 
              variant="contained"
              disabled={!spyUrl}
            >
              Submit
            </Button>
          </DialogActions>
        </Dialog>
      </Paper>
    </Box>
  );
}

export default AgentIndex; 