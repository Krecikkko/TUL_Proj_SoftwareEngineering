import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginScreen from './LoginScreen';
import SignupScreen from './SignupScreen';
import AdminDashboard from './AdminDashboard';
import UserDashboard from './UserDashboard';
import EngineerDashboard from './EngineerDashboard'; // <--- NOWOŚĆ

const App = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LoginScreen />} />
                <Route path="/signup" element={<SignupScreen />} />
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/user" element={<UserDashboard />} />
                <Route path="/engineer" element={<EngineerDashboard />} /> {/* <--- NOWA TRASA */}
            </Routes>
        </BrowserRouter>
    );
};

export default App;