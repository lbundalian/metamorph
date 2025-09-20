"""
JSON to RD Model Converter and Schema Validator.

This module provides functionality to convert RD JSON files to their corresponding
RD model objects and validate schema compliance.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import fields, is_dataclass

from ..models.rd_model import RDSchema, Patient, Diagnosis, HPOTerm, CarePlan
from .validators import ValidationError


class RDSchemaConverter:
    """Converter for RD JSON to RD model objects with schema validation."""
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
    
    def load_and_convert_from_file(self, file_path: Union[str, Path]) -> Tuple[Optional[RDSchema], List[str], List[str]]:
        """
        Load RD JSON from file and convert to RD model objects.
        
        Args:
            file_path: Path to the RD JSON file
            
        Returns:
            tuple: (RDSchema object or None, validation_errors, validation_warnings)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self.convert_from_dict(data)
            
        except FileNotFoundError:
            return None, [f"File not found: {file_path}"], []
        except json.JSONDecodeError as e:
            return None, [f"Invalid JSON format: {e}"], []
        except Exception as e:
            return None, [f"Error loading file: {e}"], []
    
    def convert_from_dict(self, data: Dict[str, Any]) -> Tuple[Optional[RDSchema], List[str], List[str]]:
        """
        Convert RD dictionary to RD model objects with validation.
        
        Args:
            data: Dictionary containing RD data
            
        Returns:
            tuple: (RDSchema object or None, validation_errors, validation_warnings)
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        try:
            # Validate basic structure
            if not self._validate_basic_structure(data):
                return None, self.validation_errors, self.validation_warnings
            
            # Convert patient
            patient = self._convert_patient(data.get("patient", {}))
            if not patient:
                return None, self.validation_errors, self.validation_warnings
            
            # Convert diagnoses
            diagnoses = self._convert_diagnoses(data.get("diagnoses", []))
            
            # Convert HPO terms
            hpo_terms = self._convert_hpo_terms(data.get("hpoTerms", []))
            
            # Convert care plans
            care_plans = self._convert_care_plans(data.get("carePlans", []))
            
            # Create RD schema
            rd_schema = RDSchema(
                patient=patient,
                diagnoses=diagnoses,
                hpoTerms=hpo_terms,
                carePlans=care_plans
            )
            
            # Final validation
            self._validate_rd_schema(rd_schema)
            
            return rd_schema, self.validation_errors, self.validation_warnings
            
        except Exception as e:
            self.validation_errors.append(f"Conversion error: {e}")
            return None, self.validation_errors, self.validation_warnings
    
    def validate_schema_compliance(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate if data complies with RD schema without full conversion.
        
        Args:
            data: Dictionary containing RD data
            
        Returns:
            tuple: (is_valid, validation_errors, validation_warnings)
        """
        rd_schema, errors, warnings = self.convert_from_dict(data)
        return rd_schema is not None and len(errors) == 0, errors, warnings
    
    def _validate_basic_structure(self, data: Dict[str, Any]) -> bool:
        """Validate basic RD structure requirements."""
        required_fields = ["patient"]
        
        for field in required_fields:
            if field not in data:
                self.validation_errors.append(f"Missing required top-level field: {field}")
                return False
        
        # Check optional but expected fields
        optional_fields = ["diagnoses", "hpoTerms", "carePlans"]
        for field in optional_fields:
            if field not in data:
                self.validation_warnings.append(f"Optional field missing: {field}")
        
        return True
    
    def _convert_patient(self, patient_data: Dict[str, Any]) -> Optional[Patient]:
        """Convert patient dictionary to Patient object."""
        try:
            # Required fields for Patient
            required_fields = ["id", "gender", "birthDate"]
            
            for field in required_fields:
                if field not in patient_data:
                    self.validation_errors.append(f"Patient missing required field: {field}")
                    return None
            
            # Validate specific field formats
            if not isinstance(patient_data.get("gender"), dict):
                self.validation_errors.append("Patient gender must be a dictionary with code, display, system")
                return None
            
            # Create Patient object with proper type handling
            patient = Patient(
                id=str(patient_data["id"]),
                gender=patient_data["gender"],
                birthDate=str(patient_data["birthDate"]),
                address=patient_data.get("address", {}),
                healthInsurance=patient_data.get("healthInsurance"),
                age=patient_data.get("age"),
                vitalStatus=patient_data.get("vitalStatus")
            )
            
            # Additional validations
            self._validate_patient_fields(patient, patient_data)
            
            return patient
            
        except Exception as e:
            self.validation_errors.append(f"Error converting patient: {e}")
            return None
    
    def _convert_diagnoses(self, diagnoses_data: List[Dict[str, Any]]) -> List[Diagnosis]:
        """Convert diagnoses list to Diagnosis objects."""
        diagnoses = []
        
        for i, diag_data in enumerate(diagnoses_data):
            try:
                # Required fields
                required_fields = ["id", "patient", "recordedOn", "codes"]
                
                for field in required_fields:
                    if field not in diag_data:
                        self.validation_errors.append(f"Diagnosis {i} missing required field: {field}")
                        continue
                
                # Validate codes is a list
                if not isinstance(diag_data.get("codes"), list):
                    self.validation_errors.append(f"Diagnosis {i} codes must be a list")
                    continue
                
                diagnosis = Diagnosis(
                    id=str(diag_data["id"]),
                    patient=diag_data["patient"],
                    recordedOn=str(diag_data["recordedOn"]),
                    codes=diag_data["codes"],
                    familyControlLevel=diag_data.get("familyControlLevel"),
                    verificationStatus=diag_data.get("verificationStatus")
                )
                
                diagnoses.append(diagnosis)
                
            except Exception as e:
                self.validation_errors.append(f"Error converting diagnosis {i}: {e}")
        
        return diagnoses
    
    def _convert_hpo_terms(self, hpo_data: List[Dict[str, Any]]) -> List[HPOTerm]:
        """Convert HPO terms list to HPOTerm objects."""
        hpo_terms = []
        
        for i, hpo_term_data in enumerate(hpo_data):
            try:
                # Required fields
                required_fields = ["id", "patient", "recordedOn", "value"]
                
                for field in required_fields:
                    if field not in hpo_term_data:
                        self.validation_errors.append(f"HPO term {i} missing required field: {field}")
                        continue
                
                # Validate value structure
                if not isinstance(hpo_term_data.get("value"), dict):
                    self.validation_errors.append(f"HPO term {i} value must be a dictionary")
                    continue
                
                hpo_term = HPOTerm(
                    id=str(hpo_term_data["id"]),
                    patient=hpo_term_data["patient"],
                    recordedOn=str(hpo_term_data["recordedOn"]),
                    value=hpo_term_data["value"],
                    status=hpo_term_data.get("status")
                )
                
                hpo_terms.append(hpo_term)
                
            except Exception as e:
                self.validation_errors.append(f"Error converting HPO term {i}: {e}")
        
        return hpo_terms
    
    def _convert_care_plans(self, care_plan_data: List[Dict[str, Any]]) -> List[CarePlan]:
        """Convert care plans list to CarePlan objects."""
        care_plans = []
        
        for i, cp_data in enumerate(care_plan_data):
            try:
                # Required fields
                required_fields = ["id", "patient", "issuedOn"]
                
                for field in required_fields:
                    if field not in cp_data:
                        self.validation_errors.append(f"Care plan {i} missing required field: {field}")
                        continue
                
                care_plan = CarePlan(
                    id=str(cp_data["id"]),
                    patient=cp_data["patient"],
                    issuedOn=str(cp_data["issuedOn"]),
                    geneticCounselingRecommended=bool(cp_data.get("geneticCounselingRecommended", False)),
                    reevaluationRecommended=bool(cp_data.get("reevaluationRecommended", False)),
                    therapyRecommendations=cp_data.get("therapyRecommendations", [])
                )
                
                care_plans.append(care_plan)
                
            except Exception as e:
                self.validation_errors.append(f"Error converting care plan {i}: {e}")
        
        return care_plans
    
    def _validate_patient_fields(self, patient: Patient, original_data: Dict[str, Any]):
        """Additional validation for patient fields."""
        # Validate gender structure
        gender = patient.gender
        if not all(key in gender for key in ["code", "display", "system"]):
            self.validation_warnings.append("Patient gender missing recommended fields: code, display, system")
        
        # Validate birth date format (basic check)
        birth_date = patient.birthDate
        if len(birth_date) != 10 or birth_date.count("-") != 2:
            self.validation_warnings.append("Patient birthDate should be in YYYY-MM-DD format")
        
        # Check for additional unexpected fields
        patient_fields = {f.name for f in fields(Patient)}
        for key in original_data:
            if key not in patient_fields:
                self.validation_warnings.append(f"Patient has unexpected field: {key}")
    
    def _validate_rd_schema(self, rd_schema: RDSchema):
        """Final validation of complete RD schema."""
        # Check relationships
        patient_id = rd_schema.patient.id
        
        # Validate all diagnoses reference the same patient
        for i, diagnosis in enumerate(rd_schema.diagnoses):
            if diagnosis.patient.get("id") != patient_id:
                self.validation_warnings.append(f"Diagnosis {i} references different patient ID")
        
        # Validate all HPO terms reference the same patient
        for i, hpo_term in enumerate(rd_schema.hpoTerms):
            if hpo_term.patient.get("id") != patient_id:
                self.validation_warnings.append(f"HPO term {i} references different patient ID")
        
        # Validate all care plans reference the same patient
        for i, care_plan in enumerate(rd_schema.carePlans):
            if care_plan.patient.get("id") != patient_id:
                self.validation_warnings.append(f"Care plan {i} references different patient ID")


