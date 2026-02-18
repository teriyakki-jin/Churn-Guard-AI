"""
Real-time Customer Churn Simulation Engine
"""
import random
from typing import Dict, Any, Generator
import asyncio


class ChurnSimulator:
    """Generates realistic customer data for simulation."""

    # Realistic distributions based on actual data
    GENDER_DIST = ['Male', 'Female']
    YES_NO = ['Yes', 'No']
    INTERNET_SERVICE = ['DSL', 'Fiber optic', 'No']
    CONTRACT_TYPES = ['Month-to-month', 'One year', 'Two year']
    PAYMENT_METHODS = [
        'Electronic check',
        'Mailed check',
        'Bank transfer (automatic)',
        'Credit card (automatic)'
    ]

    # Risk profiles for more realistic simulation
    RISK_PROFILES = {
        'high_risk': {
            'weight': 0.3,
            'tenure_range': (1, 12),
            'contract': 'Month-to-month',
            'payment': 'Electronic check',
            'internet': 'Fiber optic',
            'monthly_range': (70, 110)
        },
        'medium_risk': {
            'weight': 0.4,
            'tenure_range': (6, 36),
            'contract': None,  # Random
            'payment': None,
            'internet': None,
            'monthly_range': (40, 80)
        },
        'low_risk': {
            'weight': 0.3,
            'tenure_range': (24, 72),
            'contract': 'Two year',
            'payment': 'Credit card (automatic)',
            'internet': 'DSL',
            'monthly_range': (30, 70)
        }
    }

    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
        self.customer_id = 1000

    def _select_profile(self) -> str:
        """Select a risk profile based on weights."""
        r = random.random()
        cumulative = 0
        for profile, config in self.RISK_PROFILES.items():
            cumulative += config['weight']
            if r <= cumulative:
                return profile
        return 'medium_risk'

    def generate_customer(self) -> Dict[str, Any]:
        """Generate a single realistic customer profile."""
        profile_name = self._select_profile()
        profile = self.RISK_PROFILES[profile_name]

        # Base demographics
        tenure = random.randint(*profile['tenure_range'])
        senior = random.choices([0, 1], weights=[0.84, 0.16])[0]

        # Contract and payment
        contract = profile['contract'] or random.choice(self.CONTRACT_TYPES)
        payment = profile['payment'] or random.choice(self.PAYMENT_METHODS)
        internet = profile['internet'] or random.choice(self.INTERNET_SERVICE)

        # Monthly charges based on profile
        monthly = round(random.uniform(*profile['monthly_range']), 2)
        total = round(monthly * tenure * random.uniform(0.9, 1.1), 2)

        # Services (more likely to have services with longer tenure)
        has_internet = internet != 'No'
        service_prob = min(0.3 + (tenure / 72) * 0.5, 0.8)

        customer = {
            'customer_id': f'SIM-{self.customer_id:05d}',
            'gender': random.choice(self.GENDER_DIST),
            'SeniorCitizen': senior,
            'Partner': random.choice(self.YES_NO),
            'Dependents': random.choice(self.YES_NO),
            'tenure': tenure,
            'PhoneService': random.choices(self.YES_NO, weights=[0.9, 0.1])[0],
            'MultipleLines': random.choice(['Yes', 'No', 'No phone service']),
            'InternetService': internet,
            'OnlineSecurity': random.choice(['Yes', 'No']) if has_internet else 'No internet service',
            'OnlineBackup': random.choice(['Yes', 'No']) if has_internet else 'No internet service',
            'DeviceProtection': random.choice(['Yes', 'No']) if has_internet else 'No internet service',
            'TechSupport': random.choice(['Yes', 'No']) if has_internet else 'No internet service',
            'StreamingTV': random.choice(['Yes', 'No']) if has_internet else 'No internet service',
            'StreamingMovies': random.choice(['Yes', 'No']) if has_internet else 'No internet service',
            'Contract': contract,
            'PaperlessBilling': random.choice(self.YES_NO),
            'PaymentMethod': payment,
            'MonthlyCharges': monthly,
            'TotalCharges': total,
            '_profile': profile_name  # For debugging
        }

        self.customer_id += 1
        return customer

    def generate_batch(self, count: int = 10) -> list:
        """Generate a batch of customers."""
        return [self.generate_customer() for _ in range(count)]

    async def stream_customers(self, interval: float = 2.0) -> Generator:
        """Async generator for streaming customers."""
        while True:
            yield self.generate_customer()
            await asyncio.sleep(interval)


# Singleton instance
simulator = ChurnSimulator()
