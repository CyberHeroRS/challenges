import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import VpnKeyIcon from '@mui/icons-material/VpnKey';

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    firstName: '',
    lastName: '',
  });
  const [error, setError] = useState('');
  const [secretCode, setSecretCode] = useState('');
  const [showSecretDialog, setShowSecretDialog] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Registration failed');
      }

      setSecretCode(data.secretCode);
      setShowSecretDialog(true);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDialogClose = () => {
    setShowSecretDialog(false);
    navigate('/login');
  };

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
          maxWidth: 400,
          backgroundColor: 'background.paper',
          borderRadius: 2,
          border: '1px solid rgba(255, 23, 68, 0.5)',
        }}
      >
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <VpnKeyIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
          <Typography component="h1" variant="h4" color="primary" gutterBottom>
            New Agent Registration
          </Typography>
          <Typography variant="body2" color="text.secondary">
            СТРОГО ПОВЕРЉИВО - STROGO POVERLJIVO
          </Typography>
        </Box>

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            label="Username"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            autoFocus
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="First Name"
            value={formData.firstName}
            onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="Last Name"
            value={formData.lastName}
            onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
          />

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            REGISTER
          </Button>

          <Button
            fullWidth
            variant="outlined"
            onClick={() => navigate('/login')}
          >
            Back to Login
          </Button>
        </Box>
      </Paper>

      <Dialog
        open={showSecretDialog}
        onClose={handleDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <VpnKeyIcon color="primary" />
            <Typography variant="h6">Your Secret Code</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Save this code carefully! It will only be shown once and is required for login.
          </Alert>
          <Typography variant="body1" sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
            {secretCode}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose} variant="contained">
            I Have Saved My Code
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Register; 