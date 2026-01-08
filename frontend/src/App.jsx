import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ChatHistory from './components/ChatHistory';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
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
        // Check if there's already an empty chat (only has the initial greeting)
        const existingEmptyChat = chats.find(chat => chat.messages.length === 1 && chat.messages[0].role === 'assistant');

        if (existingEmptyChat) {
            setActiveChat(existingEmptyChat.id);
            return;
        }

        const newChat = {
            id: Date.now().toString(),
            timestamp: Date.now(),
            messages: [
                { role: 'assistant', content: 'Hello! I am RuPay Agent, your AI-powered transaction assistant. How can I help you today?' }
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

    const clearAllChats = () => {
        if (window.confirm('Are you sure you want to delete all chat history?')) {
            const newChat = {
                id: Date.now().toString(),
                timestamp: Date.now(),
                messages: [
                    { role: 'assistant', content: 'Hello! I am RuPay Agent, your AI-powered transaction assistant. How can I help you today?' }
                ]
            };
            setChats([newChat]);
            setActiveChat(newChat.id);
            localStorage.removeItem(STORAGE_KEY);
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

        // Check is it the first user message to generate title
        const isFirstUserMessage = currentChat.messages.filter(msg => msg.role === 'user').length === 0;

        try {
            // Generate title if first message
            /* // Temporarily disabled title generation until backend is ready
            if (isFirstUserMessage) {
                 generateTitle(userMessage).then(title => {
                    if (title) {
                        setChats(prev => prev.map(chat => 
                            chat.id === activeChat 
                                ? { ...chat, title: title }
                                : chat
                        ));
                    }
                });
            }
            */

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
                    onClearAll={clearAllChats}
                />
                <div className="main-content">
                    <div className="chat-container">
                        <div className="chat-messages">
                            {messages.map((msg, index) => (
                                <ChatMessage key={index} message={msg} />
                            ))}
                            {loading && (
                                <div className="message assistant">
                                    <div className="message-avatar">
                                        <img
                                            src="/rupay-logo.png"
                                            alt="RuPay"
                                            style={{ width: '100%', height: '100%', objectFit: 'contain', padding: '4px' }}
                                        />
                                    </div>
                                    <div className="message-content">
                                        <div className="rupay-loader">
                                            <span></span>
                                            <span></span>
                                            <span></span>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                        <ChatInput onSend={handleSendMessage} disabled={loading} />
                    </div>
                </div>

            </div>
        </>
    );
}

export default App;
