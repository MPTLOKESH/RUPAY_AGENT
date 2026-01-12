import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ChatHistory from './components/ChatHistory';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import { sendMessage, getHistory, clearHistory } from './services/api';
import ConfirmationModal from './components/ConfirmationModal';
import WelcomeScreen from './components/WelcomeScreen';

const STORAGE_KEY = 'rupay_chat_sessions'; // Renamed to reflect it stores sessions, not full history

function App() {
    const [chats, setChats] = useState([]);
    const [activeChat, setActiveChat] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isClearModalOpen, setIsClearModalOpen] = useState(false);
    const messagesEndRef = useRef(null);
    const initializedRef = useRef(false);

    // Initialize chats from localStorage or create first chat
    useEffect(() => {
        const loadInitialChats = async () => {
            if (initializedRef.current) return;
            initializedRef.current = true;

            const savedChats = localStorage.getItem(STORAGE_KEY);
            let initialChatId = null;

            if (savedChats) {
                const parsedChats = JSON.parse(savedChats);
                // We only need the metadata (ids), messages will be fetched
                setChats(parsedChats.map(c => ({ ...c, messages: [] })));
                initialChatId = parsedChats[0]?.id;
            } else {
                initialChatId = createNewChat(true); // pass flag to indicate return only
            }

            if (initialChatId) {
                setActiveChat(initialChatId);
                await fetchChatHistory(initialChatId);
            }
        };
        loadInitialChats();
    }, []);

    const fetchChatHistory = async (chatId) => {
        setLoading(true);
        try {
            const data = await getHistory(chatId);
            // Backend now returns { history: [...], title: "..." }
            const history = data.history || [];
            const title = data.title;

            setChats(prev => prev.map(chat =>
                chat.id === chatId
                    ? { ...chat, messages: history, title: title || chat.title || 'New Chat' }
                    : chat
            ));
        } catch (error) {
            console.error("Failed to load history", error);
        } finally {
            setLoading(false);
        }
    };

    // When active chat changes, fetch history if empty (or always to sync?)
    // For now, let's fetch on select to ensure fresh data
    useEffect(() => {
        if (activeChat) {
            fetchChatHistory(activeChat);
        }
    }, [activeChat]);

    // Save chats METADATA to localStorage (excluding messages to keep it light/synced with source of truth)
    useEffect(() => {
        if (chats.length > 0) {
            // Strip messages before saving to local storage
            const chatsMetadata = chats.map(({ messages, ...rest }) => ({ ...rest, messages: [] }));
            localStorage.setItem(STORAGE_KEY, JSON.stringify(chatsMetadata));
        }
    }, [chats]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const getCurrentChat = () => {
        return chats.find(chat => chat.id === activeChat);
    };

    const createNewChat = (returnIdOnly = false) => {
        // Check if the LATEST chat (index 0) is already empty to prevent duplicates
        if (chats.length > 0) {
            const latestChat = chats[0];
            const isEmpty = latestChat.messages.length === 0 || (latestChat.messages.length === 1 && latestChat.messages[0].role === 'assistant');

            if (isEmpty && !returnIdOnly) {
                setActiveChat(latestChat.id);
                return;
            }
        }


        const newChat = {
            id: Date.now().toString(),
            timestamp: Date.now(),
            messages: []
            // We initiate with empty. Backend/Frontend default greeting logic can be handled by UI
        };

        // Add default greeting locally
        newChat.messages = [];

        if (returnIdOnly) {
            setChats(prev => [newChat, ...prev]);
            return newChat.id;
        }

        setChats(prev => [newChat, ...prev]);
        setActiveChat(newChat.id);
    };

    const selectChat = (chatId) => {
        setActiveChat(chatId);
    };

    const deleteChat = (chatId) => {
        const updatedChats = chats.filter(chat => chat.id !== chatId);

        // Clear from Redis
        clearHistory(chatId);

        if (updatedChats.length > 0) {
            setChats(updatedChats);
            // If the deleted chat was the active one, switch to the first available
            if (chatId === activeChat) {
                setActiveChat(updatedChats[0].id);
            }
        } else {
            // If no chats left, create a fresh one immediately explicitly
            // We don't use createNewChat() here to avoid reading stale 'chats' state
            const newChat = {
                id: Date.now().toString(),
                timestamp: Date.now(),
                messages: []
            };
            setChats([newChat]);
            setActiveChat(newChat.id);
        }
    };

    const confirmClearAllChats = () => {
        setIsClearModalOpen(true);
    };

    const handleClearConfirm = () => {
        const newChat = {
            id: Date.now().toString(),
            timestamp: Date.now(),
            title: 'New Chat',
            messages: []
        };
        setChats([newChat]);
        setActiveChat(newChat.id);
        localStorage.removeItem(STORAGE_KEY);
        setIsClearModalOpen(false);
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
            // Pass activeChat as sessionId
            const response = await sendMessage(userMessage, activeChat);

            // Response from backend includes response string and title
            setChats(prev => prev.map(chat =>
                chat.id === activeChat
                    ? {
                        ...chat,
                        messages: [...newMessages, { role: 'assistant', content: response.response }],
                        timestamp: Date.now(),
                        title: response.title || chat.title || 'New Chat'
                    }
                    : chat
            ));
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
                    onClearAll={confirmClearAllChats}
                />
                <div className="main-content">
                    <div className="chat-container">
                        <div className="chat-messages">
                            {messages.length === 0 ? (
                                <WelcomeScreen onSuggestionClick={handleSendMessage} />
                            ) : (
                                <>
                                    {messages.map((msg, index) => (
                                        <ChatMessage key={index} message={msg} />
                                    ))}
                                </>
                            )}
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
                        <ChatInput key={activeChat} onSend={handleSendMessage} disabled={loading} />
                    </div>
                </div>

            </div>
            <ConfirmationModal
                isOpen={isClearModalOpen}
                onClose={() => setIsClearModalOpen(false)}
                onConfirm={handleClearConfirm}
                title="Clear All History"
                message="Are you sure you want to delete all chat history? This action cannot be undone."
            />
        </>
    );
}

export default App;
