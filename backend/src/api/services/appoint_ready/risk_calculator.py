"""
Risk Calculator Service.

Calculates patient risk scores for various conditions based on
clinical data and established risk models.

Risk Models:
- Cardiovascular risk (Framingham, ACC/AHA)
- Diabetes risk (ADA risk assessment)
- Fall risk (STEADI guidelines)
- Readmission risk
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskCalculator:
    """
    Calculates clinical risk scores for patients.

    Implements simplified versions of established risk models:
    - 10-year cardiovascular disease risk
    - Type 2 diabetes risk
    - Fall risk for elderly patients
    """

    # Risk factors and their point values
    CV_RISK_FACTORS = {
        "age": {
            "40-44": 0,
            "45-49": 3,
            "50-54": 6,
            "55-59": 8,
            "60-64": 10,
            "65-69": 11,
            "70+": 12
        },
        "smoking": 8,
        "diabetes": 6,
        "hypertension": 5,
        "high_cholesterol": 5,
        "family_history": 4,
        "obesity": 3
    }

    DIABETES_RISK_FACTORS = {
        "age_45_plus": 5,
        "overweight": 5,
        "family_history": 5,
        "sedentary": 3,
        "hypertension": 5,
        "prediabetes": 8,
        "gestational_diabetes": 10
    }

    FALL_RISK_FACTORS = {
        "age_75_plus": 5,
        "previous_fall": 10,
        "gait_balance_problems": 8,
        "dizziness": 5,
        "vision_problems": 4,
        "multiple_medications": 6,  # 4+ medications
        "cognitive_impairment": 7
    }

    def __init__(self):
        """Initialize risk calculator."""
        pass

    async def calculate_risks(
        self,
        patient_data: Dict[str, Any],
        medical_history: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculate all applicable risk scores for a patient.

        Args:
            patient_data: Patient demographics
            medical_history: FHIR medical history

        Returns:
            list: Risk scores with recommendations
        """
        logger.info(f"Calculating risk scores for patient {patient_data.get('patient_id')}")

        risks = []

        # Get patient details
        age = patient_data.get('age')
        gender = patient_data.get('gender', '').lower()

        if not age:
            logger.warning("Patient age not available, cannot calculate risks")
            return risks

        # Extract conditions from medical history
        conditions = []
        medications = []

        if medical_history:
            conditions = medical_history.get('conditions', [])
            medications = medical_history.get('medications', [])

        # 1. Cardiovascular risk (for patients 40+)
        if age >= 40:
            cv_risk = await self._calculate_cv_risk(age, gender, conditions)
            risks.append(cv_risk)

        # 2. Diabetes risk (for patients without diabetes)
        has_diabetes = any('diabetes' in c.get('name', '').lower() for c in conditions)
        if not has_diabetes and age >= 18:
            diabetes_risk = await self._calculate_diabetes_risk(age, conditions)
            risks.append(diabetes_risk)

        # 3. Fall risk (for patients 65+)
        if age >= 65:
            fall_risk = await self._calculate_fall_risk(age, conditions, medications)
            risks.append(fall_risk)

        logger.info(f"Calculated {len(risks)} risk scores")

        return risks

    async def _calculate_cv_risk(
        self,
        age: int,
        gender: str,
        conditions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate 10-year cardiovascular disease risk.

        Simplified Framingham-based model.
        """
        score = 0

        # Age points
        if age >= 70:
            score += self.CV_RISK_FACTORS['age']['70+']
        elif age >= 65:
            score += self.CV_RISK_FACTORS['age']['65-69']
        elif age >= 60:
            score += self.CV_RISK_FACTORS['age']['60-64']
        elif age >= 55:
            score += self.CV_RISK_FACTORS['age']['55-59']
        elif age >= 50:
            score += self.CV_RISK_FACTORS['age']['50-54']
        elif age >= 45:
            score += self.CV_RISK_FACTORS['age']['45-49']
        else:
            score += self.CV_RISK_FACTORS['age']['40-44']

        # Check for risk factors in conditions
        condition_names = ' '.join([c.get('name', '').lower() for c in conditions])

        if 'diabetes' in condition_names:
            score += self.CV_RISK_FACTORS['diabetes']

        if 'hypertension' in condition_names or 'blood pressure' in condition_names:
            score += self.CV_RISK_FACTORS['hypertension']

        if 'hyperlipidemia' in condition_names or 'cholesterol' in condition_names:
            score += self.CV_RISK_FACTORS['high_cholesterol']

        # Assume some risk factors (in production, would check patient data)
        # For demo purposes, add moderate risk

        # Calculate percentage risk (simplified)
        # Score 0-10: Low, 11-20: Moderate, 21-30: High, 31+: Very High
        risk_percentage = min(score * 2.5, 100)  # Cap at 100%

        # Determine category
        if risk_percentage < 10:
            category = "low"
        elif risk_percentage < 20:
            category = "moderate"
        elif risk_percentage < 30:
            category = "high"
        else:
            category = "very-high"

        # Generate factors and recommendations
        factors = []
        recommendations = []

        if age >= 55:
            factors.append(f"Age {age}")

        if 'diabetes' in condition_names:
            factors.append("Type 2 diabetes")
            recommendations.append("Optimize diabetes management")

        if 'hypertension' in condition_names:
            factors.append("Hypertension")
            recommendations.append("Monitor and control blood pressure")

        if 'cholesterol' in condition_names or 'hyperlipidemia' in condition_names:
            factors.append("High cholesterol")
            recommendations.append("Consider statin therapy")

        # General recommendations
        recommendations.extend([
            "Regular exercise (150 min/week moderate activity)",
            "Heart-healthy diet (Mediterranean or DASH)",
            "Maintain healthy weight",
            "Regular cardiovascular screening"
        ])

        return {
            "risk_type": "cardiovascular",
            "score": round(risk_percentage, 1),
            "category": category,
            "factors": factors or ["Age-related risk"],
            "recommendations": recommendations[:4]  # Top 4
        }

    async def _calculate_diabetes_risk(
        self,
        age: int,
        conditions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate Type 2 diabetes risk.

        Based on ADA risk assessment.
        """
        score = 0

        # Age factor
        if age >= 45:
            score += self.DIABETES_RISK_FACTORS['age_45_plus']

        # Check conditions
        condition_names = ' '.join([c.get('name', '').lower() for c in conditions])

        if 'hypertension' in condition_names:
            score += self.DIABETES_RISK_FACTORS['hypertension']

        if 'prediabetes' in condition_names:
            score += self.DIABETES_RISK_FACTORS['prediabetes']

        # Calculate percentage (simplified)
        risk_percentage = min(score * 3, 100)

        if risk_percentage < 15:
            category = "low"
        elif risk_percentage < 30:
            category = "moderate"
        elif risk_percentage < 50:
            category = "high"
        else:
            category = "very-high"

        factors = []
        recommendations = []

        if age >= 45:
            factors.append(f"Age {age}")

        if 'hypertension' in condition_names:
            factors.append("Hypertension")

        recommendations.extend([
            "Regular blood glucose screening (A1C or fasting glucose)",
            "Maintain healthy weight",
            "Regular physical activity",
            "Healthy diet rich in whole grains, vegetables"
        ])

        return {
            "risk_type": "diabetes",
            "score": round(risk_percentage, 1),
            "category": category,
            "factors": factors or ["Age-related risk"],
            "recommendations": recommendations
        }

    async def _calculate_fall_risk(
        self,
        age: int,
        conditions: List[Dict[str, Any]],
        medications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate fall risk for elderly patients.

        Based on STEADI (Stopping Elderly Accidents, Deaths & Injuries) guidelines.
        """
        score = 0

        # Age factor
        if age >= 75:
            score += self.FALL_RISK_FACTORS['age_75_plus']

        # Multiple medications (polypharmacy)
        if len(medications) >= 4:
            score += self.FALL_RISK_FACTORS['multiple_medications']

        # Check conditions
        condition_names = ' '.join([c.get('name', '').lower() for c in conditions])

        # Common fall-risk conditions
        if any(term in condition_names for term in ['parkinson', 'dementia', 'cognitive']):
            score += self.FALL_RISK_FACTORS['cognitive_impairment']

        if any(term in condition_names for term in ['vision', 'visual', 'cataract']):
            score += self.FALL_RISK_FACTORS['vision_problems']

        # Calculate percentage
        risk_percentage = min(score * 2.5, 100)

        if risk_percentage < 20:
            category = "low"
        elif risk_percentage < 40:
            category = "moderate"
        elif risk_percentage < 60:
            category = "high"
        else:
            category = "very-high"

        factors = []
        recommendations = []

        if age >= 75:
            factors.append(f"Age {age}")

        if len(medications) >= 4:
            factors.append(f"Multiple medications ({len(medications)})")
            recommendations.append("Medication review to reduce polypharmacy")

        recommendations.extend([
            "Fall risk assessment and screening",
            "Home safety evaluation",
            "Balance and strength exercises",
            "Vision screening",
            "Review medications that may increase fall risk"
        ])

        return {
            "risk_type": "fall",
            "score": round(risk_percentage, 1),
            "category": category,
            "factors": factors or ["Age-related fall risk"],
            "recommendations": recommendations[:5]  # Top 5
        }

    async def get_overall_risk_level(self, risks: List[Dict[str, Any]]) -> str:
        """
        Determine overall risk level from individual risk scores.

        Args:
            risks: List of individual risk assessments

        Returns:
            str: Overall risk level (low/moderate/high/very-high)
        """
        if not risks:
            return "unknown"

        # Get highest risk category
        risk_order = {"low": 1, "moderate": 2, "high": 3, "very-high": 4}
        max_risk = max(risks, key=lambda r: risk_order.get(r['category'], 0))

        return max_risk['category']


# Global instance
risk_calculator = RiskCalculator()
