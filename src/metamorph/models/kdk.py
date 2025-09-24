"""
KDK - Main class for handling KDK data with automatic parsing.
"""
import json
from pathlib import Path
from typing import Dict, Any, Union
from .parsers.kdk_parser import KDKParser
from .kdk_model import KDKSchema

class KDK:
    """
    Main KDK class that automatically parses JSON data into KDK model objects.
    
    Usage:
        # From file
        kdk = KDK("path/to/kdk.json")
        
        # From dictionary
        kdk = KDK(json_data_dict)
        
        # Access parsed data
        patient = kdk.schema.patient
        diagnoses = kdk.schema.diagnoses
    """
    
    def __init__(self, data: Union[str, Dict[str, Any]]):
        """
        Initialize KDK object with automatic parsing.
        
        Args:
            data: Either a file path (string) or JSON data (dictionary)
        """
        self.parser = KDKParser()
        self.raw_data = None
        self.schema = None
        
        # Parse the input data
        if isinstance(data, str):
            self._load_from_file(data)
        elif isinstance(data, dict):
            self._load_from_dict(data)
        else:
            raise ValueError("Data must be either a file path (string) or JSON dictionary")
    
    def _load_from_file(self, file_path: str):
        """Load and parse KDK data from JSON file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"KDK file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
        
        self.schema = self.parser.parse(self.raw_data)
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """Load and parse KDK data from dictionary."""
        self.raw_data = data
        self.schema = self.parser.parse(data)
    
    def get_patient_id(self) -> str:
        """Get the patient ID from the parsed schema."""
        return self.schema.patient.id if self.schema and self.schema.patient else ""
    
    def get_diagnoses_count(self) -> int:
        """Get the number of diagnoses."""
        return len(self.schema.diagnoses) if self.schema else 0
    
    def get_hpo_terms_count(self) -> int:
        """Get the number of HPO terms."""
        return len(self.schema.hpoTerms) if self.schema else 0
    
    def get_care_plans_count(self) -> int:
        """Get the number of care plans."""
        return len(self.schema.carePlans) if self.schema else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the parsed schema back to dictionary format."""
        return self.schema.to_dict() if self.schema else {}
    
    def __str__(self) -> str:
        """String representation of the KDK object."""
        if not self.schema:
            return "KDK(empty)"
        
        return (f"KDK(patient_id={self.get_patient_id()}, "
                f"diagnoses={self.get_diagnoses_count()}, "
                f"hpo_terms={self.get_hpo_terms_count()}, "
                f"care_plans={self.get_care_plans_count()})")
    
    def __repr__(self) -> str:
        """Detailed representation of the KDK object."""
        return self.__str__()