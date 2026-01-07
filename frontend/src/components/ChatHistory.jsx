import React from 'react';

function ChatHistory({ chats, activeChat, onNewChat, onSelectChat, onDeleteChat }) {
    const formatDate = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffInHours = (now - date) / (1000 * 60 * 60);

        if (diffInHours < 24) {
            return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
        } else if (diffInHours < 48) {
            return 'Yesterday';
        } else {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }
    };

    const getChatTitle = (chat) => {
        if (chat.messages.length <= 1) {
            return 'New Chat';
        }
        const firstUserMessage = chat.messages.find(msg => msg.role === 'user');
        if (firstUserMessage) {
            return firstUserMessage.content.slice(0, 30) + (firstUserMessage.content.length > 30 ? '...' : '');
        }
        return 'New Chat';
    };

    return (
        <div className="chat-history">
            <div className="chat-history-header">
                <button className="new-chat-button" onClick={onNewChat}>
                    <span className="icon">+</span>
                    New Chat
                </button>
            </div>

            <div className="chat-history-list">
                {chats.map((chat) => (
                    <div
                        key={chat.id}
                        className={`chat-history-item ${chat.id === activeChat ? 'active' : ''}`}
                        onClick={() => onSelectChat(chat.id)}
                    >
                        <div className="chat-item-content">
                            <div className="chat-item-title">{getChatTitle(chat)}</div>
                            <div className="chat-item-date">{formatDate(chat.timestamp)}</div>
                        </div>
                        <button
                            className="chat-item-delete"
                            onClick={(e) => {
                                e.stopPropagation();
                                onDeleteChat(chat.id);
                            }}
                            title="Delete chat"
                        >
                            ×
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ChatHistory;
