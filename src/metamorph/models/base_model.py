from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class BaseModel:
    """Base class for all schema models."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model from dictionary."""
        return cls(**data)