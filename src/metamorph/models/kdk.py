# KDK - main class for handling KDK data with auto parsing
import json
from pathlib import Path
from typing import Dict, Any, Union
from .parsers.kdk_parser import KDKParser
from .kdk_model import KDKSchema

class KDK:
    # main KDK class - auto parses JSON to KDK model objects
    # usage: kdk = KDK("path/file.json") or KDK(json_dict)
    
    def __init__(self, data: Union[str, Dict[str, Any]]):
        # init KDK with auto parsing
        # data: file path (str) or JSON data (dict)
        self.parser = KDKParser()
        self.raw_data = None
        self.schema = None
        
        # parse input data
        if isinstance(data, str):
            self._load_from_file(data)
        elif isinstance(data, dict):
            self._load_from_dict(data)
        else:
            raise ValueError("Data must be either a file path (string) or JSON dictionary")
    
    def _load_from_file(self, file_path: str):
        # load and parse KDK from JSON file
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"KDK file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
        
        self.schema = self.parser.parse(self.raw_data)
    
    def _load_from_dict(self, data: Dict[str, Any]):
        # load and parse KDK from dict
        self.raw_data = data
        self.schema = self.parser.parse(data)
    
    def get_patient_id(self) -> str:
        # get patient ID from parsed schema
        return self.schema.patient.id if self.schema and self.schema.patient else ""
    
    # def get_diagnoses_count(self) -> int:
    #     # get number of diagnoses
    #     return len(self.schema.diagnoses) if self.schema else 0
    
    # def get_hpo_terms_count(self) -> int:
    #     # get number of HPO terms
    #     return len(self.schema.hpoTerms) if self.schema else 0
    
    # def get_care_plans_count(self) -> int:
    #     # get number of care plans
    #     return len(self.schema.carePlans) if self.schema else 0
    
    def to_dict(self) -> Dict[str, Any]:
        # convert parsed schema back to dict
        return self.schema.to_dict() if self.schema else {}
    
    def __str__(self) -> str:
        # string representation of KDK object
        if not self.schema:
            return "KDK(empty)"
        
        return (f"KDK(patient_id={self.get_patient_id()}")

        # return (f"KDK(patient_id={self.get_patient_id()}, "
        #         f"diagnoses={self.get_diagnoses_count()}, "
        #         f"hpo_terms={self.get_hpo_terms_count()}, "
        #         f"care_plans={self.get_care_plans_count()})")
    
    def __repr__(self) -> str:
        # detailed representation of KDK object
        return self.__str__()