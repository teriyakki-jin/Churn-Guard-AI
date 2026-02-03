import React, { useState, createContext, useContext, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';

const ToastContext = createContext();

export const useToast = () => useContext(ToastContext);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
};

const ToastContainer = ({ toasts, removeToast }) => {
  const getIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle size={18} />;
      case 'error': return <XCircle size={18} />;
      case 'warning': return <AlertCircle size={18} />;
      default: return <Info size={18} />;
    }
  };

  const getStyle = (type) => {
    switch (type) {
      case 'success': return { background: 'rgba(16, 185, 129, 0.95)', borderColor: '#10b981' };
      case 'error': return { background: 'rgba(244, 63, 94, 0.95)', borderColor: '#f43f5e' };
      case 'warning': return { background: 'rgba(251, 191, 36, 0.95)', borderColor: '#fbbf24', color: '#1e293b' };
      default: return { background: 'rgba(99, 102, 241, 0.95)', borderColor: '#6366f1' };
    }
  };

  return (
    <div style={{
      position: 'fixed', top: '20px', right: '20px', zIndex: 9999,
      display: 'flex', flexDirection: 'column', gap: '10px'
    }}>
      <AnimatePresence>
        {toasts.map(toast => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, x: 100, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.9 }}
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              color: '#fff',
              fontSize: '0.9rem',
              boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
              cursor: 'pointer',
              maxWidth: '350px',
              ...getStyle(toast.type)
            }}
            onClick={() => removeToast(toast.id)}
          >
            {getIcon(toast.type)}
            <span>{toast.message}</span>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default ToastProvider;
