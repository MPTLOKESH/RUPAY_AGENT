import React from 'react';
import { useTheme } from '../context/ThemeContext';

import { useState, useRef, useEffect } from 'react';

function Header() {
    const { theme, setTheme } = useTheme();
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const themes = [
        { id: 'light', label: 'Light', icon: '☀️' },
        { id: 'dark', label: 'Dark', icon: '🌙' },
        { id: 'system', label: 'System', icon: '🖥️' }
    ];

    const currentTheme = themes.find(t => t.id === theme) || themes[2];

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

                <div className="theme-selector" ref={dropdownRef}>
                    <button
                        className="theme-btn"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        <span>{currentTheme.icon} {currentTheme.label}</span>
                        <span style={{ fontSize: '0.8em', opacity: 0.7 }}>▼</span>
                    </button>

                    {isOpen && (
                        <div className="theme-menu">
                            {themes.map(t => (
                                <button
                                    key={t.id}
                                    className={`theme-option ${theme === t.id ? 'active' : ''}`}
                                    onClick={() => {
                                        setTheme(t.id);
                                        setIsOpen(false);
                                    }}
                                >
                                    <span>{t.icon}</span>
                                    <span>{t.label}</span>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}

export default Header;
