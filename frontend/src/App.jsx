import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ChatHistory from './components/ChatHistory';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import DatabaseViewer from './components/DatabaseViewer';
import { sendMessage } from './services/api';

const STORAGE_KEY = 'rupay_chat_history';

function App() {
    const [chats, setChats] = useState([]);
    const [activeChat, setActiveChat] = useState(null);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    // Initialize chats from localStorage or create first chat
    useEffect(() => {
        const savedChats = localStorage.getItem(STORAGE_KEY);
        if (savedChats) {
            const parsedChats = JSON.parse(savedChats);
            setChats(parsedChats);
            setActiveChat(parsedChats[0]?.id || null);
        } else {
            createNewChat();
        }
    }, []);

    // Save chats to localStorage whenever they change
    useEffect(() => {
        if (chats.length > 0) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
        }
    }, [chats]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const getCurrentChat = () => {
        return chats.find(chat => chat.id === activeChat);
    };

    const createNewChat = () => {
        const newChat = {
            id: Date.now().toString(),
            timestamp: Date.now(),
            messages: [
                { role: 'assistant', content: 'Hello! I am your RuPay Transaction Assistant. How can I help you today?' }
            ]
        };
        setChats(prev => [newChat, ...prev]);
        setActiveChat(newChat.id);
    };

    const selectChat = (chatId) => {
        setActiveChat(chatId);
    };

    const deleteChat = (chatId) => {
        const updatedChats = chats.filter(chat => chat.id !== chatId);
        setChats(updatedChats);

        if (chatId === activeChat) {
            if (updatedChats.length > 0) {
                setActiveChat(updatedChats[0].id);
            } else {
                createNewChat();
            }
        }
    };

    const updateChatMessages = (chatId, newMessages) => {
        setChats(prev => prev.map(chat =>
            chat.id === chatId
                ? { ...chat, messages: newMessages, timestamp: Date.now() }
                : chat
        ));
    };

    useEffect(() => {
        scrollToBottom();
    }, [activeChat, chats]);

    const handleSendMessage = async (userMessage) => {
        const currentChat = getCurrentChat();
        if (!currentChat) return;

        // Add user message
        const newMessages = [...currentChat.messages, { role: 'user', content: userMessage }];
        updateChatMessages(activeChat, newMessages);
        setLoading(true);

        try {
            // API Call to backend
            const response = await sendMessage(userMessage, newMessages);
            updateChatMessages(activeChat, [...newMessages, { role: 'assistant', content: response }]);
        } catch (error) {
            updateChatMessages(activeChat, [...newMessages, { role: 'assistant', content: `Error: ${error.message}` }]);
        } finally {
            setLoading(false);
        }
    };

    const currentChat = getCurrentChat();
    const messages = currentChat?.messages || [];

    return (
        <>
            <Header />
            <div className="app-container">
                <ChatHistory
                    chats={chats}
                    activeChat={activeChat}
                    onNewChat={createNewChat}
                    onSelectChat={selectChat}
                    onDeleteChat={deleteChat}
                />
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
