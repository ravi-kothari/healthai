"""
Care Gap Detector Service.

Identifies gaps in preventive care and clinical guideline adherence.

Care Gap Categories:
- Preventive screenings (mammography, colonoscopy, etc.)
- Vaccinations (flu, pneumonia, COVID-19)
- Chronic disease management (A1C testing, eye exams for diabetics)
- Follow-up appointments
- Medication adherence
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class CareGapDetector:
    """
    Detects care gaps based on clinical guidelines and patient data.

    Guidelines implemented:
    - USPSTF preventive care recommendations
    - ADA diabetes care standards
    - AHA cardiovascular care guidelines
    - CDC vaccination schedules
    """

    # Age-based screening recommendations
    SCREENING_GUIDELINES = {
        "mammography": {
            "min_age": 40,
            "max_age": 74,
            "frequency_months": 24,  # Every 2 years
            "gender": "female",
            "priority": "high"
        },
        "colonoscopy": {
            "min_age": 45,
            "max_age": 75,
            "frequency_months": 120,  # Every 10 years
            "priority": "high"
        },
        "bone_density": {
            "min_age": 65,
            "gender": "female",
            "frequency_months": 24,
            "priority": "medium"
        },
        "prostate_screening": {
            "min_age": 50,
            "max_age": 70,
            "gender": "male",
            "frequency_months": 12,
            "priority": "medium"
        },
        "lipid_panel": {
            "min_age": 40,
            "frequency_months": 60,  # Every 5 years
            "priority": "medium"
        }
    }

    # Condition-specific care requirements
    CONDITION_CARE_REQUIREMENTS = {
        "diabetes": [
            {
                "name": "A1C testing",
                "frequency_months": 3,
                "priority": "high",
                "description": "Hemoglobin A1C test for diabetes monitoring"
            },
            {
                "name": "diabetic_eye_exam",
                "frequency_months": 12,
                "priority": "high",
                "description": "Annual dilated eye exam for diabetic retinopathy screening"
            },
            {
                "name": "diabetic_foot_exam",
                "frequency_months": 12,
                "priority": "medium",
                "description": "Annual comprehensive foot examination"
            },
            {
                "name": "kidney_function_test",
                "frequency_months": 12,
                "priority": "high",
                "description": "Annual urine albumin and serum creatinine testing"
            }
        ],
        "hypertension": [
            {
                "name": "blood_pressure_check",
                "frequency_months": 6,
                "priority": "high",
                "description": "Blood pressure monitoring"
            },
            {
                "name": "lipid_panel",
                "frequency_months": 12,
                "priority": "medium",
                "description": "Annual lipid panel"
            }
        ],
        "cardiovascular": [
            {
                "name": "ecg",
                "frequency_months": 12,
                "priority": "medium",
                "description": "Annual electrocardiogram"
            },
            {
                "name": "lipid_panel",
                "frequency_months": 6,
                "priority": "high",
                "description": "Lipid panel monitoring"
            }
        ]
    }

    # Vaccination recommendations
    VACCINATION_GUIDELINES = {
        "influenza": {
            "frequency_months": 12,
            "min_age": 6,  # months
            "priority": "medium",
            "description": "Annual influenza vaccination"
        },
        "pneumococcal": {
            "min_age": 65,
            "priority": "high",
            "description": "Pneumococcal vaccination for adults 65+"
        },
        "covid19_booster": {
            "frequency_months": 6,
            "min_age": 6,  # months
            "priority": "medium",
            "description": "COVID-19 booster vaccination"
        },
        "tdap": {
            "frequency_months": 120,  # Every 10 years
            "priority": "low",
            "description": "Tetanus, diphtheria, and pertussis booster"
        },
        "shingles": {
            "min_age": 50,
            "priority": "medium",
            "description": "Shingles (herpes zoster) vaccination"
        }
    }

    def __init__(self):
        """Initialize care gap detector."""
        pass

    async def detect_gaps(
        self,
        patient_data: Dict[str, Any],
        medical_history: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect care gaps for a patient.

        Args:
            patient_data: Patient demographics
            medical_history: FHIR medical history data

        Returns:
            list: Detected care gaps
        """
        logger.info(f"Detecting care gaps for patient {patient_data.get('patient_id')}")

        gaps = []

        # Get patient details
        age = patient_data.get('age')
        gender = patient_data.get('gender', '').lower()

        if not age:
            logger.warning("Patient age not available, skipping age-based screenings")
            return gaps

        # 1. Check preventive screenings
        screening_gaps = self._check_screening_gaps(age, gender)
        gaps.extend(screening_gaps)

        # 2. Check vaccinations
        vaccination_gaps = self._check_vaccination_gaps(age)
        gaps.extend(vaccination_gaps)

        # 3. Check condition-specific care (if medical history available)
        if medical_history and medical_history.get('conditions'):
            condition_gaps = self._check_condition_gaps(medical_history['conditions'])
            gaps.extend(condition_gaps)

        # Calculate statistics
        high_priority = len([g for g in gaps if g['priority'] == 'high'])
        overdue = len([g for g in gaps if g['overdue']])

        logger.info(f"Found {len(gaps)} care gaps ({high_priority} high priority, {overdue} overdue)")

        return gaps

    def _check_screening_gaps(self, age: int, gender: str) -> List[Dict[str, Any]]:
        """Check for preventive screening gaps."""
        gaps = []

        for screening_name, guideline in self.SCREENING_GUIDELINES.items():
            # Check age eligibility
            if age < guideline.get('min_age', 0):
                continue

            max_age = guideline.get('max_age')
            if max_age and age > max_age:
                continue

            # Check gender requirement
            required_gender = guideline.get('gender')
            if required_gender and gender != required_gender:
                continue

            # For now, assume all screenings are overdue (no historical data)
            # In production, would check FHIR observations/procedures

            frequency = guideline.get('frequency_months', 12)
            due_date = datetime.now() - timedelta(days=frequency * 30)

            gaps.append({
                "gap_type": "screening",
                "description": f"{screening_name.replace('_', ' ').title()} screening due",
                "priority": guideline['priority'],
                "due_date": due_date.strftime("%Y-%m-%d"),
                "overdue": True,  # Assume overdue without historical data
                "recommendation": f"Schedule {screening_name.replace('_', ' ')} screening"
            })

        return gaps

    def _check_vaccination_gaps(self, age: int) -> List[Dict[str, Any]]:
        """Check for vaccination gaps."""
        gaps = []

        for vaccine_name, guideline in self.VACCINATION_GUIDELINES.items():
            # Check age eligibility
            min_age = guideline.get('min_age', 0)

            # Convert months to years if needed
            if min_age < 10:  # Assume this is in months
                min_age_years = min_age / 12
            else:
                min_age_years = min_age

            if age < min_age_years:
                continue

            # For annual vaccines, assume due
            frequency = guideline.get('frequency_months')

            if frequency:
                # Recurring vaccine
                due_date = datetime.now() - timedelta(days=frequency * 30)
                overdue = True
            else:
                # One-time vaccine (check if patient is eligible)
                due_date = datetime.now()
                overdue = False

            gaps.append({
                "gap_type": "vaccination",
                "description": guideline['description'],
                "priority": guideline['priority'],
                "due_date": due_date.strftime("%Y-%m-%d") if frequency else None,
                "overdue": overdue,
                "recommendation": f"Administer {vaccine_name.replace('_', ' ')} vaccine"
            })

        return gaps

    def _check_condition_gaps(self, conditions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for condition-specific care gaps."""
        gaps = []

        # Extract active conditions
        active_conditions = [c for c in conditions if c.get('is_active')]

        for condition in active_conditions:
            condition_name = condition.get('name', '').lower()

            # Match condition to care requirements
            matched_requirements = []

            if 'diabetes' in condition_name:
                matched_requirements.extend(self.CONDITION_CARE_REQUIREMENTS.get('diabetes', []))

            if 'hypertension' in condition_name or 'blood pressure' in condition_name:
                matched_requirements.extend(self.CONDITION_CARE_REQUIREMENTS.get('hypertension', []))

            if 'cardio' in condition_name or 'heart' in condition_name:
                matched_requirements.extend(self.CONDITION_CARE_REQUIREMENTS.get('cardiovascular', []))

            # Create gaps for each requirement
            for req in matched_requirements:
                frequency = req['frequency_months']
                due_date = datetime.now() - timedelta(days=frequency * 30)

                gaps.append({
                    "gap_type": "disease_management",
                    "description": f"{req['description']} for {condition['name']}",
                    "priority": req['priority'],
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "overdue": True,  # Assume overdue without historical data
                    "recommendation": f"Schedule {req['name'].replace('_', ' ')}"
                })

        return gaps

    async def get_gap_summary(self, gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for care gaps.

        Args:
            gaps: List of detected gaps

        Returns:
            dict: Gap summary with counts and priorities
        """
        return {
            "total_gaps": len(gaps),
            "high_priority_count": len([g for g in gaps if g['priority'] == 'high']),
            "medium_priority_count": len([g for g in gaps if g['priority'] == 'medium']),
            "low_priority_count": len([g for g in gaps if g['priority'] == 'low']),
            "overdue_count": len([g for g in gaps if g['overdue']]),
            "by_type": {
                "screening": len([g for g in gaps if g['gap_type'] == 'screening']),
                "vaccination": len([g for g in gaps if g['gap_type'] == 'vaccination']),
                "disease_management": len([g for g in gaps if g['gap_type'] == 'disease_management'])
            }
        }


# Global instance
care_gap_detector = CareGapDetector()
