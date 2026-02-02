import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AuthProvider, useAuth } from './AuthContext';
import Login from './Login';
import { LayoutDashboard, UserCheck, TrendingUp, AlertCircle, Users, Activity, LogOut, Lightbulb, PieChart as PieIcon, BarChart as BarIcon } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

const API_URL = '/api';

// Modal Component for Detailed Insights
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
      <div style={{ marginTop: 'auto', cursor: 'pointer' }} className="nav-item" onClick={logout}>
        <LogOut size={20} /> Sign Out
      </div>
    </div>
  );
};

const Dashboard = ({ stats }) => {
  if (!stats) return <div className="fade-in">Loading insights...</div>;

  const pieData = [
    { name: 'Stayed', value: (stats.overall_churn_rate?.No || 0.73) * 100 },
    { name: 'Churned', value: (stats.overall_churn_rate?.Yes || 0.27) * 100 },
  ];

  const COLORS = ['#10b981', '#f43f5e'];

  // Handle both old and new data structures
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

const Strategy = ({ stats, analysis }) => {
  const [selectedInsight, setSelectedInsight] = useState(null);

  if (!stats) return <div>Loading strategies...</div>;

  const featureImportance = stats.feature_importance ? Object.entries(stats.feature_importance).map(([name, value]) => ({ name, value: value * 100 })) : [];

  const getChurnVal = (category, key) => {
    const val = stats[category]?.[key];
    if (val === undefined) return 0;
    return typeof val === 'object' ? (val.Yes * 100) : val;
  };

  // 상세 인사이트 데이터
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

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="main-content">
      <h1>Business Strategy & Advanced Analysis</h1>

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
            <div
              className="card"
              style={{
                borderLeft: '4px solid var(--accent)',
                background: 'rgba(244, 63, 94, 0.05)',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s'
              }}
              onClick={() => setSelectedInsight(insightDetails.autoPayment)}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 8px 16px rgba(244, 63, 94, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{ color: 'var(--accent)', fontWeight: 'bold' }}>● 단기 계약 + e-check 고객이 가장 위험</div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginTop: '0.5rem' }}>
                <strong>&rarr; 자동결제 전환 프로모션 필요:</strong> 전자 수표 고객대상 신용카드/직불계약 연동 시 첫 달 5$ 할인 제공
              </p>
              <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--accent)' }}>클릭하여 상세 보기 →</div>
            </div>

            <div
              className="card"
              style={{
                borderLeft: '4px solid var(--primary)',
                background: 'rgba(99, 102, 241, 0.05)',
                marginTop: '1rem',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s'
              }}
              onClick={() => setSelectedInsight(insightDetails.contractUpgrade)}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 8px 16px rgba(99, 102, 241, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{ color: 'var(--primary)', fontWeight: 'bold' }}>● 월 청구 금액 높은 고객 churn 위험</div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginTop: '0.5rem' }}>
                <strong>&rarr; 장기 할인 또는 로열티 프로그램 제안:</strong> 고액 이용자 대상 다년 계약 시 결합 서비스(보안, 백업) 무료 제공
              </p>
              <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--primary)' }}>클릭하여 상세 보기 →</div>
            </div>

            <div
              className="card"
              style={{
                borderLeft: '4px solid var(--success)',
                background: 'rgba(16, 185, 129, 0.05)',
                marginTop: '1rem',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s'
              }}
              onClick={() => setSelectedInsight(insightDetails.premiumCare)}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 8px 16px rgba(16, 185, 129, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{ color: 'var(--success)', fontWeight: 'bold' }}>● 이탈 방지 마케팅 ROI 최적화</div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginTop: '0.5rem' }}>
                <strong>&rarr; 선제적 대응:</strong> AI가 예측한 고위험 고객(Prob &gt; 70%) 대상 상담원 실시간 지원 및 맞춤형 통화 관리 도입
              </p>
              <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--success)' }}>클릭하여 상세 보기 →</div>
            </div>
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

const Predictor = () => {
  const [formData, setFormData] = useState({
    gender: 'Female', SeniorCitizen: 0, Partner: 'No', Dependents: 'No',
    tenure: 1, PhoneService: 'Yes', MultipleLines: 'No', InternetService: 'Fiber optic',
    OnlineSecurity: 'No', OnlineBackup: 'No', DeviceProtection: 'No', TechSupport: 'No',
    StreamingTV: 'No', StreamingMovies: 'No', Contract: 'Month-to-month',
    PaperlessBilling: 'Yes', PaymentMethod: 'Electronic check',
    MonthlyCharges: 70.0, TotalCharges: 70.0
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/predict`, formData);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error connecting to backend.');
    }
    setLoading(false);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="main-content">
      <h1>고객 이탈 위험 예측 (AI)</h1>
      <div className="grid">
        <div className="card" style={{ flex: 2 }}>
          <form onSubmit={handleSubmit}>
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
              <div className="form-group">
                <label className="form-label">계약 형태 (Contract Type)</label>
                <select className="form-control" value={formData.Contract} onChange={e => setFormData({ ...formData, Contract: e.target.value })}>
                  <option>Month-to-month</option>
                  <option>One year</option>
                  <option>Two year</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">결제 수단 (Payment Method)</label>
                <select className="form-control" value={formData.PaymentMethod} onChange={e => setFormData({ ...formData, PaymentMethod: e.target.value })}>
                  <option>Electronic check</option>
                  <option>Mailed check</option>
                  <option>Bank transfer (automatic)</option>
                  <option>Credit card (automatic)</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">인터넷 서비스 (Internet Service)</label>
                <select className="form-control" value={formData.InternetService} onChange={e => setFormData({ ...formData, InternetService: e.target.value })}>
                  <option>Fiber optic</option>
                  <option>DSL</option>
                  <option>No</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">가입 기간 (개월) (Tenure)</label>
                <input type="number" className="form-control" value={formData.tenure} onChange={e => setFormData({ ...formData, tenure: parseInt(e.target.value) })} />
              </div>
            </div>
            <button type="submit" className="btn-primary" style={{ width: '100%', marginTop: '1rem' }} disabled={loading}>
              {loading ? '분석 중...' : '이탈 위험 분석 실행'}
            </button>
          </form>
        </div>

        <div className="card" style={{ flex: 1.5, display: 'flex', flexDirection: 'column', textAlign: 'left' }}>
          {result ? (
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.1rem', color: 'var(--text-muted)' }}>분석 상태: <strong>{result.summary}</strong></div>
                <div className="stat-value" style={{ color: result.churn_risk_score > 0.5 ? 'var(--accent)' : 'var(--success)', webkitTextFillColor: 'initial' }}>
                  {(result.churn_risk_score * 100).toFixed(1)}%
                </div>
              </div>

              <div style={{ marginTop: '1.5rem' }}>
                <strong style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <Lightbulb size={18} color="yellow" /> 맞춤형 대응 전략:
                </strong>
                {(result.suggestions || []).map((s, i) => (
                  <div key={i} style={{ padding: '0.75rem', borderRadius: '8px', background: 'var(--glass)', border: '1px solid var(--glass-border)', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                    {s}
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

const MainContent = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;

      const config = {
        headers: { Authorization: `Bearer ${token}` }
      };

      try {
        const [resStats, resAnalysis] = await Promise.all([
          axios.get(`${API_URL}/stats`, config),
          axios.get(`${API_URL}/analysis`, config)
        ]);
        setStats(resStats.data);
        setAnalysis(resAnalysis.data);
      } catch (err) {
        console.error("Failed to fetch data", err);
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
      </AnimatePresence>
    </div>
  );
}

const AppContent = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <MainContent /> : <Login />;
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
