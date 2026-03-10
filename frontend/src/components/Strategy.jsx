import { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Download, Mail, Send, FileText, X } from 'lucide-react';
import { useToast } from '../ToastContext';
import InsightModal from './InsightModal';

const API_URL = '/api';

const insightDetails = {
  autoPayment: {
    title: '자동결제 전환 프로모션',
    color: 'var(--accent)',
    analysis: '전자 수표(Electronic check) 결제 방식을 사용하는 고객의 이탈률은 약 45%로, 자동 결제(신용카드/은행이체) 사용 고객의 이탈률 15-17%에 비해 약 3배 높습니다. 통계적 유의성 검정 결과 p-value < 0.001로 매우 강한 상관관계가 확인되었습니다.',
    strategy: '전자 수표 고객을 대상으로 자동 결제 전환 시 첫 달 5달러 할인 또는 포인트 적립 혜택을 제공합니다. 결제 실패율이 낮고 편리성이 높은 자동 결제의 장점을 강조하는 타겟 마케팅을 진행합니다.',
    effects: [
      '이탈률 45% → 20% 감소 예상 (약 55% 개선)',
      '연간 약 $450,000 매출 손실 방지',
      '고객 만족도 향상 및 결제 편의성 증대'
    ],
    actions: [
      '전자 수표 사용 고객 리스트 추출 (약 1,500명)',
      '개인화된 이메일/SMS 캠페인 발송',
      '고객센터 상담원 교육 및 전환 스크립트 제공',
      '전환율 모니터링 및 A/B 테스트 실시'
    ]
  },
  contractUpgrade: {
    title: '장기 계약 전환 프로그램',
    color: 'var(--primary)',
    analysis: 'Month-to-month 계약 고객의 이탈률은 43%로, 1년 계약(11%) 대비 3.9배, 2년 계약(3%) 대비 14배 높습니다. 특히 고액 요금 고객(월 70달러 이상)의 경우 장기 계약 전환 시 이탈 위험이 크게 감소합니다.',
    strategy: '단기 계약 고객에게 1년 또는 2년 계약 전환 시 월 요금 10-15% 할인, 프리미엄 서비스(보안, 백업) 무료 제공, 계약 기간 중 요금 동결 등의 혜택을 제공합니다.',
    effects: [
      '이탈률 43% → 15% 감소 예상 (약 65% 개선)',
      '고객 생애 가치(LTV) 평균 $1,200 증가',
      '안정적인 매출 예측 가능'
    ],
    actions: [
      'Month-to-month 고객 중 6개월 이상 사용자 타겟팅',
      '계약 전환 시뮬레이터 웹페이지 개발',
      '전환 성공 시 상담원 인센티브 제공',
      '분기별 전환율 목표 설정 및 달성도 모니터링'
    ]
  },
  premiumCare: {
    title: '고위험 고객 프리미엄 케어',
    color: 'var(--success)',
    analysis: 'AI 모델이 예측한 이탈 확률 70% 이상 고객은 실제로 80% 이상 이탈합니다. 이들은 주로 단기 계약, 전자 수표 결제, Fiber Optic 사용, 고액 요금의 특징을 보입니다. 선제적 개입 시 이탈률을 30-40% 감소시킬 수 있습니다.',
    strategy: '고위험 고객에게 전담 상담원 배정, 실시간 서비스 모니터링, 맞춤형 요금제 제안, VIP 고객 프로그램 초대 등 프리미엄 케어를 제공합니다. 이탈 징후 감지 시 즉시 개입합니다.',
    effects: [
      '고위험 고객 이탈률 80% → 50% 감소',
      '고객당 유지 비용 $300 투자 시 ROI $593 달성',
      '브랜드 충성도 및 추천 의향 증가'
    ],
    actions: [
      '매주 고위험 고객 리스트 자동 생성',
      '전담 상담원 팀 구성 및 교육',
      '개인화된 유지 시나리오 스크립트 개발',
      '성공 사례 분석 및 베스트 프랙티스 공유'
    ]
  }
};

