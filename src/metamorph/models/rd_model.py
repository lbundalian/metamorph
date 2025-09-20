
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .base_model import BaseModel

@dataclass
class Patient(BaseModel):
    id: str
    gender: Dict[str, str]
    birthDate: str
    address: Dict[str, str]
    healthInsurance: Optional[Dict[str, Any]] = None
    age: Optional[Dict[str, Any]] = None
    vitalStatus: Optional[Dict[str, Any]] = None

@dataclass
class Diagnosis(BaseModel):
    id: str
    patient: Dict[str, str]
    recordedOn: str
    codes: List[Dict[str, str]]
    familyControlLevel: Optional[Dict[str, str]] = None
    verificationStatus: Optional[Dict[str, str]] = None

@dataclass
class HPOTerm(BaseModel):
    id: str
    patient: Dict[str, str]
    recordedOn: str
    value: Dict[str, str]
    status: Optional[Dict[str, Any]] = None

@dataclass
class CarePlan(BaseModel):
    id: str
    patient: Dict[str, str]
    issuedOn: str
    geneticCounselingRecommended: bool = False
    reevaluationRecommended: bool = False
    therapyRecommendations: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class RDSchema(BaseModel):
    patient: Patient
    diagnoses: List[Diagnosis] = field(default_factory=list)
    hpoTerms: List[HPOTerm] = field(default_factory=list)
    carePlans: List[CarePlan] = field(default_factory=list)