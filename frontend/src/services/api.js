import axios from 'axios';

const API_BASE_URL = '/api';

export const sendMessage = async (message, history) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/chat`, {
            message,
            history
        });
        return response.data.response;
    } catch (error) {
        console.error('Error sending message:', error);
        throw new Error(error.response?.data?.error || 'Failed to send message');
    }
};

export const fetchDatabase = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/database`);
        return response.data.data;
    } catch (error) {
        console.error('Error fetching database:', error);
        throw new Error(error.response?.data?.error || 'Failed to fetch database');
    }
};
