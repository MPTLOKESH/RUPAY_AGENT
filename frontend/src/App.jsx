import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import DatabaseViewer from './components/DatabaseViewer';
import { sendMessage } from './services/api'; // Keep the API service

function App() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am your RuPay Transaction Assistant. How can I help you today?' }
    ]);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async (userMessage) => {
        // Add user message
        const newMessages = [...messages, { role: 'user', content: userMessage }];
        setMessages(newMessages);
        setLoading(true);

        try {
            // API Call to backend
            const response = await sendMessage(userMessage, newMessages);
            setMessages(prev => [...prev, { role: 'assistant', content: response }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${error.message}` }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <Header />
            <div className="app-container">
                <div className="main-content">
                    <div className="chat-container">
                        <div className="chat-messages">
                            {messages.map((msg, index) => (
                                <ChatMessage key={index} message={msg} />
                            ))}
                            {loading && (
                                <div className="message assistant">
                                    <div className="message-avatar">🤖</div>
                                    <div className="message-content">
                                        <span className="loading-spinner"></span>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                        <ChatInput onSend={handleSendMessage} disabled={loading} />
                    </div>
                </div>
                <DatabaseViewer />
            </div>
        </>
    );
}

export default App;
