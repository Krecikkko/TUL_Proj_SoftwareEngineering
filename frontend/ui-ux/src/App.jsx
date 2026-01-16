import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginScreen from './LoginScreen';
import SignupScreen from './SignupScreen'; // <--- IMPORT
import Dashboard from './Dashboard';
import UserDashboard from './UserDashboard';   // Importujemy
import AdminDashboard from './AdminDashboard';

const App = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LoginScreen />} />
                <Route path="/signup" element={<SignupScreen />} /> {/* <--- NOWA TRASA */}
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/user" element={<UserDashboard />} />
            </Routes>
        </BrowserRouter>
    );
};

export default App;