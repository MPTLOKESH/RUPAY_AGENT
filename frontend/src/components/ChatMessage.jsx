import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function ChatMessage({ message }) {
    const isUser = message.role === 'user';

    return (
        <div className={`message ${message.role}`}>
            <div className="message-avatar">
                {isUser ? (
                    <span>U</span>
                ) : (
                    <img
                        src="/rupay-logo.png"
                        alt="RuPay"
                        style={{ width: '100%', height: '100%', objectFit: 'contain', padding: '4px' }}
                    />
                )}
            </div>
            <div className="message-content">
                <div className="message-text">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                    </ReactMarkdown>
                </div>
            </div>
        </div>
    );
}

export default ChatMessage;
