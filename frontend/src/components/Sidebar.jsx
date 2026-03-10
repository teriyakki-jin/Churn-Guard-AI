import { LayoutDashboard, Lightbulb, UserCheck, Radio, LogOut } from 'lucide-react';
import { useAuth } from '../AuthContext';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const { logout } = useAuth();
  return (
    <div className="sidebar">
      <div style={{ padding: '0 1rem 2rem 1rem', fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary)' }}>
        ChurnGuard AI
      </div>
      <div className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
        <LayoutDashboard size={20} /> Dashboard
      </div>
      <div className={`nav-item ${activeTab === 'strategy' ? 'active' : ''}`} onClick={() => setActiveTab('strategy')}>
        <Lightbulb size={20} /> Strategy
      </div>
      <div className={`nav-item ${activeTab === 'predictor' ? 'active' : ''}`} onClick={() => setActiveTab('predictor')}>
        <UserCheck size={20} /> Predictor
      </div>
      <div className={`nav-item ${activeTab === 'simulation' ? 'active' : ''}`} onClick={() => setActiveTab('simulation')}>
        <Radio size={20} /> Simulation
      </div>
      <div style={{ marginTop: 'auto', cursor: 'pointer' }} className="nav-item" onClick={logout}>
        <LogOut size={20} /> Sign Out
      </div>
    </div>
  );
};

export default Sidebar;
