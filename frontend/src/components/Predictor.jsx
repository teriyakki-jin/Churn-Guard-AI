import { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { TrendingUp, AlertCircle, Lightbulb } from 'lucide-react';
import { useToast } from '../ToastContext';

const API_URL = '/api';

const DEFAULT_FORM = {
  gender: 'Female', SeniorCitizen: 0, Partner: 'No', Dependents: 'No',
  tenure: 1, PhoneService: 'Yes', MultipleLines: 'No', InternetService: 'Fiber optic',
  OnlineSecurity: 'No', OnlineBackup: 'No', DeviceProtection: 'No', TechSupport: 'No',
  StreamingTV: 'No', StreamingMovies: 'No', Contract: 'Month-to-month',
  PaperlessBilling: 'Yes', PaymentMethod: 'Electronic check',
  MonthlyCharges: 70.0, TotalCharges: 70.0
};

const Predictor = () => {
  const { addToast } = useToast();
  const [formData, setFormData] = useState(DEFAULT_FORM);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const set = (field) => (e) => {
    const raw = e.target.value;
    const value = field === 'SeniorCitizen' ? parseInt(raw)
      : field === 'tenure' ? (parseInt(raw) || 0)
      : (field === 'MonthlyCharges' || field === 'TotalCharges') ? (parseFloat(raw) || 0)
      : raw;
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/predict`, formData);
      setResult(res.data);
      const score = res.data.churn_risk_score;
      if (score > 0.7) {
        addToast(`위험: 이탈 확률 ${(score * 100).toFixed(1)}% - 즉시 조치 필요`, 'error', 6000);
      } else if (score > 0.5) {
        addToast(`주의: 이탈 확률 ${(score * 100).toFixed(1)}% - 관리 필요`, 'warning', 5000);
      } else {
        addToast(`분석 완료: 이탈 확률 ${(score * 100).toFixed(1)}%`, 'success');
      }
    } catch {
      addToast('서버 연결 오류가 발생했습니다.', 'error');
    }
    setLoading(false);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="main-content">
      <h1>고객 이탈 위험 예측 (AI)</h1>
      <div className="grid">
        <div className="card" style={{ flex: 2 }}>
          <form onSubmit={handleSubmit}>
            <h3 style={{ marginBottom: '1rem', fontSize: '1rem' }}>📋 기본 정보</h3>
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
              <div className="form-group">
                <label className="form-label">계약 형태</label>
                <select className="form-control" value={formData.Contract} onChange={set('Contract')}>
                  <option>Month-to-month</option>
                  <option>One year</option>
                  <option>Two year</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">결제 수단</label>
                <select className="form-control" value={formData.PaymentMethod} onChange={set('PaymentMethod')}>
                  <option>Electronic check</option>
                  <option>Mailed check</option>
                  <option>Bank transfer (automatic)</option>
                  <option>Credit card (automatic)</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">인터넷 서비스</label>
                <select className="form-control" value={formData.InternetService} onChange={set('InternetService')}>
                  <option>Fiber optic</option>
                  <option>DSL</option>
                  <option>No</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">가입 기간 (개월)</label>
                <input type="number" className="form-control" min="0" max="72" value={formData.tenure} onChange={set('tenure')} />
              </div>
              <div className="form-group">
                <label className="form-label">월 요금 ($)</label>
                <input type="number" className="form-control" min="0" step="0.01" value={formData.MonthlyCharges} onChange={set('MonthlyCharges')} />
              </div>
              <div className="form-group">
                <label className="form-label">총 청구액 ($)</label>
                <input type="number" className="form-control" min="0" step="0.01" value={formData.TotalCharges} onChange={set('TotalCharges')} />
              </div>
            </div>

            <button type="button" onClick={() => setShowAdvanced(!showAdvanced)} style={{
              background: 'transparent', border: '1px solid var(--glass-border)', color: 'var(--text-muted)',
              padding: '0.5rem 1rem', borderRadius: '6px', cursor: 'pointer', marginTop: '1rem', width: '100%'
            }}>
              {showAdvanced ? '▲ 고급 옵션 숨기기' : '▼ 고급 옵션 보기'}
            </button>

            {showAdvanced && (
              <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
                <h4 style={{ marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>👤 고객 정보</h4>
                <div className="grid" style={{ gridTemplateColumns: '1fr 1fr 1fr 1fr' }}>
                  {[
                    { label: '성별', field: 'gender', opts: ['Female', 'Male'] },
                    { label: '시니어', field: 'SeniorCitizen', opts: [{ v: 0, l: 'No' }, { v: 1, l: 'Yes' }] },
                    { label: '배우자', field: 'Partner', opts: ['No', 'Yes'] },
                    { label: '부양가족', field: 'Dependents', opts: ['No', 'Yes'] },
                  ].map(({ label, field, opts }) => (
                    <div key={field} className="form-group">
                      <label className="form-label">{label}</label>
                      <select className="form-control" value={formData[field]} onChange={set(field)}>
                        {opts.map((o) => typeof o === 'object'
                          ? <option key={o.v} value={o.v}>{o.l}</option>
                          : <option key={o}>{o}</option>
                        )}
                      </select>
                    </div>
                  ))}
                </div>

                <h4 style={{ marginTop: '1rem', marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>📞 서비스 옵션</h4>
                <div className="grid" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
                  {[
                    { label: '전화 서비스', field: 'PhoneService', opts: ['Yes', 'No'] },
                    { label: '다중 회선', field: 'MultipleLines', opts: ['No', 'Yes', 'No phone service'] },
                    { label: '온라인 보안', field: 'OnlineSecurity', opts: ['No', 'Yes', 'No internet service'] },
                    { label: '온라인 백업', field: 'OnlineBackup', opts: ['No', 'Yes', 'No internet service'] },
                    { label: '기기 보호', field: 'DeviceProtection', opts: ['No', 'Yes', 'No internet service'] },
                    { label: '기술 지원', field: 'TechSupport', opts: ['No', 'Yes', 'No internet service'] },
                    { label: '스트리밍 TV', field: 'StreamingTV', opts: ['No', 'Yes', 'No internet service'] },
                    { label: '스트리밍 영화', field: 'StreamingMovies', opts: ['No', 'Yes', 'No internet service'] },
                    { label: '전자 청구서', field: 'PaperlessBilling', opts: ['Yes', 'No'] },
                  ].map(({ label, field, opts }) => (
                    <div key={field} className="form-group">
                      <label className="form-label">{label}</label>
                      <select className="form-control" value={formData[field]} onChange={set(field)}>
                        {opts.map((o) => <option key={o}>{o}</option>)}
                      </select>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button type="submit" className="btn-primary" style={{ width: '100%', marginTop: '1rem' }} disabled={loading}>
              {loading ? '분석 중...' : '🔍 이탈 위험 분석 실행'}
            </button>
          </form>
        </div>

        <div className="card" style={{ flex: 1.5, display: 'flex', flexDirection: 'column', textAlign: 'left' }}>
          {result ? (
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
              <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                <div style={{ fontSize: '1.1rem', color: 'var(--text-muted)' }}>분석 상태: <strong>{result.summary}</strong></div>
                <div className="stat-value" style={{ color: result.churn_risk_score > 0.5 ? 'var(--accent)' : 'var(--success)', webkitTextFillColor: 'initial' }}>
                  {(result.churn_risk_score * 100).toFixed(1)}%
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                  신뢰도: {((result.confidence || 0) * 100).toFixed(1)}% | 모델: {result.model_version || 'v2'}
                </div>
              </div>

              {result.risk_factors?.length > 0 && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <strong style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <AlertCircle size={18} color="var(--accent)" /> 위험 요인 분석:
                  </strong>
                  {result.risk_factors.map((rf, i) => (
                    <div key={i} style={{
                      padding: '0.5rem 0.75rem', borderRadius: '6px',
                      background: rf.impact === 'high' ? 'rgba(244, 63, 94, 0.1)' : rf.impact === 'medium' ? 'rgba(251, 191, 36, 0.1)' : 'rgba(255,255,255,0.03)',
                      borderLeft: `3px solid ${rf.impact === 'high' ? 'var(--accent)' : rf.impact === 'medium' ? '#fbbf24' : 'var(--text-muted)'}`,
                      marginBottom: '0.5rem', fontSize: '0.85rem'
                    }}>
                      <div style={{ fontWeight: 'bold', color: rf.impact === 'high' ? 'var(--accent)' : rf.impact === 'medium' ? '#fbbf24' : 'var(--text-main)' }}>
                        {rf.factor}
                      </div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{rf.description}</div>
                    </div>
                  ))}
                </div>
              )}

              <div>
                <strong style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <Lightbulb size={18} color="yellow" /> 맞춤형 대응 전략:
                </strong>
                {(result.suggestions || []).map((s, i) => (
                  <div key={i} style={{
                    padding: '0.75rem', borderRadius: '8px',
                    background: 'var(--glass)', border: '1px solid var(--glass-border)',
                    marginBottom: '0.5rem', fontSize: '0.9rem'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                      <strong style={{ color: 'var(--primary)' }}>{s.action || s}</strong>
                      {s.priority && (
                        <span style={{
                          fontSize: '0.7rem', padding: '2px 8px', borderRadius: '10px',
                          background: s.priority === 'high' ? 'var(--accent)' : s.priority === 'medium' ? '#fbbf24' : 'var(--success)',
                          color: '#fff'
                        }}>
                          {s.priority === 'high' ? '높음' : s.priority === 'medium' ? '중간' : '낮음'}
                        </span>
                      )}
                    </div>
                    {s.details && <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{s.details}</div>}
                    {s.expected_impact && <div style={{ color: 'var(--success)', fontSize: '0.8rem', marginTop: '0.3rem' }}>→ {s.expected_impact}</div>}
                  </div>
                ))}
              </div>
            </motion.div>
          ) : (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '2rem' }}>
              <TrendingUp size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
              <p>데이터를 입력하여 맞춤형 이탈 방지 전략을 확인하세요</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default Predictor;
