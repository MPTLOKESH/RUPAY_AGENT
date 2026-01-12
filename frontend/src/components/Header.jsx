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
                        {theme === 'dark' ? (
                            // Sun Icon for Dark Mode (to switch to light)
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="12" cy="12" r="5"></circle>
                                <line x1="12" y1="1" x2="12" y2="3"></line>
                                <line x1="12" y1="21" x2="12" y2="23"></line>
                                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                                <line x1="1" y1="12" x2="3" y2="12"></line>
                                <line x1="21" y1="12" x2="23" y2="12"></line>
                                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                            </svg>
                        ) : (
                            // Moon Icon for Light Mode (to switch to dark)
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                            </svg>
                        )}
                    </button>
                </div>
            </div>
        </header>
    );
}

export default Header;
