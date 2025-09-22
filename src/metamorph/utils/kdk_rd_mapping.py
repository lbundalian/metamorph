"""
KDK to RD Field Mapping Documentation

Based on:
- KDK (BfArM): https://github.com/dnpm-dip/central-data-node/tree/main/core/src/main/scala/de/dnpm/ccdn/core/bfarm/rd
- RD (SE-dip): https://ibmi-ut.atlassian.net/wiki/spaces/DRD/pages/1474938/Data+Model+-+SE+dip
"""

from typing import Dict, List, Any

class KDKRDMapping:
    """Comprehensive mapping between KDK and RD data structures."""
    
    # Patient mapping
    PATIENT_MAPPING = {
        "patient.id": "patient.id",
        "patient.gender.code": "patient.gender.code",
        "patient.gender.display": "patient.gender.display",
        "patient.birthDate": "patient.birthDate",
        "patient.age.value": "patient.age.value",
        "patient.age.unit": "patient.age.unit",
        "patient.vitalStatus.code": "patient.vitalStatus.code",
        "patient.dateOfDeath": "patient.dateOfDeath",
        # KDK doesn't have address/insurance in patient, comes from metadata
    }
    
    # Diagnosis mapping
    DIAGNOSIS_MAPPING = {
        "diagnoses[].icd10.code": "diagnoses[].codes[0].code",  # ICD-10-GM
        "diagnoses[].icd10.version": "diagnoses[].codes[0].version",
        "diagnoses[].orphanet.code": "diagnoses[].codes[1].code",  # Orphanet
        "diagnoses[].alphaIdSE.code": "diagnoses[].codes[2].code",  # Alpha-ID-SE
        "diagnoses[].category.code": "diagnoses[].category.code",
        "diagnoses[].verificationStatus.code": "diagnoses[].verificationStatus.code",
        "diagnoses[].familyControlLevel.code": "diagnoses[].familyControlLevel.code",
        "diagnoses[].onsetDate": "diagnoses[].onsetDate",
        "diagnoses[].recordedOn": "diagnoses[].recordedOn",
    }
    
    # HPO Terms mapping
    HPO_MAPPING = {
        "hpoTerms[].value.code": "hpoTerms[].value.code",
        "hpoTerms[].value.version": "hpoTerms[].value.version",
        "hpoTerms[].onsetDate": "hpoTerms[].onsetDate",
        "hpoTerms[].recordedOn": "hpoTerms[].recordedOn",
    }
    
    # Care Plan mapping
    CARE_PLAN_MAPPING = {
        "carePlans[].issuedOn": "carePlans[].issuedOn",
        "carePlans[].geneticCounselingRecommendation": "carePlans[].geneticCounselingRecommended",
        "carePlans[].reevaluationRecommended": "carePlans[].reevaluationRecommended",
        "carePlans[].therapyRecommendations[].category.code": "carePlans[].therapyRecommendations[].category.code",
        "carePlans[].therapyRecommendations[].type.code": "carePlans[].therapyRecommendations[].type.code",
        "carePlans[].studyEnrollmentRecommendations[].nctNumber": "carePlans[].studyEnrollmentRecommendations[].nctNumber",
    }
    
    # Episode of Care mapping
    EPISODE_MAPPING = {
        "episodesOfCare[].period.start": "episodesOfCare[].period.start",
        "episodesOfCare[].period.end": "episodesOfCare[].period.end",
        "episodesOfCare[].status.code": "episodesOfCare[].status.code",
    }
    
    # NGS Report mapping
    NGS_MAPPING = {
        "ngsReports[].sequencing.type.code": "ngsReports[].type.code",
        "ngsReports[].sequencing.platform": "ngsReports[].sequencingInfo.platform.code",
        "ngsReports[].variants[].chromosome": "ngsReports[].results.smallVariants[].chromosome",
        "ngsReports[].variants[].gene": "ngsReports[].results.smallVariants[].genes[].code",
        "ngsReports[].variants[].dnaChange": "ngsReports[].results.smallVariants[].gDNAChange",
        "ngsReports[].variants[].proteinChange": "ngsReports[].results.smallVariants[].proteinChange",
        "ngsReports[].variants[].type.code": "ngsReports[].results.smallVariants[].type.code",
        "ngsReports[].variants[].significance.code": "ngsReports[].results.smallVariants[].significance.code",
        "ngsReports[].variants[].zygosity.code": "ngsReports[].results.smallVariants[].zygosity.code",
    }
    
    @classmethod
    def get_all_mappings(cls) -> Dict[str, Dict[str, str]]:
        """Get all field mappings organized by category."""
        return {
            "patient": cls.PATIENT_MAPPING,
            "diagnosis": cls.DIAGNOSIS_MAPPING,
            "hpo": cls.HPO_MAPPING,
            "care_plan": cls.CARE_PLAN_MAPPING,
            "episode": cls.EPISODE_MAPPING,
            "ngs": cls.NGS_MAPPING,
        }
    
    @classmethod
    def get_required_kdk_fields(cls) -> List[str]:
        """Get list of required KDK fields for complete mapping."""
        return [
            "patient.id",
            "patient.gender.code",
            "patient.birthDate",
            "diagnoses[].icd10.code",
            "diagnoses[].verificationStatus.code",
            "diagnoses[].familyControlLevel.code",
            "hpoTerms[].value.code",
            "carePlans[].issuedOn",
            "episodesOfCare[].status.code",
        ]
    
    @classmethod
    def get_generated_rd_fields(cls) -> List[str]:
        """Get list of fields that are generated during mapping (not directly from KDK)."""
        return [
            "patient.id",  # Generated UUID if not present
            "patient.age.value",  # Calculated from birthDate
            "patient.site",  # Default DNPM site
            "diagnoses[].id",  # Generated UUID
            "hpoTerms[].id",  # Generated UUID
            "carePlans[].id",  # Generated UUID
            "episodesOfCare[].id",  # Generated UUID
            "ngsReports[].id",  # Generated UUID
        ]
    
    @classmethod
    def get_coding_systems(cls) -> Dict[str, str]:
        """Get standard coding systems used in the mapping."""
        return {
            "icd10gm": "http://fhir.de/CodeSystem/bfarm/icd-10-gm",
            "orphanet": "https://www.orpha.net",
            "alpha_id_se": "https://www.bfarm.de/DE/Kodiersysteme/Terminologien/Alpha-ID-SE",
            "hpo": "https://hpo.jax.org",
            "gender": "dnpm-dip/rd/patient/gender",
            "vital_status": "dnpm-dip/rd/patient/vital-status",
            "verification_status": "dnpm-dip/rd/diagnosis/verification-status",
            "family_control_level": "dnpm-dip/rd/diagnosis/family-control-level",
            "therapy_category": "dnpm-dip/rd/therapy/category",
            "therapy_type": "dnpm-dip/rd/therapy/type",
            "sequencing_type": "dnpm-dip/rd/ngs/sequencing-type",
            "variant_type": "dnpm-dip/rd/variant/type",
            "variant_significance": "dnpm-dip/rd/variant/significance",
            "variant_zygosity": "dnpm-dip/rd/variant/zygosity",
        }
    
    @classmethod
    def get_display_mappings(cls) -> Dict[str, Dict[str, str]]:
        """Get German display name mappings for coded values."""
        return {
            "gender": {
                "male": "Männlich",
                "female": "Weiblich",
                "other": "Andere",
                "unknown": "Unbekannt"
            },
            "vital_status": {
                "alive": "Lebend",
                "deceased": "Verstorben",
                "unknown": "Unbekannt"
            },
            "verification_status": {
                "confirmed": "Bestätigt",
                "provisional": "Vorläufig",
                "differential": "Differentialdiagnose",
                "refuted": "Widerlegt"
            },
            "family_control_level": {
                "single-genome": "Einzelgenom",
                "duo-genome": "Duo-Genom",
                "trio-genome": "Trio-Genom"
            },
            "therapy_category": {
                "symptomatic": "Symptomatisch",
                "causal": "Kausal"
            },
            "sequencing_type": {
                "exome": "Exom-Sequenzierung",
                "genome": "Genom-Sequenzierung",
                "panel": "Panel-Sequenzierung"
            }
        }