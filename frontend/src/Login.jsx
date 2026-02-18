import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from './AuthContext';
import { useToast } from './ToastContext';
import { Lock, User, Mail } from 'lucide-react';
import axios from 'axios';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const [isRegister, setIsRegister] = useState(false);
    const { login } = useAuth();
    const { addToast } = useToast();
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        if (isRegister) {
            try {
                await axios.post('/api/register', { username, email, password });
                addToast('회원가입 성공! 로그인해주세요.', 'success');
                setIsRegister(false);
                setEmail('');
            } catch (err) {
                const detail = err.response?.data?.detail ?? '회원가입에 실패했습니다.';
                setError(detail);
                addToast(`회원가입 실패: ${detail}`, 'error');
            }
        } else {
            try {
                const success = await login(username, password);
                if (!success) {
                    setError('Invalid credentials');
                    addToast('로그인 실패: 잘못된 자격 증명', 'error');
                } else {
                    addToast('로그인 성공! 환영합니다.', 'success');
                }
            } catch (err) {
                const msg = typeof err === "string" ? err : (err?.message ?? "Invalid credentials");
                setError(msg);
                addToast(`로그인 오류: ${msg}`, 'error');
            }
        }
        setIsLoading(false);
    };

    const inputStyle = {
        width: '100%',
        padding: '12px 12px 12px 45px',
        background: 'rgba(0, 0, 0, 0.2)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '8px',
        color: 'white',
        outline: 'none',
        fontSize: '1rem'
    };

    return (
        <div style={{
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'radial-gradient(circle at top left, #1e1b4b, #0f172a)',
            color: 'white',
            fontFamily: "'Inter', sans-serif"
        }}>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                style={{
                    width: '100%',
                    maxWidth: '400px',
                    padding: '2rem',
                    background: 'rgba(255, 255, 255, 0.03)',
                    backdropFilter: 'blur(20px)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '16px',
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
                }}
            >
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <h2 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem', background: 'linear-gradient(to right, #6366f1, #ec4899)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                        {isRegister ? 'Create Account' : 'Welcome Back'}
                    </h2>
                    <p style={{ color: '#94a3b8' }}>
                        {isRegister ? 'Fill in the details to sign up' : 'Please sign in to continue'}
                    </p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '1.5rem' }}>
                        <div style={{ position: 'relative' }}>
                            <User size={20} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                            <input
                                type="text"
                                placeholder="Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                style={inputStyle}
                            />
                        </div>
                    </div>

                    {isRegister && (
                        <div style={{ marginBottom: '1.5rem' }}>
                            <div style={{ position: 'relative' }}>
                                <Mail size={20} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                                <input
                                    type="email"
                                    placeholder="Email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    style={inputStyle}
                                />
                            </div>
                        </div>
                    )}

                    <div style={{ marginBottom: '2rem' }}>
                        <div style={{ position: 'relative' }}>
                            <Lock size={20} color="#94a3b8" style={{ position: 'absolute', left: '12px', top: '12px' }} />
                            <input
                                type="password"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                style={inputStyle}
                            />
                        </div>
                    </div>

                    {error && (
                        <div style={{ color: '#f43f5e', marginBottom: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={isLoading}
                        style={{
                            width: '100%',
                            padding: '12px',
                            background: 'linear-gradient(to right, #6366f1, #8b5cf6)',
                            border: 'none',
                            borderRadius: '8px',
                            color: 'white',
                            fontSize: '1rem',
                            fontWeight: '600',
                            cursor: 'pointer',
                            opacity: isLoading ? 0.7 : 1,
                            transition: 'opacity 0.2s'
                        }}
                    >
                        {isLoading ? (isRegister ? 'Creating...' : 'Signing in...') : (isRegister ? 'Sign Up' : 'Sign In')}
                    </button>
                </form>

                <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
                    <span style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
                        {isRegister ? 'Already have an account? ' : "Don't have an account? "}
                    </span>
                    <button
                        onClick={() => { setIsRegister(!isRegister); setError(''); }}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: '#6366f1',
                            cursor: 'pointer',
                            fontSize: '0.9rem',
                            fontWeight: '600',
                            textDecoration: 'underline'
                        }}
                    >
                        {isRegister ? 'Sign In' : 'Sign Up'}
                    </button>
                </div>
            </motion.div>
        </div>
    );
};

export default Login;
