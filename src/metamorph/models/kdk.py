# KDK - main class for handling KDK data with auto parsing
import json
from pathlib import Path
from typing import Dict, Any, Union
from .parsers.kdk_parser import KDKParser
from .kdk_model import KDKSchema

class KDK:

    
    def __init__(self, data: Union[str, Dict[str, Any]]):

        self.parser = KDKParser()
        self.raw_data = None
        self.schema = None
        
        if isinstance(data, str):
            self._load_from_file(data)
        elif isinstance(data, dict):
            self._load_from_dict(data)
        else:
            raise ValueError("Data must be either a file path (string) or JSON dictionary")
    
    def _load_from_file(self, file_path: str):

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"KDK file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
        
        self.schema = self.parser.parse(self.raw_data)
    
    def _load_from_dict(self, data: Dict[str, Any]):
        self.raw_data = data
        self.schema = self.parser.parse(data)
    
    def get_patient_id(self) -> str:
        return self.schema.patient.id if self.schema and self.schema.patient else ""
    
    def to_dict(self) -> Dict[str, Any]:
        return self.schema.to_dict() if self.schema else {}
    
    def __str__(self) -> str:
        if not self.schema:
            return "KDK(empty)"
        
        return (f"KDK(patient_id={self.get_patient_id()}")
    
    def __repr__(self) -> str:
        return self.__str__()