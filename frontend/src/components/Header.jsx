import React from 'react';
import { useTheme } from '../context/ThemeContext';

function Header() {
    const { theme, setTheme } = useTheme();

    return (
        <header className="header">
            <div className="header-content">
                <img
                    src="/rupay-logo.png"
                    alt="RuPay"
                    style={{ height: '40px', objectFit: 'contain' }}
                />
                <div style={{ flex: 1 }}>
                    <h1 className="header-title">RuPay Agent</h1>
                    <p className="header-subtitle">AI-Powered Transaction Assistant</p>
                </div>
                <div className="theme-toggle">
                    <select
                        value={theme}
                        onChange={(e) => setTheme(e.target.value)}
                        style={{
                            padding: '0.5rem',
                            borderRadius: '8px',
                            border: '1px solid var(--border-color)',
                            background: 'var(--bg-secondary)',
                            color: 'var(--text-primary)',
                            cursor: 'pointer',
                            outline: 'none'
                        }}
                    >
                        <option value="light">☀️ Light</option>
                        <option value="dark">🌙 Dark</option>
                        <option value="system">🖥️ System</option>
                    </select>
                </div>
            </div>
        </header>
    );
}

export default Header;
