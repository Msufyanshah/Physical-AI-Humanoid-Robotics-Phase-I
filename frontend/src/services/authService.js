// Frontend authentication service

class AuthService {
    constructor(baseURL) {
        // For Docusaurus, use a default API URL
        // Environment variables in Docusaurus are handled differently
        this.baseURL = baseURL || 'http://localhost:8000';
    }

    async register(userData) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/rag/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            // Store user info and token
            if (result.access_token) {
                localStorage.setItem('auth_token', result.access_token);
                localStorage.setItem('user_id', result.user_id);
                localStorage.setItem('user_email', result.email);
                localStorage.setItem('username', result.username);
            }

            return result;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }

    async login(credentials) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/rag/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            // Store token and user info
            if (result.access_token) {
                localStorage.setItem('auth_token', result.access_token);
                localStorage.setItem('user_id', result.user_id);
                localStorage.setItem('user_email', result.email);
                localStorage.setItem('username', result.username);
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
        localStorage.removeItem('user_email');
        localStorage.removeItem('username');
    }

    isAuthenticated() {
        const token = localStorage.getItem('auth_token');
        return !!token;
    }

    getCurrentUserId() {
        return localStorage.getItem('user_id');
    }

    getCurrentUserEmail() {
        return localStorage.getItem('user_email');
    }

    getUsername() {
        return localStorage.getItem('username');
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
            const response = await fetch(`${this.baseURL}/api/v1/rag/user/personalization`, {
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
            const response = await fetch(`${this.baseURL}/api/v1/rag/user/personalization`, {
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

// Singleton instance
let instance = null;

AuthService.getInstance = () => {
    if (!instance) {
        instance = new AuthService();
    }
    return instance;
};

export default AuthService;