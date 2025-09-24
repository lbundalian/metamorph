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
from .kdk_to_rd_morpher import KDKToRDMorpher
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
        self.morphers = {
            'RD': KDKToRDMorpher()
        }
    
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
        """Transform KDK object to RD schema using the dedicated morpher."""
        morpher = self.morphers['RD']
        # The KDKToRDMorpher expects the raw dictionary data
        return morpher.morph(kdk_object.raw_data)
    
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
            
            # Process validation result
            if "error" in validation_result:
                # Check if it's actually a "Valid" response in plain text
                if (validation_result.get("error") == "Invalid JSON response" and 
                    validation_result.get("raw_response") == "Valid"):
                    return True, "Valid"
                else:
                    return False, f"Error: {validation_result['error']}"
            elif "errors" in validation_result and validation_result["errors"]:
                return False, f"Schema errors: {validation_result['errors']}"
            else:
                return True, "Valid"
                
        except Exception as e:
            return False, f"Validation exception: {str(e)}"
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass  # Ignore cleanup errors
    
    def get_supported_schemas(self) -> list[str]:
        """Get list of supported target schemas."""
        return self.SUPPORTED_SCHEMAS.copy()
    
    def __str__(self) -> str:
        """String representation of the morpher."""
        return f"KDKMorpher(supported_schemas={self.SUPPORTED_SCHEMAS})"