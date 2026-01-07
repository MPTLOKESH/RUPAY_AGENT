import React, { useState } from 'react';

function ChatInput({ onSend, disabled }) {
    const [input, setInput] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim() && !disabled) {
            onSend(input);
            setInput('');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="chat-input-container">
            <input
                type="text"
                className="chat-input"
                placeholder="Type your message here..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={disabled}
            />
            <button type="submit" className="send-button" disabled={disabled || !input.trim()}>
                Send
                <span>Send</span>
            </button>
        </form>
    );
}

export default ChatInput;
