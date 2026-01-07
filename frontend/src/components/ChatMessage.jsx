import React from 'react';

function ChatMessage({ message }) {
    const isUser = message.role === 'user';

    return (
        <div className={`message ${message.role}`}>
            <div className="message-avatar">
                {isUser ? '👤' : '🤖'}
            </div>
            <div className="message-content">
                <div className="message-text">
                    {message.content}
                </div>
            </div>
        </div>
    );
}

export default ChatMessage;
