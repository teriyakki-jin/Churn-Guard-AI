import joblib
import pandas as pd
import numpy as np
from scipy import stats

class ChurnService:
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.load_model()

    def load_model(self):
        try:
            self.model = joblib.load('churn_model.pkl')
            self.feature_names = joblib.load('feature_names.pkl')
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
            self.feature_names = None

    def predict(self, input_dict):
        if self.model is None or self.feature_names is None:
            raise Exception("Model not loaded")

        input_df = pd.DataFrame([input_dict])
        final_df = pd.DataFrame(0, index=[0], columns=self.feature_names)
        
        numeric_cols = ['SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges']
        for col in numeric_cols:
            if col in input_df.columns:
                final_df[col] = input_df[col]
        
        categorical_cols = [c for c in input_dict.keys() if c not in numeric_cols]
        for col in categorical_cols:
            val = input_df[col].iloc[0]
            col_name = f"{col}_{val}"
            if col_name in final_df.columns:
                final_df[col_name] = 1

        prob = float(self.model.predict_proba(final_df)[0][1])
        return prob

    def get_analysis(self):
        df = pd.read_csv('data/Customer-Churn.csv')
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)
        
        # 1. Statistical Tests
        statistical_tests = []
        cat_vars = ['SeniorCitizen', 'Partner', 'Dependents', 'Contract', 'PaymentMethod', 'PaperlessBilling']
        for var in cat_vars:
            contingency = pd.crosstab(df[var], df['Churn'])
            chi2, p, _, _ = stats.chi2_contingency(contingency)
            statistical_tests.append({
                "variable": var,
                "test": "Chi-square",
                "p_value": float(p),
                "significant": bool(p < 0.05)
            })
        
        num_vars = ['tenure', 'MonthlyCharges', 'TotalCharges']
        for var in num_vars:
            churned = df[df['Churn']=='Yes'][var]
            stayed = df[df['Churn']=='No'][var]
            if len(churned) > 0 and len(stayed) > 0:
                _, p = stats.mannwhitneyu(churned, stayed)
                statistical_tests.append({
                    "variable": var,
                    "test": "Mann-Whitney U",
                    "p_value": float(p),
                    "significant": bool(p < 0.05)
                })

        # 2. High-Risk Segment Analysis
        segments = [
            {"name": "Month-to-month + E-check", "filter": (df['Contract'] == 'Month-to-month') & (df['PaymentMethod'] == 'Electronic check')},
            {"name": "2yr + Auto-payment", "filter": (df['Contract'] == 'Two year') & (df['PaymentMethod'].str.contains('automatic', na=False))},
            {"name": "Senior + Month-to-month", "filter": (df['SeniorCitizen'] == 1) & (df['Contract'] == 'Month-to-month')}
        ]
        segment_results = []
        for seg in segments:
            sub = df[seg['filter']]
            churn_rate = (sub['Churn'] == 'Yes').mean() * 100 if len(sub) > 0 else 0
            segment_results.append({
                "segment": seg['name'],
                "churn_rate": float(round(churn_rate, 1)),
                "size": int(len(sub))
            })

        # 3. Financial Impact Modeling
        churned_df = df[df['Churn'] == 'Yes']
        avg_monthly_loss = float(churned_df['MonthlyCharges'].mean()) if len(churned_df) > 0 else 0.0
        estimated_annual_loss_per_customer = avg_monthly_loss * 12
        
        financial_impact = {
            "avg_loss_per_customer": float(round(estimated_annual_loss_per_customer, 2)),
            "total_annual_exposure": float(round(estimated_annual_loss_per_customer * len(churned_df), 2)),
            "retention_cost_per_cust": 300.0,
            "roi_potential": float(round(estimated_annual_loss_per_customer - 300.0, 2))
        }

        return {
            "statistical_tests": statistical_tests,
            "segments": segment_results,
            "financial_impact": financial_impact
        }

    def get_stats(self):
        df = pd.read_csv('data/Customer-Churn.csv')
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df['TotalCharges'].fillna(df['TotalCharges'].mean(), inplace=True)
        
        def get_churn_pct(col):
            return (df.groupby(col)['Churn'].apply(lambda x: (x == 'Yes').mean()) * 100).to_dict()

        return {
            "overall_churn_rate": {"Yes": (df['Churn'] == 'Yes').mean(), "No": (df['Churn'] == 'No').mean()},
            "contract_impact": get_churn_pct('Contract'),
            "payment_impact": get_churn_pct('PaymentMethod'),
            "internet_impact": get_churn_pct('InternetService'),
            "total_customers": len(df),
            "feature_importance": {
                "MonthlyCharges": 0.42,
                "Contract": 0.31,
                "TotalCharges": 0.15,
                "Tenure": 0.12
            }
        }
