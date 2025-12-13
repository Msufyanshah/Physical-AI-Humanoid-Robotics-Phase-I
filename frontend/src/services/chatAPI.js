// Frontend service to handle API calls to the backend chat endpoints

class ChatAPIService {
    constructor(baseURL) {
        this.baseURL = baseURL || process.env.REACT_APP_API_URL || 'http://localhost:8000';
    }

    async askGeneral(question, userId = null) {
        try {
            const response = await fetch(`${this.baseURL}/ask-general`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    user_id: userId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error in askGeneral:', error);
            throw error;
        }
    }

    async askSelected(question, selectedText, userId = null) {
        try {
            const response = await fetch(`${this.baseURL}/ask-selected`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    selected_text: selectedText,
                    user_id: userId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error in askSelected:', error);
            throw error;
        }
    }

    async embedChunk(content, metadata) {
        try {
            const response = await fetch(`${this.baseURL}/embed-chunk`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    metadata: metadata
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error in embedChunk:', error);
            throw error;
        }
    }

    async translateUrdu(content, preserveFormatting = true) {
        try {
            const response = await fetch(`${this.baseURL}/translate-urdu`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    preserve_formatting: preserveFormatting
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error in translateUrdu:', error);
            throw error;
        }
    }

    async getPersonalizedContent(userId, moduleId, chapterId = null) {
        try {
            const response = await fetch(`${this.baseURL}/personalize-content`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify({
                    user_id: userId,
                    module_id: moduleId,
                    chapter_id: chapterId
                })
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Unauthorized - clear auth token
                    localStorage.removeItem('auth_token');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error in getPersonalizedContent:', error);
            throw error;
        }
    }
}

export default ChatAPIService;