
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .base_model import BaseModel

# SE-dip RD model based on https://ibmi-ut.atlassian.net/wiki/spaces/DRD/pages/1474938/Data+Model+-+SE+dip

@dataclass
class Code(BaseModel):
    # generic code with system, code, version, display
    system: str = ""
    code: str = ""
    version: Optional[str] = None
    display: Optional[str] = None

@dataclass
class Reference(BaseModel):
    # reference to another resource
    id: str = ""
    type: str = ""

@dataclass
class Period(BaseModel):
    # time period with start and end
    start: Optional[str] = None
    end: Optional[str] = None

@dataclass
class Age(BaseModel):
    # age representation
    value: int = 0
    unit: str = "Years"

@dataclass
class Address(BaseModel):
    # patient address info
    municipalityCode: str = ""

@dataclass
class HealthInsurance(BaseModel):
    # health insurance info
    type: Code = field(default_factory=Code)
    reference: Optional[Dict[str, str]] = None

@dataclass
class VitalStatus(BaseModel):
    # patient vital status
    code: str = "alive"  # alive, deceased, unknown
    display: str = "Lebend"
    system: str = "dnpm-dip/rd/patient/vital-status"

@dataclass
class Patient(BaseModel):
    # patient info according to SE-dip spec
    id: str = ""
    gender: Code = field(default_factory=Code)
    birthDate: str = ""
    age: Optional[Age] = None
    vitalStatus: VitalStatus = field(default_factory=VitalStatus)
    dateOfDeath: Optional[str] = None
    address: Address = field(default_factory=Address)
    healthInsurance: Optional[HealthInsurance] = None
    site: Optional[Code] = None  # DNMP Site-ID

@dataclass
class Diagnosis(BaseModel):
    # diagnosis according to SE-dip spec
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    recordedOn: str = ""
    codes: List[Code] = field(default_factory=list)  # ICD-10-GM, Orphanet, Alpha-ID-SE
    verificationStatus: Code = field(default_factory=Code)
    familyControlLevel: Code = field(default_factory=Code)
    onsetDate: Optional[str] = None  # YYYY-MM format
    hospitalization: Optional[Dict[str, Any]] = None
    notes: List[str] = field(default_factory=list)

@dataclass
class HPOTerm(BaseModel):
    # HPO phenotype term according to SE-dip spec
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    recordedOn: str = ""
    value: Code = field(default_factory=Code)
    onsetDate: Optional[str] = None
    status: Optional[Dict[str, Any]] = None

@dataclass
class TherapyRecommendation(BaseModel):
    # therapy recommendation according to SE-dip spec
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    issuedOn: str = ""
    category: Code = field(default_factory=Code)  # symptomatic, causal
    type: Code = field(default_factory=Code)
    medication: List[Code] = field(default_factory=list)
    supportingVariants: List[Reference] = field(default_factory=list)
    notes: Optional[str] = None

@dataclass
class StudyEnrollmentRecommendation(BaseModel):
    """Study enrollment recommendation."""
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    issuedOn: str = ""
    study: List[Reference] = field(default_factory=list)
    supportingVariants: List[Reference] = field(default_factory=list)

@dataclass
class ClinicalManagementRecommendation(BaseModel):
    """Clinical management recommendation."""
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    issuedOn: str = ""
    type: Code = field(default_factory=Code)
    notes: List[str] = field(default_factory=list)

@dataclass
class CarePlan(BaseModel):
    """Care plan according to SE-dip specification."""
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    issuedOn: str = ""
    geneticCounselingRecommended: bool = False
    reevaluationRecommended: bool = False
    noSequencingPerformedReason: Optional[Code] = None
    therapyRecommendations: List[TherapyRecommendation] = field(default_factory=list)
    studyEnrollmentRecommendations: List[StudyEnrollmentRecommendation] = field(default_factory=list)
    clinicalManagementRecommendation: Optional[ClinicalManagementRecommendation] = None
    notes: List[str] = field(default_factory=list)

@dataclass
class EpisodeOfCare(BaseModel):
    """Episode of care according to SE-dip specification."""
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    period: Period = field(default_factory=Period)

@dataclass
class GmfcsStatus(BaseModel):
    """GMFCS (Gross Motor Function Classification System) status."""
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    effectiveDate: str = ""
    value: Code = field(default_factory=Code)

@dataclass
class Hospitalization(BaseModel):
    """Hospitalization information."""
    numberOfStays: Code = field(default_factory=Code)
    numberOfDays: Code = field(default_factory=Code)

@dataclass
class Variant(BaseModel):
    """Genetic variant information."""
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    chromosome: Optional[str] = None
    genes: List[Code] = field(default_factory=list)
    localization: List[Code] = field(default_factory=list)
    startPosition: Optional[int] = None
    endPosition: Optional[int] = None
    ref: Optional[str] = None
    alt: Optional[str] = None
    gDNAChange: Optional[str] = None
    cDNAChange: Optional[str] = None
    proteinChange: Optional[str] = None
    acmgClass: Optional[Code] = None
    acmgCriteria: List[Dict[str, Any]] = field(default_factory=list)
    zygosity: Optional[Code] = None
    segregationAnalysis: Optional[Code] = None
    modeOfInheritance: Optional[Code] = None
    significance: Optional[Code] = None
    externalIds: List[Dict[str, str]] = field(default_factory=list)
    publications: List[Reference] = field(default_factory=list)

@dataclass
class SequencingInfo(BaseModel):
    """Sequencing platform information."""
    platform: Code = field(default_factory=Code)
    kit: Optional[str] = None

@dataclass
class Autozygosity(BaseModel):
    """Autozygosity observation."""
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    value: float = 0.0

@dataclass
class NGSReport(BaseModel):
    """NGS report according to SE-dip specification."""
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    issuedOn: str = ""
    type: Code = field(default_factory=Code)
    sequencingInfo: Optional[SequencingInfo] = None
    conclusion: Optional[Code] = None
    results: Optional[Dict[str, Any]] = None

@dataclass
class Therapy(BaseModel):
    """Therapy information."""
    id: str = ""
    patient: Reference = field(default_factory=Reference)
    recordedOn: str = ""
    basedOn: Optional[Reference] = None
    period: Optional[Period] = None
    category: Optional[Code] = None
    type: Optional[Code] = None
    medication: List[Code] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

@dataclass
class FollowUp(BaseModel):
    """Follow-up information."""
    date: str = ""
    patient: Reference = field(default_factory=Reference)
    lastContactDate: Optional[str] = None
    patientStatus: Optional[Code] = None

@dataclass
class RDSchema(BaseModel):
    """Complete RD schema according to SE-dip specification."""
    patient: Patient = field(default_factory=Patient)
    episodesOfCare: List[EpisodeOfCare] = field(default_factory=list)
    diagnoses: List[Diagnosis] = field(default_factory=list)
    hpoTerms: List[HPOTerm] = field(default_factory=list)
    gmfcsStatus: List[GmfcsStatus] = field(default_factory=list)
    hospitalization: Optional[Hospitalization] = None
    ngsReports: List[NGSReport] = field(default_factory=list)
    carePlans: List[CarePlan] = field(default_factory=list)
    followUps: List[FollowUp] = field(default_factory=list)
    therapies: List[Dict[str, Any]] = field(default_factory=list)  # Therapy history structure