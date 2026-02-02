import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

// Initialize axios header synchronously before any component renders
const storedToken = localStorage.getItem('token');
if (storedToken) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
}

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(storedToken ? { username: 'admin' } : null);
    const [token, setToken] = useState(storedToken);

    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            setUser({ username: 'admin' });
        } else {
            delete axios.defaults.headers.common['Authorization'];
            setUser(null);
        }
    }, [token]);

    const login = async (username, password) => {
        const body = new URLSearchParams({ username, password }).toString();

        try {
            const res = await axios.post('/api/token', body, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            const access_token = res.data.access_token;
            setToken(access_token);
            localStorage.setItem('token', access_token);
            return true;
        } catch (error) {
            console.error("Login failed", error);
            if (error.code === "ERR_NETWORK" || error.message === "Network Error") {
                throw "백엔드에 연결할 수 없습니다. 터미널에서 백엔드(8000)가 실행 중인지 확인하세요.";
            }
            const raw = error.response?.data?.detail ?? error.message ?? "Login failed";
            const msg = Array.isArray(raw)
                ? raw.map((e) => e?.msg ?? e).join(", ")
                : typeof raw === "string"
                    ? raw
                    : String(raw?.detail ?? raw ?? "Invalid credentials");
            throw msg;
        }
    };

    const logout = () => {
        setToken(null);
        localStorage.removeItem('token');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
