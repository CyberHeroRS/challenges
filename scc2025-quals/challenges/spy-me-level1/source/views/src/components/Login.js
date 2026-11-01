import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Alert,
} from '@mui/material';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import { useAuth } from '../context/AuthContext';

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [secretCode, setSecretCode] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, secretCode }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Login failed');
      }

      await login(data.id);
      navigate('/agents');
    } catch (err) {
      setError(err.message);
    }
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
            SpyMe HQ
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
            label="Agent Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="Secret Code"
            value={secretCode}
            onChange={(e) => setSecretCode(e.target.value)}
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
            AUTHENTICATE
          </Button>

          <Typography variant="body2" align="center" sx={{ mt: 2 }}>
            New agent?{' '}
            <Link to="/register" style={{ color: '#ff1744' }}>
              Register here
            </Link>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
}

export default Login; 