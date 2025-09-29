from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .base_model import BaseModel

# core value objects based on BfArM RD spec
@dataclass
class Coding(BaseModel):
    # coded value with system, code, version, display
    system: str = ""
    code: str = ""
    version: Optional[str] = None
    display: Optional[str] = None

@dataclass
class ICD10GM(BaseModel):
    # ICD-10-GM coding
    code: str = ""
    version: Optional[str] = None
    display: Optional[str] = None

@dataclass
class ICD0M(BaseModel):
    # ICD-O-M coding for morphology
    code: str = ""
    version: Optional[str] = None
    display: Optional[str] = None

@dataclass
class ICDT(BaseModel):
    # ICD-T coding for topography
    code: str = ""
    version: Optional[str] = None
    display: Optional[str] = None

@dataclass
class HPO(BaseModel):
    # human phenotype ontology term
    code: str = ""
    version: Optional[str] = None
    display: Optional[str] = None

@dataclass
class Orphanet(BaseModel):
    # orphanet rare disease coding
    code: str = ""
    version: Optional[str] = None
    display: Optional[str] = None

@dataclass
class AlphaIdSE(BaseModel):
    # alpha-ID-SE coding
    code: str = ""
    version: Optional[str] = None
    display: Optional[str] = None

# patient demographics
@dataclass
class Gender(BaseModel):
    # patient gender coding
    code: str = ""  # male, female, other, unknown
    display: Optional[str] = None

@dataclass
class VitalStatus(BaseModel):
    # patient vital status
    code: str = ""  # alive, deceased, unknown
    display: Optional[str] = None

@dataclass
class Age(BaseModel):
    # patient age info
    value: int = 0
    unit: str = "years"

# diagnosis related
@dataclass
class DiagnosisCategory(BaseModel):
    # diagnosis category
    code: str = ""  # primary, secondary, etc.
    display: Optional[str] = None

@dataclass
class VerificationStatus(BaseModel):
    # diagnosis verification status
    code: str = ""  # confirmed, provisional, differential, etc.
    display: Optional[str] = None

@dataclass
class FamilyControlLevel(BaseModel):
    # family control level for genetic analysis
    code: str = ""  # single-genome, duo-genome, trio-genome
    display: Optional[str] = None

@dataclass
class Diagnosis(BaseModel):
    # diagnosis info with multiple coding systems
    icd10: Optional[ICD10GM] = None
    icdO3M: Optional[ICD0M] = None
    icdO3T: Optional[ICDT] = None
    orphanet: Optional[Orphanet] = None
    alphaIdSE: Optional[AlphaIdSE] = None
    category: Optional[DiagnosisCategory] = None
    verificationStatus: Optional[VerificationStatus] = None
    familyControlLevel: Optional[FamilyControlLevel] = None
    onsetDate: Optional[str] = None  # YYYY-MM format
    recordedOn: Optional[str] = None  # YYYY-MM-DD format



# HPO terms
@dataclass
class HPOTerm(BaseModel):
    # HPO phenotype term
    value: HPO = field(default_factory=HPO)
    onsetDate: Optional[str] = None  # YYYY-MM format
    recordedOn: Optional[str] = None  # YYYY-MM-DD format

# care plan elements
@dataclass
class TherapyCategory(BaseModel):
    # therapy recommendation category
    code: str = ""  # symptomatic, causal
    display: Optional[str] = None

@dataclass
class TherapyType(BaseModel):
    # type of therapy
    code: str = ""
    display: Optional[str] = None

@dataclass
class TherapyRecommendation(BaseModel):
    # therapy recommendation
    category: TherapyCategory = field(default_factory=TherapyCategory)
    type: TherapyType = field(default_factory=TherapyType)
    issuedOn: Optional[str] = None

@dataclass
class StudyEnrollmentRecommendation(BaseModel):
    # study enrollment recommendation
    nctNumber: Optional[str] = None
    title: Optional[str] = None
    issuedOn: Optional[str] = None

@dataclass
class GeneticCounselingRecommendation(BaseModel):
    # genetic counseling recommendation
    reason: Optional[str] = None
    issuedOn: Optional[str] = None

@dataclass
class CarePlan(BaseModel):
    # care plan with recommendations
    issuedOn: Optional[str] = None
    therapyRecommendations: List[TherapyRecommendation] = field(default_factory=list)
    studyEnrollmentRecommendations: List[StudyEnrollmentRecommendation] = field(default_factory=list)
    geneticCounselingRecommendation: Optional[GeneticCounselingRecommendation] = None
    reevaluationRecommended: bool = False

# episode of care
@dataclass
class EpisodeOfCare(BaseModel):
    # episode of care info
    period: Dict[str, str] = field(default_factory=dict)  # start, end dates
    status: str = ""  # active, finished, etc.

# NGS report elements
@dataclass
class Sequencing(BaseModel):
    # sequencing info
    type: str = ""  # WES, WGS, Panel, etc.
    platform: Optional[str] = None
    kit: Optional[str] = None

@dataclass
class VariantType(BaseModel):
    # type of genetic variant
    code: str = ""  # SNV, CNV, SV, etc.
    display: Optional[str] = None

@dataclass
class Significance(BaseModel):
    # clinical significance of variant
    code: str = ""  # pathogenic, likely_pathogenic, etc.
    display: Optional[str] = None

@dataclass
class Zygosity(BaseModel):
    # zygosity of variant
    code: str = ""  # homozygous, heterozygous, etc.
    display: Optional[str] = None

@dataclass
class Variant(BaseModel):
    # genetic variant info
    chromosome: Optional[str] = None
    gene: Optional[str] = None
    dnaChange: Optional[str] = None
    proteinChange: Optional[str] = None
    type: Optional[VariantType] = None
    significance: Optional[Significance] = None
    zygosity: Optional[Zygosity] = None

@dataclass
class NGSReport(BaseModel):
    # NGS report info
    sequencing: Sequencing = field(default_factory=Sequencing)
    variants: List[Variant] = field(default_factory=list)
    issuedOn: Optional[str] = None

# patient info
@dataclass
class Patient(BaseModel):
    # patient demographic and basic info
    id: str = ""
    gender: Gender = field(default_factory=Gender)
    birthDate: Optional[str] = None
    age: Optional[Age] = None
    vitalStatus: VitalStatus = field(default_factory=VitalStatus)
    dateOfDeath: Optional[str] = None

# main schema
@dataclass
class KDKSchema(BaseModel):
    # complete KDK (BfArM RD) schema structure
    patient: Patient = field(default_factory=Patient)
    diagnoses: List[Diagnosis] = field(default_factory=list)
    hpoTerms: List[HPOTerm] = field(default_factory=list)
    carePlans: List[CarePlan] = field(default_factory=list)
    episodesOfCare: List[EpisodeOfCare] = field(default_factory=list)
    ngsReports: List[NGSReport] = field(default_factory=list)
    
    # metadata
    recordedOn: Optional[str] = None
    lastUpdate: Optional[str] = None