import React from 'react';

const WelcomeScreen = () => {
    return (
        <div className="welcome-screen">
            <div className="welcome-content">
                <div className="welcome-logo">
                    <img
                        src="/rupay-logo.png"
                        alt="RuPay"
                        className="welcome-logo-img"
                    />
                </div>
                <h1 className="welcome-title">Welcome to RuPay Assistant</h1>
                <p className="welcome-subtitle">
                    Your AI-powered guide for seamless transactions.
                    <br />How can I help you today?
                </p>
            </div>
        </div>
    );
};

export default WelcomeScreen;
