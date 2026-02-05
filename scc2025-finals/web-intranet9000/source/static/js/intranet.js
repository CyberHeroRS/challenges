class IntranetApp {
    constructor() {
        this.token = localStorage.getItem('sessionToken');
    }

    async login(employeeNumber, password) {
        const response = await this.unauthenticatedRequest('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ employee_number: parseInt(employeeNumber), password })
        });

        if (response.ok) {
            const result = await response.json();
            this.token = result.session_token;
            localStorage.setItem('sessionToken', this.token);
            return true;
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Login failed');
        }
    }

    async unauthenticatedRequest(url, options = {}) {
        return fetch(url, options);
    }

    async authenticatedRequest(url, options = {}) {
        if (!this.token) {
            window.location.href = '/login';
            throw new Error('Not authenticated');
        }

        const authOptions = {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${this.token}`
            }
        };

        const response = await fetch(url, authOptions);

        if (response.status === 401 || response.status === 403) {
            // Token expired or invalid
            localStorage.removeItem('sessionToken');
            window.location.href = '/login';
            throw new Error('Authentication failed');
        }

        return response;
    }
}