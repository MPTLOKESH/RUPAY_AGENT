import React, { useMemo, useState } from 'react';

function ChatHistory({ chats, activeChat, onNewChat, onSelectChat, onDeleteChat, onClearAll }) {
    const [isCollapsed, setIsCollapsed] = useState(false);

    // Helper to group chats by date
    const categorizedChats = useMemo(() => {
        const groups = {
            'Today': [],
            'Yesterday': [],
            'Previous 7 Days': [],
            'Older': []
        };

        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const last7Days = new Date(today);
        last7Days.setDate(last7Days.getDate() - 7);

        chats.forEach(chat => {
            const date = new Date(chat.timestamp);
            const chatDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

            if (chatDate.getTime() === today.getTime()) {
                groups['Today'].push(chat);
            } else if (chatDate.getTime() === yesterday.getTime()) {
                groups['Yesterday'].push(chat);
            } else if (chatDate > last7Days) {
                groups['Previous 7 Days'].push(chat);
            } else {
                groups['Older'].push(chat);
            }
        });

        // Sort: Newest first within groups
        Object.keys(groups).forEach(key => {
            groups[key].sort((a, b) => b.timestamp - a.timestamp);
        });

        return groups;
    }, [chats]);

    const getChatTitle = (chat) => {
        if (chat.title) return chat.title;

        if (!chat.messages || chat.messages.length === 0) return 'New Chat';

        // Use the first user message as title if available
        const firstUserMessage = chat.messages.find(msg => msg.role === 'user');
        if (firstUserMessage) {
            // Truncate to 30 chars
            return firstUserMessage.content.length > 30
                ? firstUserMessage.content.substring(0, 30) + '...'
                : firstUserMessage.content;
        }
        return 'New Chat';
    };

    const handleNewChat = () => {
        setIsCollapsed(false);
        onNewChat();
    };

    return (
        <div className={`chat-history ${isCollapsed ? 'collapsed' : ''}`}>
            <div className="chat-history-header">
                <button
                    className="sidebar-toggle"
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="3" y1="12" x2="21" y2="12"></line>
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <line x1="3" y1="18" x2="21" y2="18"></line>
                    </svg>
                </button>

                <button className="new-chat-button" onClick={handleNewChat} title="New Chat">
                    {isCollapsed ? (
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                    ) : (
                        <>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            New Chat
                        </>
                    )}
                </button>
            </div>

            <div className="chat-history-list">
                {Object.entries(categorizedChats).map(([category, items]) => (
                    items.length > 0 && (
                        <div key={category} className="history-group">
                            {!isCollapsed && <div className="history-group-label">{category}</div>}
                            {items.map(chat => (
                                <div
                                    key={chat.id}
                                    className={`chat-history-item ${activeChat === chat.id ? 'active' : ''}`}
                                    onClick={() => onSelectChat(chat.id)}
                                >
                                    <div className="chat-item-icon">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                                        </svg>
                                    </div>
                                    {!isCollapsed && (
                                        <>
                                            <div className="chat-item-text">
                                                {getChatTitle(chat)}
                                            </div>
                                            <button
                                                className="chat-item-delete-btn"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    onDeleteChat(chat.id);
                                                }}
                                                title="Delete Chat"
                                            >
                                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <path d="M18 6L6 18M6 6l12 12"></path>
                                                </svg>
                                            </button>
                                        </>
                                    )}
                                </div>
                            ))}
                        </div>
                    )
                ))}

                {chats.length === 0 && (
                    <div className="empty-state">
                        {!isCollapsed && <p>No chat history</p>}
                    </div>
                )}
            </div>

            <div className="chat-history-footer">
                <button
                    className="clear-history-btn"
                    onClick={onClearAll}
                    title="Clear All History"
                >
                    {isCollapsed ? (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    ) : (
                        <>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            </svg>
                            Clear History
                        </>
                    )}
                </button>


            </div>
        </div>
    );
}

export default ChatHistory;
