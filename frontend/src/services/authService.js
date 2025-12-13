// Frontend authentication service

class AuthService {
    constructor(baseURL) {
        this.baseURL = baseURL || process.env.REACT_APP_API_URL || 'http://localhost:8000';
    }

    async register(userData) {
        try {
            const response = await fetch(`${this.baseURL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Store user info and token
            if (result.token) {
                localStorage.setItem('auth_token', result.token);
                localStorage.setItem('user_id', result.user_id);
            }

            return result;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }

    async login(credentials) {
        try {
            const response = await fetch(`${this.baseURL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Store token and user info
            if (result.token) {
                localStorage.setItem('auth_token', result.token);
                localStorage.setItem('user_id', result.user_id);
            }

            return result;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_id');
    }

    isAuthenticated() {
        const token = localStorage.getItem('auth_token');
        return !!token;
    }

    getCurrentUserId() {
        return localStorage.getItem('user_id');
    }

    getToken() {
        return localStorage.getItem('auth_token');
    }

    async getPersonalizationSettings() {
        const token = this.getToken();
        if (!token) {
            throw new Error('Not authenticated');
        }

        try {
            const response = await fetch(`${this.baseURL}/user/personalization`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    this.logout();
                    throw new Error('Unauthorized - please log in again');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting personalization settings:', error);
            throw error;
        }
    }

    async updatePersonalizationSettings(settings) {
        const token = this.getToken();
        if (!token) {
            throw new Error('Not authenticated');
        }

        try {
            const response = await fetch(`${this.baseURL}/user/personalization`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });

            if (!response.ok) {
                if (response.status === 401) {
                    this.logout();
                    throw new Error('Unauthorized - please log in again');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error updating personalization settings:', error);
            throw error;
        }
    }
}

export default AuthService;