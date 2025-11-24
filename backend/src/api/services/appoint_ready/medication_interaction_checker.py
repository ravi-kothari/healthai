"""
Medication Interaction Checker Service for Appoint-Ready

Checks for drug-drug interactions and provides clinical recommendations.
Integrates patient allergies and active medications for comprehensive review.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ...models.clinical import Medication, Allergy


class MedicationInteractionChecker:
    """Service for checking medication interactions and allergies."""

    # Drug interaction database (simplified - in production, use RxNorm/Med-RT API)
    INTERACTION_DATABASE = {
        ('warfarin', 'aspirin'): {
            'severity': 'severe',
            'description': 'Increased risk of bleeding',
            'clinical_effect': 'Both medications affect blood clotting, significantly increasing bleeding risk',
            'recommendation': 'Monitor INR closely. Consider alternative antiplatelet if possible. Watch for signs of bleeding.'
        },
        ('lisinopril', 'spironolactone'): {
            'severity': 'moderate',
            'description': 'Risk of hyperkalemia',
            'clinical_effect': 'Both medications can increase potassium levels',
            'recommendation': 'Monitor serum potassium levels regularly. Consider potassium-restricted diet.'
        },
        ('metformin', 'contrast dye'): {
            'severity': 'severe',
            'description': 'Risk of lactic acidosis',
            'clinical_effect': 'Contrast dye can impair kidney function, leading to metformin accumulation',
            'recommendation': 'Hold metformin before and 48 hours after contrast administration. Check renal function.'
        },
        ('simvastatin', 'clarithromycin'): {
            'severity': 'severe',
            'description': 'Increased risk of rhabdomyolysis',
            'clinical_effect': 'Clarithromycin inhibits metabolism of simvastatin, increasing muscle toxicity risk',
            'recommendation': 'Temporarily discontinue simvastatin during clarithromycin therapy. Monitor for muscle pain.'
        },
        ('fluoxetine', 'tramadol'): {
            'severity': 'moderate',
            'description': 'Risk of serotonin syndrome',
            'clinical_effect': 'Both medications increase serotonin levels',
            'recommendation': 'Monitor for serotonin syndrome symptoms: agitation, confusion, rapid heart rate, fever.'
        },
        ('methotrexate', 'nsaids'): {
            'severity': 'moderate',
            'description': 'Increased methotrexate toxicity',
            'clinical_effect': 'NSAIDs can reduce methotrexate clearance',
            'recommendation': 'Monitor methotrexate levels and complete blood count. Use lowest NSAID dose.'
        },
        ('digoxin', 'furosemide'): {
            'severity': 'moderate',
            'description': 'Risk of digoxin toxicity',
            'clinical_effect': 'Furosemide-induced hypokalemia increases digoxin toxicity risk',
            'recommendation': 'Monitor potassium and digoxin levels. Consider potassium supplementation.'
        },
        ('levothyroxine', 'calcium'): {
            'severity': 'mild',
            'description': 'Reduced levothyroxine absorption',
            'clinical_effect': 'Calcium can bind to levothyroxine in the gut',
            'recommendation': 'Separate administration by at least 4 hours. Monitor TSH levels.'
        },
        ('lisinopril', 'nsaids'): {
            'severity': 'moderate',
            'description': 'Reduced antihypertensive effect',
            'clinical_effect': 'NSAIDs can reduce effectiveness of ACE inhibitors and increase kidney injury risk',
            'recommendation': 'Monitor blood pressure and renal function. Use NSAIDs sparingly.'
        },
        ('warfarin', 'ciprofloxacin'): {
            'severity': 'severe',
            'description': 'Increased bleeding risk',
            'clinical_effect': 'Ciprofloxacin inhibits warfarin metabolism, increasing INR',
            'recommendation': 'Monitor INR more frequently during and after antibiotic therapy. May need warfarin dose adjustment.'
        }
    }

    def __init__(self, db: Session):
        self.db = db

    def get_medication_review(self, patient_id: str) -> Dict[str, Any]:
        """
        Perform comprehensive medication review including interaction checking.

        Args:
            patient_id: Patient ID

        Returns:
            Dictionary containing medication review data
        """
        # Get active medications
        medications = (
            self.db.query(Medication)
            .filter(
                and_(
                    Medication.patient_id == patient_id,
                    Medication.status == 'active'
                )
            )
            .all()
        )

        # Get allergies
        allergies = (
            self.db.query(Allergy)
            .filter(
                and_(
                    Allergy.patient_id == patient_id,
                    Allergy.status == 'active'
                )
            )
            .all()
        )

        # Format medications
        formatted_meds = [self._format_medication(med) for med in medications]

        # Check for interactions
        interactions = self._check_interactions(medications)

        # Format allergies
        formatted_allergies = [self._format_allergy(allergy) for allergy in allergies]

        # Count severe interactions
        severe_count = sum(1 for i in interactions if i['severity'] == 'severe')

        return {
            'patient_id': patient_id,
            'medications': formatted_meds,
            'interactions': interactions,
            'allergies': formatted_allergies,
            'total_medications': len(formatted_meds),
            'interaction_count': len(interactions),
            'severe_interaction_count': severe_count
        }

    def _format_medication(self, med: Medication) -> Dict[str, Any]:
        """
        Format medication for response.

        Args:
            med: Medication model instance

        Returns:
            Formatted medication dictionary
        """
        return {
            'medication_id': str(med.id),
            'name': med.name,
            'dosage': med.dosage,
            'frequency': med.frequency,
            'route': med.route,
            'start_date': med.start_date.isoformat() if med.start_date else None,
            'status': med.status,
            'prescriber': med.prescriber,
            'indication': med.notes  # Use notes field for indication
        }

    def _format_allergy(self, allergy: Allergy) -> Dict[str, Any]:
        """
        Format allergy for response.

        Args:
            allergy: Allergy model instance

        Returns:
            Formatted allergy dictionary
        """
        return {
            'allergen': allergy.allergen,
            'reaction': allergy.reaction,
            'severity': allergy.severity
        }

    def _check_interactions(self, medications: List[Medication]) -> List[Dict[str, Any]]:
        """
        Check for drug-drug interactions among active medications.

        Args:
            medications: List of Medication instances

        Returns:
            List of identified interactions
        """
        interactions = []
        interaction_id = 1

        # Compare each pair of medications
        for i, med1 in enumerate(medications):
            for med2 in medications[i + 1:]:
                interaction = self._find_interaction(med1.name, med2.name)
                if interaction:
                    interactions.append({
                        'interaction_id': str(interaction_id),
                        'medication_1': med1.name,
                        'medication_2': med2.name,
                        **interaction
                    })
                    interaction_id += 1

        # Sort by severity (severe first)
        severity_order = {'severe': 0, 'moderate': 1, 'mild': 2}
        interactions.sort(key=lambda x: severity_order.get(x['severity'], 3))

        return interactions

    def _find_interaction(self, med1_name: str, med2_name: str) -> Optional[Dict[str, str]]:
        """
        Find interaction between two medications.

        Args:
            med1_name: First medication name
            med2_name: Second medication name

        Returns:
            Interaction details if found, None otherwise
        """
        # Normalize medication names (lowercase, remove common suffixes)
        med1 = self._normalize_medication_name(med1_name)
        med2 = self._normalize_medication_name(med2_name)

        # Check both orders
        key1 = (med1, med2)
        key2 = (med2, med1)

        if key1 in self.INTERACTION_DATABASE:
            return self.INTERACTION_DATABASE[key1]
        elif key2 in self.INTERACTION_DATABASE:
            return self.INTERACTION_DATABASE[key2]

        return None

    def _normalize_medication_name(self, name: str) -> str:
        """
        Normalize medication name for comparison.

        Args:
            name: Medication name

        Returns:
            Normalized name
        """
        # Convert to lowercase
        normalized = name.lower().strip()

        # Remove common brand name suffixes and dose information
        suffixes_to_remove = [
            'er', 'xr', 'sr', 'cr',  # Extended release variants
            'mg', 'mcg', 'g',  # Dose units
            'tablet', 'tablets', 'capsule', 'capsules',
            'injection', 'solution', 'suspension'
        ]

        words = normalized.split()
        # Keep only the base drug name (usually first word)
        if words:
            base_name = words[0]
            # Remove any trailing dose numbers
            base_name = ''.join([c for c in base_name if not c.isdigit()])
            return base_name

        return normalized

    def add_interaction_rule(
        self,
        drug1: str,
        drug2: str,
        severity: str,
        description: str,
        clinical_effect: str,
        recommendation: str
    ):
        """
        Add a new interaction rule to the database.

        Args:
            drug1: First drug name
            drug2: Second drug name
            severity: Interaction severity (severe/moderate/mild)
            description: Brief description
            clinical_effect: Clinical effect explanation
            recommendation: Clinical recommendation
        """
        key = (drug1.lower(), drug2.lower())
        self.INTERACTION_DATABASE[key] = {
            'severity': severity,
            'description': description,
            'clinical_effect': clinical_effect,
            'recommendation': recommendation
        }
