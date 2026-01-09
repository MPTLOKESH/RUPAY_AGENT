
import axios from 'axios';

const API_BASE_URL = '/api';

// Send a chat message to the backend
export const sendMessage = async (message, sessionId) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/chat`, {
            message,
            session_id: sessionId,
            history: [] // History is now managed by the backend
        });
        return response.data;
    } catch (error) {
        console.error('Error sending message:', error);
        throw error;
    }
};

// Get chat history for a session
export const getHistory = async (sessionId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/history/${sessionId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching history:', error);
        throw error;
    }
};

// Clear chat history
export const clearHistory = async (sessionId) => {
    try {
        await axios.delete(`${API_BASE_URL}/history/${sessionId}`);
    } catch (error) {
        console.error('Error clearing history:', error);
        throw error;
    }
};

// Fetch database data (renamed from fetchDatabase)
export const getDatabaseData = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/database`);
        return response.data.data;
    } catch (error) {
        console.error('Error fetching database:', error);
        throw new Error(error.response?.data?.error || 'Failed to fetch database');
    }
};
