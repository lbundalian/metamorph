from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class BaseModel:
    # base class for all schema models
    
    def to_dict(self) -> Dict[str, Any]:
        # convert model to dict
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        # create model from dict
        return cls(**data)