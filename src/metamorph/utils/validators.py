"""
Validation utilities for metamorph transformations.
"""

from typing import Dict, Any, List
import uuid
from datetime import datetime


class DataValidator:
    """Validator for medical data transformations."""
    
    @staticmethod
    def validate_kdk_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate KDK data structure.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required top-level structure
        required_sections = ["case", "metaData", "plan"]
        for section in required_sections:
            if section not in data:
                errors.append(f"Missing required section: {section}")
        
        # Validate metadata
        metadata = data.get("metaData", {})
        if not metadata.get("birthDate"):
            errors.append("Missing birthDate in metaData")
            
        # Validate case data
        case = data.get("case", {})
        diagnosis_od = case.get("diagnosisOd", {})
        
        # Check for at least one diagnosis or HPO term
        has_main_diagnosis = bool(diagnosis_od.get("mainDiagnosis", {}).get("code"))
        has_hpo_terms = bool(diagnosis_od.get("hpoTerms", []))
        
        if not has_main_diagnosis and not has_hpo_terms:
            errors.append("No diagnosis or HPO terms found")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_rd_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate RD data structure.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required top-level structure
        required_sections = ["patient", "diagnoses", "hpoTerms", "carePlans"]
        for section in required_sections:
            if section not in data:
                errors.append(f"Missing required section: {section}")
        
        # Validate patient
        patient = data.get("patient", {})
        required_patient_fields = ["id", "gender", "birthDate"]
        for field in required_patient_fields:
            if field not in patient:
                errors.append(f"Missing required patient field: {field}")
        
        # Validate ID format
        patient_id = patient.get("id", "")
        if patient_id and not DataValidator._is_valid_uuid(patient_id):
            errors.append("Patient ID is not a valid UUID")
        
        # Validate diagnoses structure
        diagnoses = data.get("diagnoses", [])
        for i, diagnosis in enumerate(diagnoses):
            if not diagnosis.get("id"):
                errors.append(f"Diagnosis {i} missing ID")
            if not diagnosis.get("codes"):
                errors.append(f"Diagnosis {i} missing codes")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_transformation_quality(source_kdk: Dict[str, Any], target_rd: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that transformation preserved important data.
        
        Returns:
            tuple: (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check if patient data was preserved
        kdk_metadata = source_kdk.get("metaData", {})
        rd_patient = target_rd.get("patient", {})
        
        if kdk_metadata.get("birthDate") != rd_patient.get("birthDate"):
            warnings.append("Birth date not preserved correctly")
            
        if kdk_metadata.get("gender") != rd_patient.get("gender", {}).get("code"):
            warnings.append("Gender not preserved correctly")
        
        # Check if diagnoses were preserved
        kdk_diagnoses = source_kdk.get("case", {}).get("diagnosisOd", {})
        rd_diagnoses = target_rd.get("diagnoses", [])
        
        main_diagnosis = kdk_diagnoses.get("mainDiagnosis", {})
        if main_diagnosis.get("code") and not any(
            main_diagnosis["code"] in str(diag.get("codes", [])) 
            for diag in rd_diagnoses
        ):
            warnings.append("Main diagnosis code not found in transformed data")
        
        # Check HPO terms
        kdk_hpo_count = len(kdk_diagnoses.get("hpoTerms", []))
        rd_hpo_count = len(target_rd.get("hpoTerms", []))
        
        if kdk_hpo_count > 0 and rd_hpo_count == 0:
            warnings.append("HPO terms were lost during transformation")
        elif kdk_hpo_count != rd_hpo_count:
            warnings.append(f"HPO term count mismatch: {kdk_hpo_count} -> {rd_hpo_count}")
        
        return len(warnings) == 0, warnings
    
    @staticmethod
    def _is_valid_uuid(uuid_string: str) -> bool:
        """Check if string is a valid UUID."""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _is_valid_date(date_string: str) -> bool:
        """Check if string is a valid date."""
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False


class TransformationError(Exception):
    """Exception raised when data transformation fails."""
    pass


class ValidationError(Exception):
    """Exception raised when data validation fails."""
    pass