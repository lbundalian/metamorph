"""
KDK Morpher - Transforms KDK objects to different target schemas.

Clean Architecture:
- models/: Contains model/schema classes  
- morphers/: Contains conversion scripts between schemas (e.g., KDKMorpher)
- utils/: Contains other methods and classes
- models/parsers/: Contains parser classes under models

Your requested usage:
    # Create KDK object (auto-parses JSON to KDK model)
    kdk = KDK("path/to/kdk.json")
    
    # Create morpher and transform to target schema
    morpher = KDKMorpher()
    rd_object = morpher.morph(kdk, 'RD')  # Your exact API
    
    # Save and validate
    morpher.save(rd_object, "output.json")
    is_valid, message = morpher.validate(rd_object)
"""
from typing import Dict, Any, Union
from ..models.kdk import KDK  
from ..utils.validate_api import validate_with_api
import json
import tempfile
import os

class KDKMorpher:
    """
    KDK Morpher class that transforms KDK objects to different target schemas.
    
    Architecture:
    - Uses KDK objects from models/
    - Transforms using morphers/ (this class)
    - Validates using utils/
    - Parsers are in models/parsers/
    """
    
    SUPPORTED_SCHEMAS = ['RD']  # Will be extended for FHIR, HL7, etc.
    
    def __init__(self):
        """Initialize the KDK Morpher."""
        pass
    
    def morph(self, kdk_object: KDK, target_schema: str) -> Dict[str, Any]:
        """
        Transform KDK object to target schema.
        
        Args:
            kdk_object: KDK object containing parsed KDK data
            target_schema: Target schema string ('RD', more to be added later)
            
        Returns:
            Dictionary containing the transformed data (RD object)
            
        Raises:
            ValueError: If target_schema is not supported
            RuntimeError: If KDK object is not properly initialized
        """
        # Validate inputs
        if not isinstance(kdk_object, KDK):
            raise TypeError("First argument must be a KDK object")
        
        if target_schema not in self.SUPPORTED_SCHEMAS:
            raise ValueError(f"Unsupported target schema '{target_schema}'. "
                           f"Supported schemas: {', '.join(self.SUPPORTED_SCHEMAS)}")
        
        if not kdk_object.schema:
            raise RuntimeError("KDK object is not properly initialized or parsed")
        
        # Perform the transformation based on target schema
        if target_schema == 'RD':
            return self._morph_to_rd(kdk_object)
        
        # Future schemas will be added here
        # elif target_schema == 'FHIR':
        #     return self._morph_to_fhir(kdk_object)
        # elif target_schema == 'HL7':
        #     return self._morph_to_hl7(kdk_object)
        
        raise ValueError(f"Morpher for '{target_schema}' not implemented")
    
    def _morph_to_rd(self, kdk_object: KDK) -> Dict[str, Any]:
        """Transform KDK object to RD schema using parsed KDK model properties directly."""
        from ..models.rd_model import (
            Patient, Code, Age, VitalStatus, Address, Reference,
            Diagnosis, HPOTerm, TherapyRecommendation, CarePlan,
            EpisodeOfCare, Period, NGSReport, Variant, HealthInsurance
        )
        from datetime import datetime
        import uuid
        
        # Helper function for converting dataclass objects to dictionaries
        def to_dict(obj):
            """Convert dataclass objects to dictionaries."""
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if hasattr(value, '__dict__'):
                        result[key] = to_dict(value)
                    elif isinstance(value, list):
                        result[key] = [to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                    else:
                        result[key] = value
                return result
            return obj
        
        # Access the parsed KDK schema object directly - this is the key!
        kdk_schema = kdk_object.schema  # Access through KDK object property
        
        # Create RD Patient using KDK object properties
        rd_patient = Patient(
            id=kdk_schema.patient.id,  # Access through KDK object property
            gender=Code(
                code=kdk_schema.patient.gender.code,  # Access through KDK object property
                display=kdk_schema.patient.gender.display or "",
                system="http://hl7.org/fhir/administrative-gender"
            ),
            birthDate=kdk_schema.patient.birthDate or "",  # Access through KDK object property
            age=Age(
                value=kdk_schema.patient.age.value,
                unit=kdk_schema.patient.age.unit or "years"
            ) if kdk_schema.patient.age else None,  # Access through KDK object property
            vitalStatus=VitalStatus(
                code=kdk_schema.patient.vitalStatus.code or "alive",  # Access through KDK object property
                system="dnpm-dip/rd/patient/vital-status"
            ),
            dateOfDeath=kdk_schema.patient.dateOfDeath,  # Access through KDK object property
            address=Address(),  # Default - not in KDK model
            healthInsurance=HealthInsurance(
                type=Code(code="GKV", display="gesetzliche Krankenversicherung", system="http://fhir.de/CodeSystem/versicherungsart-de-basis")
            ),
            site=Code(code="default-site")
        )
        
        # Create RD Diagnoses using KDK object properties
        rd_diagnoses = []
        for kdk_diagnosis in kdk_schema.diagnoses:  # Access through KDK object property
            codes = []
            
            # Track which code types are present in the original data
            has_icd10 = bool(kdk_diagnosis.icd10)
            has_orphanet = bool(kdk_diagnosis.orphanet)
            has_alphaIdSE = bool(kdk_diagnosis.alphaIdSE)
            
            # Access diagnosis codes through KDK object properties
            if kdk_diagnosis.icd10:  # Access through KDK object property
                codes.append(Code(
                    code=kdk_diagnosis.icd10.code,  # Access through KDK object property
                    display=kdk_diagnosis.icd10.display or "",
                    version=kdk_diagnosis.icd10.version,
                    system="http://fhir.de/CodeSystem/bfarm/icd-10-gm"
                ))
            
            if kdk_diagnosis.orphanet:  # Access through KDK object property
                codes.append(Code(
                    code=kdk_diagnosis.orphanet.code,  # Access through KDK object property
                    display=kdk_diagnosis.orphanet.display or "",
                    version=kdk_diagnosis.orphanet.version,
                    system="http://www.orpha.net"
                ))
            
            if kdk_diagnosis.alphaIdSE:  # Access through KDK object property
                codes.append(Code(
                    code=kdk_diagnosis.alphaIdSE.code,  # Access through KDK object property
                    display=kdk_diagnosis.alphaIdSE.display or "",
                    version=kdk_diagnosis.alphaIdSE.version,
                    system="http://fhir.de/CodeSystem/alpha-id-se"
                ))
            
            rd_diagnosis = Diagnosis(
                id=str(uuid.uuid4()),
                patient=Reference(id=kdk_schema.patient.id, type="Patient"),  # Access through KDK object property
                recordedOn=kdk_diagnosis.recordedOn or datetime.now().strftime("%Y-%m-%d"),  # Access through KDK object property
                codes=codes,
                verificationStatus=Code(
                    code=kdk_diagnosis.verificationStatus.code if kdk_diagnosis.verificationStatus else "confirmed",  # Access through KDK object property
                    system="http://terminology.hl7.org/CodeSystem/condition-ver-status"
                ),
                familyControlLevel=Code(
                    code=kdk_diagnosis.familyControlLevel.code if kdk_diagnosis.familyControlLevel else "single-genome",  # Access through KDK object property
                    system="dnpm-dip/rd/diagnosis/family-control-level"
                ),
                onsetDate=kdk_diagnosis.onsetDate  # Access through KDK object property
            )
            
            # Check if any required codes are missing from the original data
            missing_codes = []
            if not has_icd10:
                missing_codes.append("ICD-10-GM")
            if not has_orphanet:
                missing_codes.append("ORDO")
            if not has_alphaIdSE:
                missing_codes.append("Alpha-ID-SE")
            
            # Add missingCodeReason if any codes are missing from original data
            if missing_codes:
                # Convert diagnosis to dict first, then add missingCodeReason
                diagnosis_dict = to_dict(rd_diagnosis)
                diagnosis_dict["missingCodeReason"] = {
                    "code": "no-matching-code",
                    "display": "Kein geeigneter Code (ICD-10-GM, ORDO, Alpha-ID-SE) verfügbar"
                }
                rd_diagnoses.append(diagnosis_dict)
            else:
                rd_diagnoses.append(rd_diagnosis)
        
        # Create RD HPO Terms using KDK object properties
        rd_hpo_terms = []
        for kdk_hpo in kdk_schema.hpoTerms:  # Access through KDK object property
            rd_hpo = HPOTerm(
                id=str(uuid.uuid4()),
                patient=Reference(id=kdk_schema.patient.id, type="Patient"),  # Access through KDK object property
                recordedOn=kdk_hpo.recordedOn or datetime.now().strftime("%Y-%m-%d"),  # Access through KDK object property
                value=Code(
                    code=kdk_hpo.value.code,  # Access through KDK object property
                    display=kdk_hpo.value.display or "",
                    version=kdk_hpo.value.version,
                    system="http://purl.obolibrary.org/obo/hp.owl"
                ),
                onsetDate=kdk_hpo.onsetDate  # Access through KDK object property
            )
            rd_hpo_terms.append(rd_hpo)
        
        # Create the final RD structure
        rd_data = {
            "patient": to_dict(rd_patient),
            "diagnoses": [to_dict(diag) for diag in rd_diagnoses],
            "hpoTerms": [to_dict(hpo) for hpo in rd_hpo_terms],
            "carePlans": [],  # Required by API
            "episodesOfCare": []  # Required by API
        }
        
        return rd_data
    
    def save(self, transformed_object: Dict[str, Any], output_path: str) -> bool:
        """
        Save transformed object to JSON file.
        
        Args:
            transformed_object: The transformed object dictionary to save
            output_path: Path where to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from pathlib import Path
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(transformed_object, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Transformed object saved to {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving transformed object to {output_path}: {e}")
            return False
    
    def validate(self, transformed_object: Dict[str, Any], target_schema: str = 'RD') -> tuple[bool, str]:
        """
        Validate transformed object against target schema API.
        
        Args:
            transformed_object: The transformed object to validate
            target_schema: The target schema to validate against
            
        Returns:
            Tuple of (is_valid: bool, response_message: str)
        """
        if target_schema not in self.SUPPORTED_SCHEMAS:
            return False, f"Validation not supported for schema '{target_schema}'"
        
        # Create temporary file for validation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(transformed_object, f, indent=2, ensure_ascii=False)
            temp_file = f.name
        
        try:
            # Validate using the API
            validation_result = validate_with_api(temp_file)
            
            # Process validation result with CLI-friendly messages
            return self._parse_validation_response(validation_result)
                
        except Exception as e:
            return False, f"Validation exception: {str(e)}"
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass  # Ignore cleanup errors
    
    def _parse_validation_response(self, validation_result: dict) -> tuple[bool, str]:
        """
        Parse API validation response into CLI-friendly messages.
        
        Args:
            validation_result: Raw validation result from API
            
        Returns:
            Tuple of (is_valid: bool, cli_message: str)
        """
        # Handle API errors
        if "error" in validation_result:
            error = validation_result["error"]
            
            # Special case: Plain text "Valid" response
            if (error == "Invalid JSON response" and 
                validation_result.get("raw_response") == "Valid"):
                return True, "✅ Schema validation passed"
            
            # Handle different error types with friendly messages
            if "timed out" in error.lower():
                return False, "🕒 API request timed out - please try again"
            elif "curl command failed" in error.lower():
                return False, f"🌐 Network error (curl failed): {validation_result.get('stderr', 'Unknown error')}"
            elif "file not found" in error.lower():
                return False, "📁 File not found for validation"
            else:
                return False, f"❌ API Error: {error}"
        
        # Handle validation errors (schema violations)
        if "errors" in validation_result and validation_result["errors"]:
            errors = validation_result["errors"]
            error_count = len(errors)
            
            # Create user-friendly error summary
            cli_message = f"🔍 Found {error_count} validation error{'s' if error_count > 1 else ''}:\n"
            
            for i, error in enumerate(errors[:5], 1):  # Show max 5 errors
                # Clean up error message
                clean_error = self._format_error_message(error)
                cli_message += f"   {i}. {clean_error}\n"
            
            if error_count > 5:
                cli_message += f"   ... and {error_count - 5} more error{'s' if error_count - 5 > 1 else ''}"
            
            return False, cli_message.rstrip()
        
        # Handle successful validation
        if validation_result.get("validation_successful", True):
            return True, "✅ Schema validation passed successfully"
        
        # Default case
        return True, "✅ Validation completed"
    
    def _format_error_message(self, error: str) -> str:
        """
        Format individual error messages to be more CLI-friendly.
        
        Args:
            error: Raw error message from API
            
        Returns:
            Formatted CLI-friendly error message
        """
        # Handle string representation of dictionaries
        if error.startswith("{'severity'"):
            try:
                # Try to extract details from string representation
                if "'details':" in error:
                    details_start = error.find("'details': '") + 12
                    details_end = error.find("'}", details_start)
                    if details_end > details_start:
                        details = error[details_start:details_end]
                        return self._humanize_field_error(details)
            except:
                pass
        
        # Handle direct field error messages
        if ":" in error and "/" in error:
            return self._humanize_field_error(error)
        
        # Return cleaned up version of original error
        return error.replace("{'severity': 'error', 'details': '", "").replace("'}", "").strip("'\"")
    
    def _humanize_field_error(self, field_error: str) -> str:
        """
        Convert field error paths to human-readable messages.
        
        Args:
            field_error: Field error like "/patient/birthDate: error.expected.date.isoformat"
            
        Returns:
            Human-readable error message
        """
        # Common field mappings
        field_mappings = {
            "/patient/birthDate": "Patient birth date",
            "/patient/gender": "Patient gender",
            "/patient/healthInsurance": "Health insurance information",
            "/diagnoses": "Diagnosis information",
            "/hpoTerms": "HPO phenotype terms",
            "/carePlans": "Care plans",
            "/episodesOfCare": "Episodes of care",
            "/patient/address": "Patient address"
        }
        
        # Common error mappings
        error_mappings = {
            "error.expected.date.isoformat": "must be in ISO date format (YYYY-MM-DD)",
            "Found empty list where non-empty list expected": "cannot be empty (at least one item required)",
            "error.path.missing": "is required but missing",
            "Invalid 'code' value": "has invalid code value",
            "Fehlerhaftes Format: erste 5 Ziffern erwartet": "must be exactly 5 digits"
        }
        
        # Extract field path and error
        if ":" in field_error:
            field_path, error_desc = field_error.split(":", 1)
            field_path = field_path.strip()
            error_desc = error_desc.strip()
            
            # Get human-readable field name
            human_field = field_mappings.get(field_path, field_path.replace("/", " > ").strip(" > "))
            
            # Get human-readable error description
            human_error = error_mappings.get(error_desc, error_desc)
            
            return f"{human_field} {human_error}"
        
        return field_error
    
    def get_supported_schemas(self) -> list[str]:
        """Get list of supported target schemas."""
        return self.SUPPORTED_SCHEMAS.copy()
    
    def __str__(self) -> str:
        """String representation of the morpher."""
        return f"KDKMorpher(supported_schemas={self.SUPPORTED_SCHEMAS})"