const Strategy = ({ stats, analysis }) => {
  const [selectedInsight, setSelectedInsight] = useState(null);
  const { addToast } = useToast();
  const [downloading, setDownloading] = useState(null);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailAddress, setEmailAddress] = useState('');
  const [sendingEmail, setSendingEmail] = useState(false);

  const handleDownload = async (type) => {
    setDownloading(type);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_URL}/reports/export/${type}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = type === 'csv' ? 'churn_stats.csv' : 'churn_report.pdf';
      a.click();
      window.URL.revokeObjectURL(url);
      addToast(`${type.toUpperCase()} 다운로드 완료`, 'success');
    } catch {
      addToast(`${type.toUpperCase()} 다운로드 실패`, 'error');
    }
    setDownloading(null);
  };

  const handleSendEmail = async () => {
    if (!emailAddress) return;
    setSendingEmail(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/notifications/send-report`,
        { email: [emailAddress] },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      addToast(`${emailAddress}로 리포트 발송 요청 완료`, 'success');
      setShowEmailModal(false);
      setEmailAddress('');
    } catch {
      addToast('이메일 발송 실패', 'error');
    }
    setSendingEmail(false);
  };

  if (!stats) return <div>Loading strategies...</div>;

  const featureImportance = stats.feature_importance
    ? Object.entries(stats.feature_importance).map(([name, value]) => ({ name, value: value * 100 }))
    : [];

  const getChurnVal = (category, key) => {
    const val = stats[category]?.[key];
    if (val === undefined) return 0;
    return typeof val === 'object' ? (val.Yes * 100) : val;
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="main-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h1 style={{ margin: 0 }}>Business Strategy & Advanced Analysis</h1>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => handleDownload('csv')}
            disabled={downloading === 'csv'}
            style={{
              padding: '0.5rem 1rem', background: 'var(--glass)', border: '1px solid var(--glass-border)',
              borderRadius: '8px', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem'
            }}
          >
            <Download size={16} /> {downloading === 'csv' ? '...' : 'CSV'}
          </button>
          <button
            onClick={() => handleDownload('pdf')}
            disabled={downloading === 'pdf'}
            style={{
              padding: '0.5rem 1rem', background: 'var(--glass)', border: '1px solid var(--glass-border)',
              borderRadius: '8px', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem'
            }}
          >
            <FileText size={16} /> {downloading === 'pdf' ? '...' : 'PDF'}
          </button>
          <button
            onClick={() => setShowEmailModal(true)}
            style={{
              padding: '0.5rem 1rem', background: 'var(--primary)', border: 'none',
              borderRadius: '8px', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem'
            }}
          >
            <Mail size={16} /> Email
          </button>
        </div>
      </div>

      {showEmailModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }} onClick={() => setShowEmailModal(false)}>
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="card"
            style={{ maxWidth: '420px', width: '100%', position: 'relative' }}
            onClick={(e) => e.stopPropagation()}
          >
            <button onClick={() => setShowEmailModal(false)} style={{
              position: 'absolute', top: '15px', right: '15px', background: 'var(--glass)',
              border: '1px solid var(--glass-border)', borderRadius: '50%', width: '30px', height: '30px',
              cursor: 'pointer', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <X size={16} />
            </button>
            <h3 style={{ marginBottom: '1rem' }}>리포트 이메일 발송</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              입력한 이메일로 Churn 분석 PDF 리포트를 발송합니다.
            </p>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="email"
                placeholder="recipient@example.com"
                value={emailAddress}
                onChange={(e) => setEmailAddress(e.target.value)}
                className="form-control"
                style={{ flex: 1 }}
              />
              <button
                onClick={handleSendEmail}
                disabled={sendingEmail || !emailAddress}
                style={{
                  padding: '0.75rem 1.2rem', background: 'var(--primary)', border: 'none',
                  borderRadius: '8px', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem',
                  opacity: sendingEmail || !emailAddress ? 0.5 : 1
                }}
              >
                <Send size={16} /> {sendingEmail ? '...' : '발송'}
              </button>
            </div>
          </motion.div>
        </div>
      )}

      <div className="grid">
        <div className="card" style={{ flex: 1.5 }}>
          <h3>📊 주요 분석 결과 요약</h3>
          <div style={{ marginTop: '1rem' }}>
            <div className="card" style={{ background: 'rgba(255,255,255,0.03)', border: 'none', padding: '10px 15px' }}>
              <strong>1) 계약 유형별 churn율</strong>
              <ul style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                <li>Month-to-month: {getChurnVal('contract_impact', 'Month-to-month').toFixed(0)}%</li>
                <li>One year: {getChurnVal('contract_impact', 'One year').toFixed(0)}%</li>
                <li>Two year: {getChurnVal('contract_impact', 'Two year').toFixed(0)}%</li>
              </ul>
            </div>

            <div className="card" style={{ background: 'rgba(255,255,255,0.03)', border: 'none', padding: '10px 15px', marginTop: '10px' }}>
              <strong>2) 지불 방식 영향</strong>
              <ul style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                <li>Electronic check: churn율이 가장 높음 ({getChurnVal('payment_impact', 'Electronic check').toFixed(0)}%)</li>
                <li>Automatic payment: churn율 상대적으로 낮음</li>
              </ul>
            </div>

            <div className="card" style={{ background: 'rgba(255,255,255,0.03)', border: 'none', padding: '10px 15px', marginTop: '10px' }}>
              <strong>3) 머신러닝 기반 특성 중요도 (Feature Importance)</strong>
              <table style={{ width: '100%', marginTop: '15px', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-muted)' }}>
                    <th style={{ textAlign: 'left', padding: '8px' }}>순위</th>
                    <th style={{ textAlign: 'left', padding: '8px' }}>변수명</th>
                    <th style={{ textAlign: 'left', padding: '8px' }}>중요도</th>
                  </tr>
                </thead>
                <tbody>
                  {featureImportance.map((item, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '8px' }}>{index + 1}</td>
                      <td style={{ padding: '8px', fontWeight: 'bold' }}>{item.name}</td>
                      <td style={{ padding: '8px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div style={{ flex: 1, height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                            <div style={{ width: `${item.value}%`, height: '100%', background: 'var(--primary)' }}></div>
                          </div>
                          <span>{item.value.toFixed(0)}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="card" style={{ flex: 2 }}>
          <h3>📈 비즈니스 인사이트 (Business Insights)</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>💡 카드를 클릭하면 상세 전략을 확인할 수 있습니다</p>
          <div style={{ marginTop: '1rem' }}>
            {[
              { key: 'autoPayment', color: 'var(--accent)', bg: 'rgba(244, 63, 94, 0.05)', shadow: 'rgba(244, 63, 94, 0.2)', label: '● 단기 계약 + e-check 고객이 가장 위험', text: '→ 자동결제 전환 프로모션 필요: 전자 수표 고객대상 신용카드/직불계약 연동 시 첫 달 5$ 할인 제공' },
              { key: 'contractUpgrade', color: 'var(--primary)', bg: 'rgba(99, 102, 241, 0.05)', shadow: 'rgba(99, 102, 241, 0.2)', label: '● 월 청구 금액 높은 고객 churn 위험', text: '→ 장기 할인 또는 로열티 프로그램 제안: 고액 이용자 대상 다년 계약 시 결합 서비스(보안, 백업) 무료 제공' },
              { key: 'premiumCare', color: 'var(--success)', bg: 'rgba(16, 185, 129, 0.05)', shadow: 'rgba(16, 185, 129, 0.2)', label: '● 이탈 방지 마케팅 ROI 최적화', text: '→ 선제적 대응: AI가 예측한 고위험 고객(Prob > 70%) 대상 상담원 실시간 지원 및 맞춤형 통화 관리 도입' },
            ].map(({ key, color, bg, shadow, label, text }, i) => (
              <div
                key={key}
                className="card"
                style={{
                  borderLeft: `4px solid ${color}`,
                  background: bg,
                  cursor: 'pointer',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  marginTop: i > 0 ? '1rem' : 0
                }}
                onClick={() => setSelectedInsight(insightDetails[key])}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = `0 8px 16px ${shadow}`;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{ color, fontWeight: 'bold' }}>{label}</div>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginTop: '0.5rem' }}><strong>{text}</strong></p>
                <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color }}>클릭하여 상세 보기 →</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {analysis && (
        <div className="grid" style={{ marginTop: '1.5rem' }}>
          <div className="card">
            <h3>⚖️ 통계적 유의성 검정 (p-value)</h3>
            <table style={{ width: '100%', marginTop: '10px', fontSize: '0.8rem' }}>
              <thead>
                <tr style={{ color: 'var(--text-muted)' }}>
                  <th style={{ textAlign: 'left' }}>변수</th>
                  <th style={{ textAlign: 'left' }}>테스트</th>
                  <th style={{ textAlign: 'left' }}>p-value</th>
                  <th style={{ textAlign: 'left' }}>Significant</th>
                </tr>
              </thead>
              <tbody>
                {analysis.statistical_tests.map((t, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '5px 0' }}>{t.variable}</td>
                    <td>{t.test}</td>
                    <td>{t.p_value.toExponential(2)}</td>
                    <td style={{ color: t.significant ? 'var(--success)' : 'var(--accent)' }}>
                      {t.significant ? 'YES' : 'NO'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card">
            <h3>🎯 고위험군 세분화 분석</h3>
            <table style={{ width: '100%', marginTop: '10px' }}>
              <thead>
                <tr style={{ color: 'var(--text-muted)' }}>
                  <th style={{ textAlign: 'left' }}>Segment</th>
                  <th style={{ textAlign: 'left' }}>Churn Rate</th>
                </tr>
              </thead>
              <tbody>
                {analysis.segments.map((s, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '10px 0' }}>{s.segment}</td>
                    <td style={{ fontWeight: 'bold', color: s.churn_rate > 30 ? 'var(--accent)' : 'var(--success)' }}>
                      {s.churn_rate}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div style={{ marginTop: '2rem' }}>
              <h3>💰 예상 손실 및 리텐션 가치</h3>
              <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '1rem' }}>
                <div style={{ padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>1인당 연간 손실</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>${analysis.financial_impact.avg_loss_per_customer}</div>
                </div>
                <div style={{ padding: '10px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>유지 프로그램 가치</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'var(--success)' }}>+${analysis.financial_impact.roi_potential}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <InsightModal insight={selectedInsight} onClose={() => setSelectedInsight(null)} />
    </motion.div>
  );
};

export default Strategy;
