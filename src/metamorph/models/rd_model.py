
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .base_model import BaseModel

@dataclass
class Patient(BaseModel):
    id: str
    gender: Dict[str, str]
    birthDate: str
    address: Dict[str, str]  # municipalityCode
    healthInsurance: Optional[Dict[str, Any]] = None
    age: Optional[Dict[str, Any]] = None
    vitalStatus: Optional[Dict[str, Any]] = None
    site: Optional[Dict[str, str]] = None

@dataclass
class Diagnosis(BaseModel):
    id: str
    patient: Dict[str, str]
    recordedOn: str
    codes: List[Dict[str, str]]
    verificationStatus: Dict[str, str]
    familyControlLevel: Dict[str, str]
    onsetDate: Optional[str] = None  # yyyy-MM format
    hospitalization: Optional[Dict[str, Any]] = None
    notes: List[str] = field(default_factory=list)

@dataclass
class HPOTerm(BaseModel):
    id: str
    patient: Dict[str, str]
    recordedOn: str
    value: Dict[str, str]
    onsetDate: Optional[str] = None  # yyyy-MM format
    status: Optional[Dict[str, Any]] = None

@dataclass
class EpisodeOfCare(BaseModel):
    id: str
    patient: Dict[str, str]
    period: Dict[str, str]  # start and optional end date

@dataclass
class TherapyRecommendation(BaseModel):
    id: str
    patient: Dict[str, str]
    issuedOn: str
    category: Dict[str, str]
    type: Dict[str, str]
    medication: List[Dict[str, Any]] = field(default_factory=list)
    supportingVariants: List[Dict[str, Any]] = field(default_factory=list)
    notes: Optional[str] = None

@dataclass
class StudyEnrollmentRecommendation(BaseModel):
    id: str
    patient: Dict[str, str]
    issuedOn: str
    study: List[Dict[str, str]]
    supportingVariants: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ClinicalManagementRecommendation(BaseModel):
    id: str
    patient: Dict[str, str]
    issuedOn: str
    type: Dict[str, str]
    notes: List[str] = field(default_factory=list)

@dataclass
class NGSReport(BaseModel):
    id: str
    patient: Dict[str, str]
    issuedOn: str
    type: Dict[str, str]
    sequencingInfo: Optional[Dict[str, Any]] = None
    conclusion: Optional[Dict[str, str]] = None
    results: Optional[Dict[str, Any]] = None

@dataclass
class FollowUp(BaseModel):
    date: str
    patient: Dict[str, str]
    lastContactDate: Optional[str] = None
    patientStatus: Optional[Dict[str, str]] = None

@dataclass
class Therapy(BaseModel):
    id: str
    patient: Dict[str, str]
    recordedOn: str
    basedOn: Optional[Dict[str, str]] = None
    period: Optional[Dict[str, str]] = None
    category: Optional[Dict[str, str]] = None
    type: Optional[Dict[str, str]] = None
    medication: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

@dataclass
class CarePlan(BaseModel):
    id: str
    patient: Dict[str, str]
    issuedOn: str
    geneticCounselingRecommended: bool = False
    reevaluationRecommended: bool = False
    noSequencingPerformedReason: Optional[Dict[str, str]] = None
    therapyRecommendations: List[TherapyRecommendation] = field(default_factory=list)
    studyEnrollmentRecommendations: List[StudyEnrollmentRecommendation] = field(default_factory=list)
    clinicalManagementRecommendation: Optional[ClinicalManagementRecommendation] = None
    notes: List[str] = field(default_factory=list)

@dataclass
class RDSchema(BaseModel):
    patient: Patient
    episodesOfCare: List[EpisodeOfCare] = field(default_factory=list)
    diagnoses: List[Diagnosis] = field(default_factory=list)
    hpoTerms: List[HPOTerm] = field(default_factory=list)
    gmfcsStatus: List[Dict[str, Any]] = field(default_factory=list)
    hospitalization: Optional[Dict[str, Any]] = None
    ngsReports: List[NGSReport] = field(default_factory=list)
    carePlans: List[CarePlan] = field(default_factory=list)
    followUps: List[FollowUp] = field(default_factory=list)
    therapies: List[Dict[str, Any]] = field(default_factory=list)  # Therapy history structure