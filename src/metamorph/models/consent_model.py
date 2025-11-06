from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from .base_model import BaseModel


@dataclass
class Coding(BaseModel):
    # coded value with system, code, version, display
    system: Optional[str] = None
    code: str = ""
    version: Optional[str] = None
    display: Optional[str] = None



@dataclass(frozen=True)
class PolicyStatus:
    status: str
    date: str

@dataclass
class Provision:
    purpose: str
    date: str
    type: str

@dataclass
class Consent:
    date: str
    version: str
    
    # key: policy name/code, value: history of statuses (most recent last)
    provisions: List[Provision] = field(default_factory=list)



@dataclass
class Metadata:
    type: str
    transferTAN: str
    healthInsuranceType: Coding
    modelProjectConsent: Optional[Consent] = None
    researchConsents: List[Dict[str, Any]] = field(default_factory=list)
    reasonResearchConsentMissing: str = None
