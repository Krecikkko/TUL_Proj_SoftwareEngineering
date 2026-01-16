import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
    const navigate = useNavigate();

    // Weryfikacja uprawnień: przekierowanie do logowania jeśli brak flagi autoryzacji
    useEffect(() => {
        const isLoggedIn = localStorage.getItem('isAuthenticated');
        if (!isLoggedIn) {
            navigate('/');
        }
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('isAuthenticated');
        navigate('/');
    };

    return (
        <div style={{ padding: '50px', fontFamily: 'Arial, sans-serif' }}>
            <h1>Witaj w systemie! 🎉</h1>
            <p>To jest tajny panel dostępny tylko po zalogowaniu.</p>

            <div style={{ marginTop: '20px', padding: '20px', backgroundColor: '#d1fae5', borderRadius: '8px' }}>
                <h3 style={{ margin: 0 }}>🔒 Status bezpieczeństwa:</h3>
                <p>Jesteś autoryzowany. Odśwież stronę - nadal tu będziesz!</p>
            </div>

            <button
                onClick={handleLogout}
                style={{
                    marginTop: '30px',
                    padding: '10px 20px',
                    backgroundColor: '#c53030',
                    color: 'white',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer'
                }}
            >
                Wyloguj się
            </button>
        </div>
    );
};

export default Dashboard;