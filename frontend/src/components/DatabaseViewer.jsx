import React, { useState, useEffect } from 'react';
import { fetchDatabase } from '../services/api';

function DatabaseViewer() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isMaximized, setIsMaximized] = useState(false);

    const handleRefresh = async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await fetchDatabase();
            setData(result);
        } catch (err) {
            setError(err.message || 'Failed to fetch database');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        handleRefresh();
    }, []);

    return (
        <div className={`sidebar ${isMaximized ? 'maximized' : ''}`}>
            <div className="sidebar-header">
                <div className="sidebar-title">
                    <span>📊</span>
                    Live Database
                </div>
                <div className="sidebar-actions">
                    <button
                        onClick={() => setIsMaximized(!isMaximized)}
                        className="maximize-button"
                        title={isMaximized ? 'Minimize' : 'Maximize'}
                    >
                        {isMaximized ? '◧' : '⛶'}
                    </button>
                    <button
                        onClick={handleRefresh}
                        className={`refresh-button ${loading ? 'loading' : ''}`}
                        disabled={loading}
                    >
                        Refresh
                    </button>
                </div>
            </div>

            <div className="sidebar-content">
                {error ? (
                    <div className="error-message">
                        {error}
                    </div>
                ) : !data ? (
                    <div className="info-message">
                        Loading transaction data...
                    </div>
                ) : data.length === 0 ? (
                    <div className="info-message">
                        No transactions found.
                    </div>
                ) : (
                    <table className="database-table">
                        <thead>
                            <tr>
                                {Object.keys(data[0]).map((key) => (
                                    <th key={key}>
                                        {key.replace(/_/g, ' ').toUpperCase()}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((row, index) => (
                                <tr key={index}>
                                    {Object.values(row).map((value, i) => (
                                        <td key={i}>
                                            {typeof value === 'string' && (value === 'Success' || value === 'Failed') ? (
                                                <span className={`status-badge ${value === 'Success' ? 'status-success' : 'status-failed'}`}>
                                                    {value}
                                                </span>
                                            ) : (
                                                value
                                            )}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

export default DatabaseViewer;
