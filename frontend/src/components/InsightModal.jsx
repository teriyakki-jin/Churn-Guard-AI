import { motion } from 'framer-motion';

const InsightModal = ({ insight, onClose }) => {
  if (!insight) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }} onClick={onClose}>
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="card"
        style={{
          maxWidth: '700px',
          width: '100%',
          maxHeight: '80vh',
          overflow: 'auto',
          position: 'relative'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '15px',
            right: '15px',
            background: 'var(--glass)',
            border: '1px solid var(--glass-border)',
            borderRadius: '50%',
            width: '30px',
            height: '30px',
            cursor: 'pointer',
            color: 'white',
            fontSize: '18px'
          }}
        >
          ×
        </button>

        <h2 style={{ marginBottom: '1.5rem', color: insight.color }}>{insight.title}</h2>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>📊 현황 분석</h3>
          <p style={{ color: 'var(--text-muted)', lineHeight: '1.6' }}>{insight.analysis}</p>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>💡 권장 전략</h3>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '15px', borderRadius: '8px' }}>
            <p style={{ lineHeight: '1.6' }}>{insight.strategy}</p>
          </div>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>📈 예상 효과</h3>
          <ul style={{ paddingLeft: '20px', color: 'var(--text-muted)' }}>
            {insight.effects.map((effect, i) => (
              <li key={i} style={{ marginBottom: '0.5rem' }}>{effect}</li>
            ))}
          </ul>
        </div>

        <div style={{ background: 'rgba(99, 102, 241, 0.1)', padding: '15px', borderRadius: '8px', borderLeft: '4px solid var(--primary)' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>🎯 실행 방안</h3>
          <ol style={{ paddingLeft: '20px', color: 'var(--text-muted)' }}>
            {insight.actions.map((action, i) => (
              <li key={i} style={{ marginBottom: '0.5rem' }}>{action}</li>
            ))}
          </ol>
        </div>
      </motion.div>
    </div>
  );
};

export default InsightModal;
