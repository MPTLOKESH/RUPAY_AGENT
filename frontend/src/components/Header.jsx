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
                <a href="https://www.npci.org.in/product/rupay" target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
                    <img
                        src="/rupay-logo.png"
                        alt="RuPay"
                        style={{ height: '36px', width: 'auto', display: 'block' }}
                    />
                </a>
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', marginLeft: '1rem' }}>
                    <span className="header-subtitle" style={{ padding: 0, border: 'none', fontSize: '1rem', fontWeight: 500, color: 'var(--text-primary)' }}>
                        AI-Powered Transaction Assistant
                    </span>
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
