"""
FHIR Client Service for interacting with HAPI FHIR Server.

Provides standardized access to FHIR R4 resources including:
- Patient resources
- Observations (vitals, lab results)
- Conditions (diagnoses, problems)
- MedicationStatements
- Procedures
- Allergies and Intolerances
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from fhirpy import SyncFHIRClient
from fhirpy.base.exceptions import ResourceNotFound, OperationOutcome

from src.api.config import settings

logger = logging.getLogger(__name__)


class FHIRClient:
    """
    FHIR R4 client for healthcare data interoperability.

    Connects to HAPI FHIR server and provides methods for:
    - Creating, reading, updating, and deleting FHIR resources
    - Searching and querying patient data
    - Managing observations, conditions, medications
    - HIPAA-compliant data access
    """

    def __init__(self):
        """Initialize FHIR client."""
        self.use_mock = not settings.ENABLE_FHIR

        if not self.use_mock:
            try:
                self.client = SyncFHIRClient(
                    url=settings.FHIR_SERVER_URL,
                    authorization=None  # No auth for local HAPI FHIR
                )
                logger.info(f"FHIR client connected to {settings.FHIR_SERVER_URL}")
            except Exception as e:
                logger.warning(f"Failed to connect to FHIR server: {e}. Using mock mode.")
                self.use_mock = True
        else:
            logger.info("Using mock FHIR client (FHIR integration disabled)")

    # ==================== Patient Resources ====================

    def create_patient(
        self,
        identifier: str,
        given_name: str,
        family_name: str,
        birth_date: str,
        gender: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a FHIR Patient resource.

        Args:
            identifier: Patient identifier (e.g., MRN)
            given_name: First name
            family_name: Last name
            birth_date: Date of birth (YYYY-MM-DD)
            gender: Gender (male/female/other/unknown)
            **kwargs: Additional patient attributes

        Returns:
            dict: Created FHIR Patient resource
        """
        if self.use_mock:
            return self._mock_patient(identifier, given_name, family_name)

        try:
            patient = self.client.resource(
                'Patient',
                identifier=[{
                    'system': 'http://healthcare.azure.com/mrn',
                    'value': identifier
                }],
                name=[{
                    'use': 'official',
                    'given': [given_name],
                    'family': family_name
                }],
                birthDate=birth_date,
                gender=gender,
                **kwargs
            )
            patient.save()

            logger.info(f"Created FHIR Patient: {patient.id}")
            return patient.serialize()

        except Exception as e:
            logger.error(f"Error creating FHIR patient: {e}")
            raise

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a FHIR Patient by ID.

        Args:
            patient_id: FHIR Patient resource ID

        Returns:
            dict: FHIR Patient resource or None
        """
        if self.use_mock:
            return self._mock_patient(patient_id, "John", "Doe")

        try:
            patient = self.client.resources('Patient').search(_id=patient_id).first()
            if patient:
                return patient.serialize()
            return None

        except ResourceNotFound:
            logger.warning(f"FHIR Patient not found: {patient_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching FHIR patient: {e}")
            raise

    def search_patients(self, **search_params) -> List[Dict[str, Any]]:
        """
        Search for FHIR Patients.

        Args:
            **search_params: FHIR search parameters (name, identifier, birthdate, etc.)

        Returns:
            list: List of matching FHIR Patient resources
        """
        if self.use_mock:
            return [self._mock_patient("12345", "John", "Doe")]

        try:
            patients = self.client.resources('Patient').search(**search_params).fetch_all()
            return [p.serialize() for p in patients]

        except Exception as e:
            logger.error(f"Error searching FHIR patients: {e}")
            raise

    # ==================== Observation Resources ====================

    def create_observation(
        self,
        patient_id: str,
        code: str,
        code_system: str,
        display: str,
        value: Any,
        unit: Optional[str] = None,
        effective_datetime: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a FHIR Observation (vital signs, lab results, etc.).

        Args:
            patient_id: FHIR Patient reference
            code: Observation code (e.g., LOINC code)
            code_system: Code system (e.g., http://loinc.org)
            display: Human-readable name
            value: Observation value
            unit: Unit of measurement
            effective_datetime: When observation was made
            **kwargs: Additional attributes

        Returns:
            dict: Created FHIR Observation resource
        """
        if self.use_mock:
            return self._mock_observation(patient_id, code, display, value, unit)

        try:
            observation_data = {
                'resourceType': 'Observation',
                'status': 'final',
                'code': {
                    'coding': [{
                        'system': code_system,
                        'code': code,
                        'display': display
                    }]
                },
                'subject': {
                    'reference': f'Patient/{patient_id}'
                },
                'effectiveDateTime': effective_datetime or datetime.utcnow().isoformat(),
                **kwargs
            }

            # Add value based on type
            if isinstance(value, (int, float)):
                observation_data['valueQuantity'] = {
                    'value': value,
                    'unit': unit or '',
                    'system': 'http://unitsofmeasure.org',
                    'code': unit or ''
                }
            else:
                observation_data['valueString'] = str(value)

            observation = self.client.resource('Observation', **observation_data)
            observation.save()

            logger.info(f"Created FHIR Observation: {observation.id} for patient {patient_id}")
            return observation.serialize()

        except Exception as e:
            logger.error(f"Error creating FHIR observation: {e}")
            raise

    def get_patient_observations(
        self,
        patient_id: str,
        code: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get observations for a patient.

        Args:
            patient_id: FHIR Patient reference
            code: Filter by observation code (optional)
            category: Filter by category (e.g., vital-signs, laboratory)

        Returns:
            list: List of FHIR Observation resources
        """
        if self.use_mock:
            return [
                self._mock_observation(patient_id, "8310-5", "Body temperature", 98.6, "°F"),
                self._mock_observation(patient_id, "8867-4", "Heart rate", 72, "bpm")
            ]

        try:
            search_params = {'patient': patient_id}
            if code:
                search_params['code'] = code
            if category:
                search_params['category'] = category

            observations = self.client.resources('Observation').search(**search_params).fetch_all()
            return [obs.serialize() for obs in observations]

        except Exception as e:
            logger.error(f"Error fetching patient observations: {e}")
            raise

    # ==================== Condition Resources ====================

    def create_condition(
        self,
        patient_id: str,
        code: str,
        code_system: str,
        display: str,
        clinical_status: str = 'active',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a FHIR Condition (diagnosis, problem).

        Args:
            patient_id: FHIR Patient reference
            code: Condition code (e.g., ICD-10, SNOMED CT)
            code_system: Code system
            display: Human-readable condition name
            clinical_status: active/inactive/resolved
            **kwargs: Additional attributes

        Returns:
            dict: Created FHIR Condition resource
        """
        if self.use_mock:
            return self._mock_condition(patient_id, code, display, clinical_status)

        try:
            condition = self.client.resource(
                'Condition',
                clinicalStatus={
                    'coding': [{
                        'system': 'http://terminology.hl7.org/CodeSystem/condition-clinical',
                        'code': clinical_status
                    }]
                },
                code={
                    'coding': [{
                        'system': code_system,
                        'code': code,
                        'display': display
                    }]
                },
                subject={
                    'reference': f'Patient/{patient_id}'
                },
                **kwargs
            )
            condition.save()

            logger.info(f"Created FHIR Condition: {condition.id} for patient {patient_id}")
            return condition.serialize()

        except Exception as e:
            logger.error(f"Error creating FHIR condition: {e}")
            raise

    def get_patient_conditions(
        self,
        patient_id: str,
        clinical_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conditions for a patient.

        Args:
            patient_id: FHIR Patient reference
            clinical_status: Filter by status (active/inactive/resolved)

        Returns:
            list: List of FHIR Condition resources
        """
        if self.use_mock:
            return [
                self._mock_condition(patient_id, "E11.9", "Type 2 diabetes mellitus", "active"),
                self._mock_condition(patient_id, "I10", "Essential hypertension", "active")
            ]

        try:
            search_params = {'patient': patient_id}
            if clinical_status:
                search_params['clinical-status'] = clinical_status

            conditions = self.client.resources('Condition').search(**search_params).fetch_all()
            return [cond.serialize() for cond in conditions]

        except Exception as e:
            logger.error(f"Error fetching patient conditions: {e}")
            raise

    # ==================== MedicationStatement Resources ====================

    def create_medication_statement(
        self,
        patient_id: str,
        medication_code: str,
        medication_display: str,
        status: str = 'active',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a FHIR MedicationStatement.

        Args:
            patient_id: FHIR Patient reference
            medication_code: Medication code (e.g., RxNorm)
            medication_display: Medication name
            status: active/completed/stopped
            **kwargs: Additional attributes

        Returns:
            dict: Created FHIR MedicationStatement resource
        """
        if self.use_mock:
            return self._mock_medication(patient_id, medication_code, medication_display, status)

        try:
            med_statement = self.client.resource(
                'MedicationStatement',
                status=status,
                medicationCodeableConcept={
                    'coding': [{
                        'system': 'http://www.nlm.nih.gov/research/umls/rxnorm',
                        'code': medication_code,
                        'display': medication_display
                    }]
                },
                subject={
                    'reference': f'Patient/{patient_id}'
                },
                **kwargs
            )
            med_statement.save()

            logger.info(f"Created FHIR MedicationStatement: {med_statement.id}")
            return med_statement.serialize()

        except Exception as e:
            logger.error(f"Error creating FHIR medication statement: {e}")
            raise

    def get_patient_medications(
        self,
        patient_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get medication statements for a patient.

        Args:
            patient_id: FHIR Patient reference
            status: Filter by status (active/completed/stopped)

        Returns:
            list: List of FHIR MedicationStatement resources
        """
        if self.use_mock:
            return [
                self._mock_medication(patient_id, "314076", "Metformin 500mg", "active"),
                self._mock_medication(patient_id, "197361", "Lisinopril 10mg", "active")
            ]

        try:
            search_params = {'patient': patient_id}
            if status:
                search_params['status'] = status

            medications = self.client.resources('MedicationStatement').search(**search_params).fetch_all()
            return [med.serialize() for med in medications]

        except Exception as e:
            logger.error(f"Error fetching patient medications: {e}")
            raise

    # ==================== AllergyIntolerance Resources ====================

    def create_allergy(
        self,
        patient_id: str,
        code: str,
        display: str,
        clinical_status: str = 'active',
        criticality: str = 'low',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a FHIR AllergyIntolerance.

        Args:
            patient_id: FHIR Patient reference
            code: Allergen code
            display: Allergen name
            clinical_status: active/inactive/resolved
            criticality: low/high/unable-to-assess
            **kwargs: Additional attributes

        Returns:
            dict: Created FHIR AllergyIntolerance resource
        """
        if self.use_mock:
            return self._mock_allergy(patient_id, code, display, criticality)

        try:
            allergy = self.client.resource(
                'AllergyIntolerance',
                clinicalStatus={
                    'coding': [{
                        'system': 'http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical',
                        'code': clinical_status
                    }]
                },
                code={
                    'coding': [{
                        'system': 'http://snomed.info/sct',
                        'code': code,
                        'display': display
                    }]
                },
                patient={
                    'reference': f'Patient/{patient_id}'
                },
                criticality=criticality,
                **kwargs
            )
            allergy.save()

            logger.info(f"Created FHIR AllergyIntolerance: {allergy.id}")
            return allergy.serialize()

        except Exception as e:
            logger.error(f"Error creating FHIR allergy: {e}")
            raise

    def get_patient_allergies(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get allergies for a patient.

        Args:
            patient_id: FHIR Patient reference

        Returns:
            list: List of FHIR AllergyIntolerance resources
        """
        if self.use_mock:
            return [
                self._mock_allergy(patient_id, "387207008", "Penicillin", "high"),
                self._mock_allergy(patient_id, "300916003", "Peanuts", "high")
            ]

        try:
            allergies = self.client.resources('AllergyIntolerance').search(patient=patient_id).fetch_all()
            return [allergy.serialize() for allergy in allergies]

        except Exception as e:
            logger.error(f"Error fetching patient allergies: {e}")
            raise

    # ==================== Comprehensive Patient Summary ====================

    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive patient summary including all resources.

        Args:
            patient_id: FHIR Patient reference

        Returns:
            dict: Patient summary with all FHIR resources
        """
        try:
            summary = {
                'patient': self.get_patient(patient_id),
                'conditions': self.get_patient_conditions(patient_id),
                'medications': self.get_patient_medications(patient_id),
                'allergies': self.get_patient_allergies(patient_id),
                'observations': self.get_patient_observations(patient_id)
            }

            logger.info(f"Retrieved complete FHIR summary for patient {patient_id}")
            return summary

        except Exception as e:
            logger.error(f"Error fetching patient summary: {e}")
            raise

    # ==================== Mock Data Methods ====================

    def _mock_patient(self, identifier: str, given_name: str, family_name: str) -> Dict[str, Any]:
        """Generate mock FHIR Patient resource."""
        return {
            'resourceType': 'Patient',
            'id': identifier,
            'identifier': [{
                'system': 'http://healthcare.azure.com/mrn',
                'value': identifier
            }],
            'name': [{
                'use': 'official',
                'given': [given_name],
                'family': family_name
            }],
            'gender': 'unknown',
            'birthDate': '1980-01-01'
        }

    def _mock_observation(
        self,
        patient_id: str,
        code: str,
        display: str,
        value: Any,
        unit: Optional[str]
    ) -> Dict[str, Any]:
        """Generate mock FHIR Observation resource."""
        return {
            'resourceType': 'Observation',
            'id': f'obs-{code}-{patient_id}',
            'status': 'final',
            'code': {
                'coding': [{
                    'system': 'http://loinc.org',
                    'code': code,
                    'display': display
                }]
            },
            'subject': {'reference': f'Patient/{patient_id}'},
            'valueQuantity': {
                'value': value,
                'unit': unit
            },
            'effectiveDateTime': datetime.utcnow().isoformat()
        }

    def _mock_condition(
        self,
        patient_id: str,
        code: str,
        display: str,
        status: str
    ) -> Dict[str, Any]:
        """Generate mock FHIR Condition resource."""
        return {
            'resourceType': 'Condition',
            'id': f'cond-{code}-{patient_id}',
            'clinicalStatus': {
                'coding': [{
                    'system': 'http://terminology.hl7.org/CodeSystem/condition-clinical',
                    'code': status
                }]
            },
            'code': {
                'coding': [{
                    'system': 'http://hl7.org/fhir/sid/icd-10',
                    'code': code,
                    'display': display
                }]
            },
            'subject': {'reference': f'Patient/{patient_id}'}
        }

    def _mock_medication(
        self,
        patient_id: str,
        code: str,
        display: str,
        status: str
    ) -> Dict[str, Any]:
        """Generate mock FHIR MedicationStatement resource."""
        return {
            'resourceType': 'MedicationStatement',
            'id': f'med-{code}-{patient_id}',
            'status': status,
            'medicationCodeableConcept': {
                'coding': [{
                    'system': 'http://www.nlm.nih.gov/research/umls/rxnorm',
                    'code': code,
                    'display': display
                }]
            },
            'subject': {'reference': f'Patient/{patient_id}'}
        }

    def _mock_allergy(
        self,
        patient_id: str,
        code: str,
        display: str,
        criticality: str
    ) -> Dict[str, Any]:
        """Generate mock FHIR AllergyIntolerance resource."""
        return {
            'resourceType': 'AllergyIntolerance',
            'id': f'allergy-{code}-{patient_id}',
            'clinicalStatus': {
                'coding': [{
                    'system': 'http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical',
                    'code': 'active'
                }]
            },
            'code': {
                'coding': [{
                    'system': 'http://snomed.info/sct',
                    'code': code,
                    'display': display
                }]
            },
            'patient': {'reference': f'Patient/{patient_id}'},
            'criticality': criticality
        }


# Global instance
fhir_client = FHIRClient()
