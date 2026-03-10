import { motion } from 'framer-motion';
import { Users, Activity } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';

const COLORS = ['#10b981', '#f43f5e'];

const Dashboard = ({ stats }) => {
  if (!stats) return <div className="fade-in">Loading insights...</div>;

  const pieData = [
    { name: 'Stayed', value: (stats.overall_churn_rate?.No || 0.73) * 100 },
    { name: 'Churned', value: (stats.overall_churn_rate?.Yes || 0.27) * 100 },
  ];

  const contractData = stats.contract_impact ? Object.keys(stats.contract_impact).map(key => {
    const val = stats.contract_impact[key];
    const churn = typeof val === 'object' ? (val.Yes * 100) : val;
    return { name: key, churn: parseFloat(churn).toFixed(1) };
  }) : [];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="main-content">
      <h1 style={{ marginBottom: '2rem' }}>Revenue Insights & Retention</h1>

      <div className="grid">
        <div className="card">
          <div style={{ display: 'flex', gap: '0.5rem', color: 'var(--text-muted)' }}><Users size={16} /> Total Customers</div>
          <div className="stat-value">{stats.total_customers}</div>
          <div style={{ color: 'var(--success)', fontSize: '0.9rem' }}>+2.4% from last month</div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', gap: '0.5rem', color: 'var(--text-muted)' }}><Activity size={16} /> Churn Rate</div>
          <div className="stat-value">{((stats.overall_churn_rate?.Yes || 0) * 100).toFixed(1)}%</div>
          <div style={{ color: 'var(--accent)', fontSize: '0.9rem' }}>Critical focus needed</div>
        </div>
      </div>

      <div className="grid" style={{ marginTop: '1.5rem' }}>
        <div className="card" style={{ height: '400px' }}>
          <h3>Churn by Contract Type (%)</h3>
          <ResponsiveContainer width="100%" height="80%">
            <BarChart data={contractData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid var(--glass-border)' }}
                itemStyle={{ color: '#fff' }}
              />
              <Bar dataKey="churn" fill="var(--accent)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card" style={{ height: '400px' }}>
          <h3>Customer Retention Status</h3>
          <ResponsiveContainer width="100%" height="80%">
            <PieChart>
              <Pie
                data={pieData}
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', fontSize: '0.9rem' }}>
            <span style={{ color: '#10b981' }}>● Stayed</span>
            <span style={{ color: '#f43f5e' }}>● Churned</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
