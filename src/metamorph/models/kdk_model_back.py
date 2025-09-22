from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .base_model import BaseModel

@dataclass
class PriorDiagnostic(BaseModel):
    type: str = ""
    date: str = ""

@dataclass
class HPOTerm(BaseModel):
    text: str = ""
    system: str = ""
    code: str = ""
    version: str = ""

@dataclass
class TopographyHistology(BaseModel):
    text: str = ""
    system: str = ""
    code: str = ""
    version: str = ""

@dataclass
class Diagnosis(BaseModel):
    code: str = ""
    version: str = ""
    date: str = ""
    system: str = ""
    display: str = ""

@dataclass
class DiagnosisOd(BaseModel):
    germlineDiagnosisConfirmed: bool = False
    hpoTerms: List[HPOTerm] = field(default_factory=list)
    topography: TopographyHistology = field(default_factory=lambda: TopographyHistology())
    histology: TopographyHistology = field(default_factory=lambda: TopographyHistology())
    mainDiagnosis: Diagnosis = field(default_factory=lambda: Diagnosis())
    additionalDiagnoses: List[Diagnosis] = field(default_factory=list)
    ecogPerformanceStatusScore: str = ""
    libraryType: str = ""

@dataclass
class Case(BaseModel):
    priorDiagnostic: PriorDiagnostic = field(default_factory=PriorDiagnostic)
    diagnosisOd: DiagnosisOd = field(default_factory=DiagnosisOd)

@dataclass
class Scope(BaseModel):
    type: str = ""
    date: str = ""
    domain: str = ""

@dataclass
class MVConsent(BaseModel):
    version: str = ""
    scope: List[Scope] = field(default_factory=list)
    presentationDate: str = ""

@dataclass
class ResearchConsent(BaseModel):
    schemaVersion: str = ""
    scope: Dict[str, Any] = field(default_factory=dict)
    presentationDate: str = ""

@dataclass
class Submission(BaseModel):
    clinicalDataNodeId: str = ""
    type: str = ""
    submitterId: str = ""
    genomicDataCenterId: str = ""
    date: str = ""
    diseaseType: str = ""

@dataclass
class MetaData(BaseModel):
    gender: str = ""
    mvConsent: MVConsent = field(default_factory=MVConsent)
    birthDate: str = ""
    researchConsents: List[ResearchConsent] = field(default_factory=list)
    decisionToInclude: bool = False
    coverageType: str = ""
    tanC: str = ""
    submission: Submission = field(default_factory=Submission)
    molecularBoardDecisionDate: str = ""
    addressAGS: str = ""

@dataclass
class CarePlanOd(BaseModel):
    studyRecommended: bool = False
    counsellingRecommended: bool = False
    interventionRecommended: bool = False
    molecularBoardDecisionDate: str = ""
    reEvaluationRecommended: bool = False

@dataclass
class Plan(BaseModel):
    preventiveMeasures: List[Dict[str, str]] = field(default_factory=list)
    carePlanOd: CarePlanOd = field(default_factory=CarePlanOd)

@dataclass
class KDKSchema(BaseModel):
    case: Case = field(default_factory=Case)
    metaData: MetaData = field(default_factory=MetaData)
    plan: Plan = field(default_factory=Plan)