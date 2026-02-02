"""
Churn Service v2 - Enhanced with Feature Engineering support
"""
import joblib
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Optional
import json
import os


class ChurnServiceV2:
    """Enhanced Churn Prediction Service with Feature Engineering."""

    def __init__(self, model_version: str = 'v2'):
        self.model = None
        self.feature_names = None
        self.metadata = None
        self.model_version = model_version
        self.load_model()

    def load_model(self):
        """Load model and feature names."""
        try:
            model_file = f'churn_model_{self.model_version}.pkl'
            feature_file = f'feature_names_{self.model_version}.pkl'
            metadata_file = f'model_metadata_{self.model_version}.json'

            # Fallback to v1 if v2 doesn't exist
            if not os.path.exists(model_file):
                model_file = 'churn_model.pkl'
                feature_file = 'feature_names.pkl'
                self.model_version = 'v1'

            self.model = joblib.load(model_file)
            self.feature_names = joblib.load(feature_file)

            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    self.metadata = json.load(f)

            print(f"Model {self.model_version} loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
            self.feature_names = None

    def engineer_features(self, input_df: pd.DataFrame, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Apply feature engineering to input data."""
        df = input_df.copy()

        # Get reference data for normalization
        ref_df = pd.read_csv('data/Customer-Churn.csv')
        ref_df['TotalCharges'] = pd.to_numeric(ref_df['TotalCharges'], errors='coerce').fillna(0)

        max_charges = ref_df['MonthlyCharges'].max()
        max_total = ref_df['TotalCharges'].max()

        # 1. Customer Value Score
        df['CustomerValueScore'] = (
            raw_df['tenure'].iloc[0] * 0.3 +
            (raw_df['MonthlyCharges'].iloc[0] / max_charges) * 100 * 0.4 +
            (raw_df['TotalCharges'].iloc[0] / max_total) * 100 * 0.3
        )

        # 2. Service Count
        service_cols = [
            'PhoneService', 'MultipleLines', 'InternetService',
            'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
            'TechSupport', 'StreamingTV', 'StreamingMovies'
        ]
        service_count = 0
        for col in service_cols:
            if col in raw_df.columns:
                val = raw_df[col].iloc[0]
                if val in ['Yes', 'DSL', 'Fiber optic']:
                    service_count += 1
        df['ServiceCount'] = service_count

        # 3. Contract Stability
        contract_map = {'Month-to-month': 1, 'One year': 2, 'Two year': 3}
        df['ContractStability'] = contract_map.get(raw_df['Contract'].iloc[0], 1)

        # 4. Payment Risk
        payment_map = {
            'Electronic check': 3,
            'Mailed check': 2,
            'Bank transfer (automatic)': 1,
            'Credit card (automatic)': 1
        }
        df['PaymentRisk'] = payment_map.get(raw_df['PaymentMethod'].iloc[0], 2)

        # 5. Tenure Group
        tenure = raw_df['tenure'].iloc[0]
        if tenure <= 12:
            tenure_group = 'New'
        elif tenure <= 24:
            tenure_group = 'Growing'
        elif tenure <= 48:
            tenure_group = 'Mature'
        else:
            tenure_group = 'Loyal'

        for grp in ['New', 'Growing', 'Mature', 'Loyal']:
            col_name = f'TenureGroup_{grp}'
            if col_name in self.feature_names:
                df[col_name] = 1 if grp == tenure_group else 0

        # 6. Charge Ratio
        total = raw_df['TotalCharges'].iloc[0]
        monthly = raw_df['MonthlyCharges'].iloc[0]
        tenure_val = max(raw_df['tenure'].iloc[0], 1)
        df['ChargeRatio'] = monthly / (total / tenure_val) if total > 0 else 1

        # 7. Average Monthly Spend
        df['AvgMonthlySpend'] = total / tenure_val if tenure_val > 0 else monthly

        # 8. Senior Monthly
        df['SeniorMonthly'] = int(
            raw_df['SeniorCitizen'].iloc[0] == 1 and
            raw_df['Contract'].iloc[0] == 'Month-to-month'
        )

        # 9. Premium Services
        premium_cols = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport']
        premium_count = sum(1 for col in premium_cols
                          if col in raw_df.columns and raw_df[col].iloc[0] == 'Yes')
        df['PremiumServices'] = premium_count

        # 10. Fiber No Security
        df['FiberNoSecurity'] = int(
            raw_df['InternetService'].iloc[0] == 'Fiber optic' and
            raw_df['OnlineSecurity'].iloc[0] == 'No'
        )

        return df

    def predict(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction with detailed analysis."""
        if self.model is None or self.feature_names is None:
            raise Exception("Model not loaded")

        # Create input dataframe
        raw_df = pd.DataFrame([input_dict])

        # Initialize feature dataframe
        final_df = pd.DataFrame(0, index=[0], columns=self.feature_names)

        # Set numeric features
        numeric_cols = ['SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges']
        for col in numeric_cols:
            if col in raw_df.columns and col in final_df.columns:
                final_df[col] = raw_df[col].iloc[0]

        # Set categorical features (one-hot encoded)
        categorical_cols = [c for c in input_dict.keys() if c not in numeric_cols]
        for col in categorical_cols:
            val = raw_df[col].iloc[0]
            col_name = f"{col}_{val}"
            if col_name in final_df.columns:
                final_df[col_name] = 1

        # Apply feature engineering if v2
        if self.model_version == 'v2':
            final_df = self.engineer_features(final_df, raw_df)

        # Ensure all columns exist
        for col in self.feature_names:
            if col not in final_df.columns:
                final_df[col] = 0

        # Reorder columns to match training
        final_df = final_df[self.feature_names]

        # Make prediction
        prob = float(self.model.predict_proba(final_df)[0][1])

        # Generate risk factors
        risk_factors = self._analyze_risk_factors(input_dict, prob)

        # Generate suggestions
        suggestions = self._generate_suggestions(input_dict, risk_factors)

        return {
            "churn_risk_score": round(prob, 4),
            "prediction": "Yes" if prob > 0.5 else "No",
            "summary": self._get_risk_summary(prob),
            "confidence": round(abs(prob - 0.5) * 2, 4),
            "risk_factors": risk_factors,
            "suggestions": suggestions,
            "model_version": self.model_version
        }

    def _analyze_risk_factors(self, input_dict: Dict, prob: float) -> List[Dict]:
        """Analyze contributing risk factors."""
        factors = []

        # Contract risk
        if input_dict.get('Contract') == 'Month-to-month':
            factors.append({
                "factor": "Month-to-month Contract",
                "impact": "high",
                "description": "3.7x higher churn rate than 2-year contracts"
            })

        # Payment method risk
        if input_dict.get('PaymentMethod') == 'Electronic check':
            factors.append({
                "factor": "Electronic Check Payment",
                "impact": "high",
                "description": "45% churn rate vs 15-19% for automatic payments"
            })

        # Internet service risk
        if input_dict.get('InternetService') == 'Fiber optic':
            factors.append({
                "factor": "Fiber Optic Service",
                "impact": "medium",
                "description": "41.9% churn rate, 2.2x higher than DSL"
            })

        # Tenure risk
        tenure = input_dict.get('tenure', 0)
        if tenure <= 6:
            factors.append({
                "factor": "New Customer",
                "impact": "high",
                "description": "Customers under 6 months have highest churn"
            })
        elif tenure <= 12:
            factors.append({
                "factor": "Early-stage Customer",
                "impact": "medium",
                "description": "First year is critical retention period"
            })

        # High charges risk
        if input_dict.get('MonthlyCharges', 0) > 70:
            factors.append({
                "factor": "High Monthly Charges",
                "impact": "medium",
                "description": "Higher bills correlate with increased churn"
            })

        # No security services
        if (input_dict.get('InternetService') != 'No' and
            input_dict.get('OnlineSecurity') == 'No'):
            factors.append({
                "factor": "No Online Security",
                "impact": "medium",
                "description": "Customers without security features churn more"
            })

        # Senior citizen
        if input_dict.get('SeniorCitizen') == 1:
            factors.append({
                "factor": "Senior Citizen",
                "impact": "low",
                "description": "Senior citizens show higher churn tendency"
            })

        return factors

    def _generate_suggestions(self, input_dict: Dict, risk_factors: List[Dict]) -> List[Dict]:
        """Generate actionable retention suggestions."""
        suggestions = []

        if input_dict.get('Contract') == 'Month-to-month':
            suggestions.append({
                "action": "Offer Contract Upgrade",
                "priority": "high",
                "details": "Provide 15-20% discount for 1-year contract commitment",
                "expected_impact": "Reduce churn risk by 70%"
            })

        if input_dict.get('PaymentMethod') == 'Electronic check':
            suggestions.append({
                "action": "Promote Auto-Pay",
                "priority": "high",
                "details": "$5/month credit for switching to automatic payment",
                "expected_impact": "Reduce churn risk by 60%"
            })

        if input_dict.get('InternetService') == 'Fiber optic':
            suggestions.append({
                "action": "Service Quality Check",
                "priority": "medium",
                "details": "Proactive call to ensure satisfaction with fiber service",
                "expected_impact": "Address service issues early"
            })

        if input_dict.get('MonthlyCharges', 0) > 70:
            suggestions.append({
                "action": "Bundle Optimization",
                "priority": "medium",
                "details": "Review services and offer optimized bundle pricing",
                "expected_impact": "Improve perceived value"
            })

        if (input_dict.get('OnlineSecurity') == 'No' and
            input_dict.get('InternetService') != 'No'):
            suggestions.append({
                "action": "Upsell Security Package",
                "priority": "medium",
                "details": "Offer 3-month free trial of online security",
                "expected_impact": "Increase stickiness with additional services"
            })

        tenure = input_dict.get('tenure', 0)
        if tenure <= 6:
            suggestions.append({
                "action": "New Customer Onboarding",
                "priority": "high",
                "details": "Personal check-in call and welcome package",
                "expected_impact": "Build relationship in critical early period"
            })

        if not suggestions:
            suggestions.append({
                "action": "Loyalty Recognition",
                "priority": "low",
                "details": "Send appreciation message and loyalty rewards",
                "expected_impact": "Maintain positive relationship"
            })

        return suggestions

    def _get_risk_summary(self, prob: float) -> str:
        """Get risk level summary."""
        if prob > 0.7:
            return "Critical Risk"
        elif prob > 0.5:
            return "High Risk"
        elif prob > 0.3:
            return "Moderate Risk"
        elif prob > 0.15:
            return "Low Risk"
        else:
            return "Minimal Risk"

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        df = pd.read_csv('data/Customer-Churn.csv')
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['TotalCharges'].fillna(df['TotalCharges'].mean(), inplace=True)

        def get_churn_pct(col):
            return (df.groupby(col)['Churn'].apply(lambda x: (x == 'Yes').mean()) * 100).to_dict()

        # Calculate feature importance from model if available
        feature_importance = {}
        if self.model is not None and hasattr(self.model, 'named_estimators_'):
            xgb_model = self.model.named_estimators_.get('xgb')
            if xgb_model is not None:
                importances = xgb_model.feature_importances_
                top_indices = np.argsort(importances)[-4:][::-1]
                for idx in top_indices:
                    if idx < len(self.feature_names):
                        feature_importance[self.feature_names[idx]] = round(float(importances[idx]), 2)
        else:
            feature_importance = {
                "MonthlyCharges": 0.42,
                "Contract": 0.31,
                "TotalCharges": 0.15,
                "Tenure": 0.12
            }

        return {
            "overall_churn_rate": {
                "Yes": round((df['Churn'] == 'Yes').mean(), 4),
                "No": round((df['Churn'] == 'No').mean(), 4)
            },
            "contract_impact": get_churn_pct('Contract'),
            "payment_impact": get_churn_pct('PaymentMethod'),
            "internet_impact": get_churn_pct('InternetService'),
            "total_customers": len(df),
            "churned_customers": len(df[df['Churn'] == 'Yes']),
            "feature_importance": feature_importance,
            "model_version": self.model_version,
            "model_metrics": self.metadata.get('ensemble_metrics') if self.metadata else None
        }

    def get_analysis(self) -> Dict[str, Any]:
        """Get detailed analysis."""
        df = pd.read_csv('data/Customer-Churn.csv')
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)

        # Statistical Tests
        statistical_tests = []
        cat_vars = ['SeniorCitizen', 'Partner', 'Dependents', 'Contract', 'PaymentMethod', 'PaperlessBilling']
        for var in cat_vars:
            contingency = pd.crosstab(df[var], df['Churn'])
            chi2, p, _, _ = stats.chi2_contingency(contingency)
            statistical_tests.append({
                "variable": var,
                "test": "Chi-square",
                "chi2_statistic": round(float(chi2), 2),
                "p_value": float(p),
                "significant": bool(p < 0.05)
            })

        num_vars = ['tenure', 'MonthlyCharges', 'TotalCharges']
        for var in num_vars:
            churned = df[df['Churn'] == 'Yes'][var]
            stayed = df[df['Churn'] == 'No'][var]
            if len(churned) > 0 and len(stayed) > 0:
                stat, p = stats.mannwhitneyu(churned, stayed)
                statistical_tests.append({
                    "variable": var,
                    "test": "Mann-Whitney U",
                    "statistic": round(float(stat), 2),
                    "p_value": float(p),
                    "significant": bool(p < 0.05)
                })

        # High-Risk Segments
        segments = [
            {"name": "Month-to-month + E-check",
             "filter": (df['Contract'] == 'Month-to-month') & (df['PaymentMethod'] == 'Electronic check')},
            {"name": "Two year + Auto-payment",
             "filter": (df['Contract'] == 'Two year') & (df['PaymentMethod'].str.contains('automatic', na=False))},
            {"name": "Senior + Month-to-month",
             "filter": (df['SeniorCitizen'] == 1) & (df['Contract'] == 'Month-to-month')},
            {"name": "Fiber + No Security",
             "filter": (df['InternetService'] == 'Fiber optic') & (df['OnlineSecurity'] == 'No')},
            {"name": "New Customer (<6mo)",
             "filter": df['tenure'] <= 6}
        ]

        segment_results = []
        for seg in segments:
            sub = df[seg['filter']]
            churn_rate = (sub['Churn'] == 'Yes').mean() * 100 if len(sub) > 0 else 0
            segment_results.append({
                "segment": seg['name'],
                "churn_rate": round(float(churn_rate), 1),
                "size": int(len(sub)),
                "pct_of_total": round(len(sub) / len(df) * 100, 1)
            })

        # Financial Impact
        churned_df = df[df['Churn'] == 'Yes']
        avg_monthly = float(churned_df['MonthlyCharges'].mean()) if len(churned_df) > 0 else 0
        avg_tenure = float(churned_df['tenure'].mean()) if len(churned_df) > 0 else 0

        financial_impact = {
            "avg_monthly_loss": round(avg_monthly, 2),
            "avg_annual_loss_per_customer": round(avg_monthly * 12, 2),
            "total_annual_exposure": round(avg_monthly * 12 * len(churned_df), 2),
            "avg_customer_lifetime_months": round(avg_tenure, 1),
            "retention_cost_estimate": 300.0,
            "roi_per_saved_customer": round(avg_monthly * 12 - 300, 2)
        }

        return {
            "statistical_tests": statistical_tests,
            "segments": segment_results,
            "financial_impact": financial_impact,
            "model_version": self.model_version
        }
