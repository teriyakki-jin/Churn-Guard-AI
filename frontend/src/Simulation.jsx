import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, RefreshCw, Users, AlertTriangle, TrendingUp, Activity } from 'lucide-react';
import { useToast } from './ToastContext';

const API_URL = '/api';
const WS_URL = `ws://${window.location.hostname}:8002/api/ws/simulation`;

const Simulation = () => {
  const { addToast } = useToast();
  const [isRunning, setIsRunning] = useState(false);
  const [predictions, setPredictions] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    highRisk: 0,
    avgProbability: 0
  });
  const [interval, setInterval] = useState(2);
  const wsRef = useRef(null);
  const maxPredictions = 50;

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const token = localStorage.getItem('token');
    const ws = new WebSocket(`${WS_URL}?interval=${interval}&token=${token}`);

    ws.onopen = () => {
      addToast('시뮬레이션 연결됨', 'success');
      setIsRunning(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'prediction') {
        setPredictions(prev => {
          const updated = [data, ...prev].slice(0, maxPredictions);
          return updated;
        });

        // Update stats
        setStats(prev => {
          const newTotal = prev.total + 1;
          const isHighRisk = data.prediction.churn_probability > 0.5;
          const newHighRisk = prev.highRisk + (isHighRisk ? 1 : 0);
          const newAvg = ((prev.avgProbability * prev.total) + data.prediction.churn_probability) / newTotal;
          return {
            total: newTotal,
            highRisk: newHighRisk,
            avgProbability: newAvg
          };
        });
      }
    };

    ws.onerror = () => {
      addToast('WebSocket 연결 오류', 'error');
    };

    ws.onclose = () => {
      setIsRunning(false);
    };

    wsRef.current = ws;
  }, [interval, addToast]);

  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setIsRunning(false);
      addToast('시뮬레이션 중지됨', 'info');
    }
  }, [addToast]);

  const toggleSimulation = () => {
    if (isRunning) {
      disconnectWebSocket();
    } else {
      connectWebSocket();
    }
  };

  const resetStats = () => {
    setPredictions([]);
    setStats({ total: 0, highRisk: 0, avgProbability: 0 });
    addToast('통계 초기화됨', 'info');
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const getRiskColor = (prob) => {
    if (prob > 0.7) return '#f43f5e';
    if (prob > 0.5) return '#f59e0b';
    if (prob > 0.3) return '#eab308';
    return '#10b981';
  };

  const getRiskBg = (prob) => {
    if (prob > 0.7) return 'rgba(244, 63, 94, 0.1)';
    if (prob > 0.5) return 'rgba(245, 158, 11, 0.1)';
    if (prob > 0.3) return 'rgba(234, 179, 8, 0.1)';
    return 'rgba(16, 185, 129, 0.1)';
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="main-content"
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1>실시간 이탈 예측 시뮬레이션</h1>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <select
            value={interval}
            onChange={(e) => setInterval(Number(e.target.value))}
            disabled={isRunning}
            style={{
              padding: '0.5rem 1rem',
              background: 'var(--glass)',
              border: '1px solid var(--glass-border)',
              borderRadius: '8px',
              color: 'white',
              cursor: isRunning ? 'not-allowed' : 'pointer'
            }}
          >
            <option value={0.5}>0.5초</option>
            <option value={1}>1초</option>
            <option value={2}>2초</option>
            <option value={5}>5초</option>
          </select>
          <button
            onClick={toggleSimulation}
            style={{
              padding: '0.5rem 1.5rem',
              background: isRunning ? 'var(--accent)' : 'var(--primary)',
              border: 'none',
              borderRadius: '8px',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: 'bold'
            }}
          >
            {isRunning ? <><Pause size={18} /> 중지</> : <><Play size={18} /> 시작</>}
          </button>
          <button
            onClick={resetStats}
            style={{
              padding: '0.5rem 1rem',
              background: 'var(--glass)',
              border: '1px solid var(--glass-border)',
              borderRadius: '8px',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
            <Users size={18} /> 분석된 고객
          </div>
          <div className="stat-value">{stats.total}</div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
            <AlertTriangle size={18} /> 고위험 고객
          </div>
          <div className="stat-value" style={{ color: 'var(--accent)' }}>
            {stats.highRisk}
            <span style={{ fontSize: '1rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
              ({stats.total > 0 ? ((stats.highRisk / stats.total) * 100).toFixed(1) : 0}%)
            </span>
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
            <TrendingUp size={18} /> 평균 이탈 확률
          </div>
          <div className="stat-value" style={{ color: getRiskColor(stats.avgProbability) }}>
            {(stats.avgProbability * 100).toFixed(1)}%
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
            <Activity size={18} /> 상태
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            marginTop: '0.5rem'
          }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: isRunning ? '#10b981' : '#64748b',
              animation: isRunning ? 'pulse 1.5s infinite' : 'none'
            }} />
            <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
              {isRunning ? '실행 중' : '대기'}
            </span>
          </div>
        </div>
      </div>

      {/* Live Feed */}
      <div className="card" style={{ height: '500px', overflow: 'hidden' }}>
        <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={20} /> 실시간 예측 피드
          {isRunning && (
            <span style={{
              fontSize: '0.75rem',
              padding: '2px 8px',
              background: 'var(--success)',
              borderRadius: '10px',
              marginLeft: 'auto'
            }}>LIVE</span>
          )}
        </h3>

        <div style={{
          height: 'calc(100% - 40px)',
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
          <AnimatePresence mode="popLayout">
            {predictions.length === 0 ? (
              <div style={{
                textAlign: 'center',
                color: 'var(--text-muted)',
                padding: '3rem'
              }}>
                시뮬레이션을 시작하면 실시간 예측이 표시됩니다
              </div>
            ) : (
              predictions.map((pred, idx) => (
                <motion.div
                  key={pred.customer_id}
                  initial={{ opacity: 0, x: -50, height: 0 }}
                  animate={{ opacity: 1, x: 0, height: 'auto' }}
                  exit={{ opacity: 0, x: 50 }}
                  transition={{ duration: 0.3 }}
                  style={{
                    padding: '0.75rem 1rem',
                    background: getRiskBg(pred.prediction.churn_probability),
                    borderRadius: '8px',
                    borderLeft: `4px solid ${getRiskColor(pred.prediction.churn_probability)}`,
                    display: 'grid',
                    gridTemplateColumns: '120px 1fr 100px 120px',
                    alignItems: 'center',
                    gap: '1rem',
                    fontSize: '0.9rem'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 'bold', color: 'var(--primary)' }}>
                      {pred.customer_id}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {pred.profile}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    <span style={{ color: 'var(--text-muted)' }}>
                      계약: <strong style={{ color: 'white' }}>{pred.customer_data.contract}</strong>
                    </span>
                    <span style={{ color: 'var(--text-muted)' }}>
                      결제: <strong style={{ color: 'white' }}>{pred.customer_data.payment.split(' ')[0]}</strong>
                    </span>
                    <span style={{ color: 'var(--text-muted)' }}>
                      기간: <strong style={{ color: 'white' }}>{pred.customer_data.tenure}개월</strong>
                    </span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{
                      fontWeight: 'bold',
                      fontSize: '1.1rem',
                      color: getRiskColor(pred.prediction.churn_probability)
                    }}>
                      {(pred.prediction.churn_probability * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div style={{
                    textAlign: 'center',
                    padding: '0.25rem 0.5rem',
                    background: getRiskColor(pred.prediction.churn_probability),
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    fontSize: '0.8rem'
                  }}>
                    {pred.prediction.risk_level}
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </motion.div>
  );
};

export default Simulation;
