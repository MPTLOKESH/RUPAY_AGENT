import React from 'react';
import { useTheme } from '../context/ThemeContext';



function Header() {
    const { theme, setTheme } = useTheme();

    const toggleTheme = () => {
        setTheme(theme === 'dark' ? 'light' : 'dark');
    };

    return (
        <header className="header">
            <div className="header-content">
                <a href="https://www.npci.org.in/product/rupay" target="_blank" rel="noopener noreferrer">
                    <img
                        src="/rupay-logo.png"
                        alt="RuPay"
                        style={{ height: '40px', objectFit: 'contain', cursor: 'pointer' }}
                    />
                </a>
                <div style={{ flex: 1 }}>
                    <h1 className="header-title">RuPay Agent</h1>
                    <p className="header-subtitle">AI-Powered Transaction Assistant</p>
                </div>

                <div className="theme-selector">
                    <button
                        className="theme-btn"
                        onClick={toggleTheme}
                        title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
                    >
                        <span>{theme === 'dark' ? '☀️' : '🌙'}</span>
                    </button>
                </div>
            </div>
        </header>
    );
}

export default Header;
