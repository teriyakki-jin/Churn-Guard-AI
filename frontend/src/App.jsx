import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AnimatePresence } from 'framer-motion';
import { AuthProvider, useAuth } from './AuthContext';
import { ToastProvider } from './ToastContext';
import Login from './Login';
import Simulation from './Simulation';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Strategy from './components/Strategy';
import Predictor from './components/Predictor';

const API_URL = '/api';

const MainContent = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;
      const config = { headers: { Authorization: `Bearer ${token}` } };
      try {
        const [resStats, resAnalysis] = await Promise.all([
          axios.get(`${API_URL}/stats`, config),
          axios.get(`${API_URL}/analysis`, config)
        ]);
        setStats(resStats.data);
        setAnalysis(resAnalysis.data);
      } catch (err) {
        console.error('Failed to fetch data', err);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <AnimatePresence mode="wait">
        {activeTab === 'dashboard' && <Dashboard key="dash" stats={stats} />}
        {activeTab === 'strategy' && <Strategy key="strat" stats={stats} analysis={analysis} />}
        {activeTab === 'predictor' && <Predictor key="pred" />}
        {activeTab === 'simulation' && <Simulation key="sim" />}
      </AnimatePresence>
    </div>
  );
};

const AppContent = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <MainContent /> : <Login />;
};

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
