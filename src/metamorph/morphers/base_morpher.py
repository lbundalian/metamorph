from abc import ABC, abstractmethod
from typing import Dict, Any, TypeVar, Generic

T = TypeVar('T')
U = TypeVar('U')

class BaseMorpher(ABC, Generic[T, U]):
    """Base morpher interface."""
    
    @abstractmethod
    def morph(self, source: T) -> U:
        """Morph source format to target format."""
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data structure."""
        pass

    def morph_and_validate(self, source: T) -> U:
        """Morph data and validate the result."""
        result = self.morph(source)
        if not self.validate(result if isinstance(result, dict) else result.to_dict()):
            raise ValueError("Morphed data failed validation")
        return result