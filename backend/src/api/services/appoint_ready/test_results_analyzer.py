"""
Test Results Analyzer Service for Appoint-Ready

Analyzes patient lab results and highlights clinically relevant findings.
Identifies abnormal values, trends, and critical results.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ...models.clinical import LabResult
from ...services.fhir.fhir_client import FHIRClient


class TestResultsAnalyzer:
    """Service for analyzing and highlighting relevant test results."""

    def __init__(self, db: Session, fhir_client: Optional[FHIRClient] = None):
        self.db = db
        self.fhir_client = fhir_client or FHIRClient()

    def get_relevant_test_results(
        self,
        patient_id: str,
        days_back: int = 180
    ) -> Dict[str, Any]:
        """
        Get and analyze relevant test results for a patient.

        Args:
            patient_id: Patient ID
            days_back: Number of days to look back for results

        Returns:
            Dictionary containing analyzed test results
        """
        # Get recent lab results from database
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        lab_results = (
            self.db.query(LabResult)
            .filter(
                and_(
                    LabResult.patient_id == patient_id,
                    LabResult.date_resulted >= cutoff_date
                )
            )
            .order_by(desc(LabResult.date_resulted))
            .all()
        )

        # Analyze results
        analyzed_results = []
        abnormal_count = 0
        critical_count = 0

        for result in lab_results:
            analyzed = self._analyze_result(result)
            analyzed_results.append(analyzed)

            if analyzed['status'] == 'critical':
                critical_count += 1
            elif analyzed['status'].startswith('abnormal'):
                abnormal_count += 1

        # Group by category and calculate trends
        grouped_results = self._group_by_category(analyzed_results)
        results_with_trends = self._calculate_trends(grouped_results)

        return {
            'patient_id': patient_id,
            'results': results_with_trends,
            'abnormal_count': abnormal_count,
            'critical_count': critical_count,
            'last_updated': datetime.utcnow().isoformat()
        }

    def _analyze_result(self, result: LabResult) -> Dict[str, Any]:
        """
        Analyze a single lab result for abnormalities.

        Args:
            result: LabResult model instance

        Returns:
            Analyzed result dictionary
        """
        status = self._determine_status(
            result.result_value,
            result.reference_range
        )

        category = self._categorize_test(result.test_name)

        return {
            'test_name': result.test_name,
            'value': result.result_value,
            'unit': result.unit or '',
            'reference_range': result.reference_range or 'N/A',
            'status': status,
            'date': result.date_resulted.isoformat() if result.date_resulted else None,
            'category': category
        }

    def _determine_status(
        self,
        value: str,
        reference_range: Optional[str]
    ) -> str:
        """
        Determine if a result is normal, abnormal, or critical.

        Args:
            value: Result value
            reference_range: Reference range string (e.g., "4.5-11.0")

        Returns:
            Status: 'normal', 'abnormal_high', 'abnormal_low', or 'critical'
        """
        if not reference_range or not value:
            return 'normal'

        try:
            # Parse numeric value
            numeric_value = float(value.split()[0])  # Handle values like "150 mg/dL"

            # Parse reference range
            if '-' in reference_range:
                parts = reference_range.split('-')
                low = float(parts[0].strip())
                high = float(parts[1].split()[0].strip())  # Handle "11.0 x10^9/L"

                # Determine status
                if numeric_value < low:
                    # Check if critically low
                    if numeric_value < low * 0.5:  # 50% below normal
                        return 'critical'
                    return 'abnormal_low'
                elif numeric_value > high:
                    # Check if critically high
                    if numeric_value > high * 1.5:  # 50% above normal
                        return 'critical'
                    return 'abnormal_high'
                else:
                    return 'normal'
            elif '<' in reference_range:
                # Handle "< 200 mg/dL" format
                max_val = float(reference_range.replace('<', '').strip().split()[0])
                if numeric_value > max_val:
                    if numeric_value > max_val * 1.5:
                        return 'critical'
                    return 'abnormal_high'
                return 'normal'
            elif '>' in reference_range:
                # Handle "> 60 mL/min" format
                min_val = float(reference_range.replace('>', '').strip().split()[0])
                if numeric_value < min_val:
                    if numeric_value < min_val * 0.5:
                        return 'critical'
                    return 'abnormal_low'
                return 'normal'
        except (ValueError, IndexError, AttributeError):
            # If parsing fails, assume normal
            return 'normal'

        return 'normal'

    def _categorize_test(self, test_name: str) -> str:
        """
        Categorize test into clinical groups.

        Args:
            test_name: Name of the test

        Returns:
            Category name
        """
        test_lower = test_name.lower()

        # Hematology
        if any(term in test_lower for term in ['hemoglobin', 'hematocrit', 'wbc', 'rbc', 'platelet', 'mcv', 'mch', 'cbc']):
            return 'hematology'

        # Chemistry/Metabolic
        if any(term in test_lower for term in ['glucose', 'sodium', 'potassium', 'calcium', 'creatinine', 'bun', 'cmp', 'bmp']):
            return 'chemistry'

        # Lipid Panel
        if any(term in test_lower for term in ['cholesterol', 'hdl', 'ldl', 'triglyceride']):
            return 'lipid_panel'

        # Liver Function
        if any(term in test_lower for term in ['alt', 'ast', 'bilirubin', 'albumin', 'alkaline phosphatase', 'ggt']):
            return 'liver_function'

        # Renal Function
        if any(term in test_lower for term in ['egfr', 'creatinine', 'bun', 'urea']):
            return 'renal_function'

        # Thyroid
        if any(term in test_lower for term in ['tsh', 't3', 't4', 'thyroid']):
            return 'thyroid_function'

        # Coagulation
        if any(term in test_lower for term in ['pt', 'ptt', 'inr', 'coagulation']):
            return 'coagulation'

        # Cardiac
        if any(term in test_lower for term in ['troponin', 'bnp', 'nt-probnp', 'ck-mb']):
            return 'cardiac_markers'

        # Default
        return 'other'

    def _group_by_category(self, results: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group results by category.

        Args:
            results: List of analyzed results

        Returns:
            Dictionary grouped by category
        """
        grouped = {}
        for result in results:
            category = result['category']
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(result)
        return grouped

    def _calculate_trends(self, grouped_results: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Calculate trends for repeated tests.

        Args:
            grouped_results: Results grouped by category

        Returns:
            Flattened list with trend information
        """
        results_with_trends = []

        for category, results in grouped_results.items():
            # Group by test name to find repeated tests
            test_groups = {}
            for result in results:
                test_name = result['test_name']
                if test_name not in test_groups:
                    test_groups[test_name] = []
                test_groups[test_name].append(result)

            # Calculate trends for each test
            for test_name, test_results in test_groups.items():
                # Sort by date (most recent first)
                sorted_results = sorted(
                    test_results,
                    key=lambda x: x['date'] if x['date'] else '',
                    reverse=True
                )

                # Add trend to most recent result if we have multiple results
                if len(sorted_results) >= 2:
                    latest = sorted_results[0]
                    previous = sorted_results[1]

                    try:
                        latest_val = float(latest['value'].split()[0])
                        previous_val = float(previous['value'].split()[0])

                        if latest_val > previous_val * 1.1:  # 10% increase
                            latest['trend'] = 'up'
                        elif latest_val < previous_val * 0.9:  # 10% decrease
                            latest['trend'] = 'down'
                        else:
                            latest['trend'] = 'stable'
                    except (ValueError, IndexError, AttributeError):
                        latest['trend'] = None

                    results_with_trends.append(latest)
                else:
                    # Single result, no trend
                    sorted_results[0]['trend'] = None
                    results_with_trends.append(sorted_results[0])

        return results_with_trends