def validate_rd_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Convenience function to validate an RD JSON file.
    
    Args:
        file_path: Path to the RD JSON file
        
    Returns:
        dict: Validation result with schema object, errors, and warnings
    """
    converter = RDSchemaConverter()
    rd_schema, errors, warnings = converter.load_and_convert_from_file(file_path)
    
    return {
        "is_valid": rd_schema is not None and len(errors) == 0,
        "rd_schema": rd_schema,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "patient_valid": rd_schema is not None,
            "diagnoses_count": len(rd_schema.diagnoses) if rd_schema else 0,
            "hpo_terms_count": len(rd_schema.hpoTerms) if rd_schema else 0,
            "care_plans_count": len(rd_schema.carePlans) if rd_schema else 0,
            "total_errors": len(errors),
            "total_warnings": len(warnings)
        }
    }


def validate_transformation_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to validate transformation output data.
    
    Args:
        data: Dictionary containing RD data from transformation
        
    Returns:
        dict: Validation result with schema object, errors, and warnings
    """
    converter = RDSchemaConverter()
    rd_schema, errors, warnings = converter.convert_from_dict(data)
    
    return {
        "is_valid": rd_schema is not None and len(errors) == 0,
        "rd_schema": rd_schema,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "patient_valid": rd_schema is not None,
            "diagnoses_count": len(rd_schema.diagnoses) if rd_schema else 0,
            "hpo_terms_count": len(rd_schema.hpoTerms) if rd_schema else 0,
            "care_plans_count": len(rd_schema.carePlans) if rd_schema else 0,
            "total_errors": len(errors),
            "total_warnings": len(warnings)
        }
    }