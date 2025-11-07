# KDK Parser Mappings - Centralized constant mappings for KDK parser
from typing import Dict, Any

class KDKMappings:
    """Centralized mappings and constants for KDK parser."""
    
    # Gender mappings
    GENDER_DISPLAY = {
        "male": "Männlich", 
        "female": "Weiblich", 
        "other": "Sonstiges"
    }
    
    # Insurance type mappings
    INSURANCE_TYPE = {
        "AT": "Beihilfe",
        "BG": "Berufsgenossenschaft",
        "GKV": "Gesetzliche Krankenversicherung",
        "GPV": "Gesetzliche Pflegeversicherung",
        "PKV": "Private Krankenversicherung",
        "PPV": "Private Pflegeversicherung",
        "SALT": "Selbstzahler",
        "SCO": "Sozialhilfeträger",
        "ST": "Sonstige Kostenträger",
        "UNK": "Unbekannt"
    }
    
    # Purpose mappings for consent
    PURPOSE_MAPPING = {
        "mvSequencing": "sequencing",
        "reIdentification": "reidentification",
        "caseIdentification": "case-identification"
    }
    
    # Research consent missing reason mappings
    REASON_MAPPING = {
        "patient-inability": "Einwilligung durch den Patienten nicht möglich",
        "patient-refusal": "Einwilligung vom Patienten abgelehnt",
        "consent-not-returned": "Einwilligung vom Patienten nicht abgegeben",
        "other-patient-reason": "Anderer Patienten-bedingter Grund",
        "technical-issues": "Consent aus technischen Gründen nicht verfügbar",
        "organizational-issues": "Consent aus organisatorischen Gründen nicht verfügbar"
    }
    
    # Family control level mappings
    FC_MATCHING = { 
        "singleGenome": "single-genome",
        "duoGenome": "duo-genome",
        "trioGenome": "trio-genome"
    }
    
    FAMILY_CONTROL_MAPPING = {
        "single-genome": "Single-Genome",
        "duo-genome": "Duo-Genome", 
        "trio-genome": "Trio-Genome",
        "no-record": "Keine Angabe"
    }
    
    # ACMG class mappings
    ACMG_CLASS_MAP = {
        "1": "Benign",
        "2": "Likely benign",
        "3": "Uncertain significance",
        "4": "Likely pathogenic",
        "5": "Pathogenic",
    }
    
    # Diagnostic significance mappings
    SIGNIFICANCE_MAP = {
        "primary": "Variant in context of patient's disease",
        "incidental": "Incidental finding",
        "candidate": "Candidate variant"
    }
    
    # ACMG criteria mappings
    ACMG_CRITERIA_MAPPING = {
        # Pathogenic - Very Strong
        "PVS1": "Pathogenic Very Strong",
        
        # Pathogenic - Strong
        "PS1": "Pathogenic Strong",
        "PS2": "Pathogenic Strong",
        "PS3": "Pathogenic Strong",
        "PS4": "Pathogenic Strong",
        
        # Pathogenic - Moderate
        "PM1": "Pathogenic Moderate",
        "PM2": "Pathogenic Moderate",
        "PM3": "Pathogenic Moderate",
        "PM4": "Pathogenic Moderate",
        "PM5": "Pathogenic Moderate",
        "PM6": "Pathogenic Moderate",
        
        # Pathogenic - Supporting
        "PP1": "Pathogenic Supporting",
        "PP2": "Pathogenic Supporting",
        "PP3": "Pathogenic Supporting",
        "PP4": "Pathogenic Supporting",
        "PP5": "Pathogenic Supporting",
        
        # Benign - Standalone
        "BA1": "Benign Standalone",
        
        # Benign - Strong
        "BS1": "Benign Strong",
        "BS2": "Benign Strong",
        "BS3": "Benign Strong",
        "BS4": "Benign Strong",
        
        # Benign - Supporting
        "BP1": "Benign Supporting",
        "BP2": "Benign Supporting",
        "BP3": "Benign Supporting",
        "BP4": "Benign Supporting",
        "BP5": "Benign Supporting",
        "BP6": "Benign Supporting",
        "BP7": "Benign Supporting",
    }
    
    # ACMG modifier mappings
    ACMG_MODIFIER_MAPPING = {
        # Pathogenic evidence adjustments
        "VeryStrong": "Pathogenic Very Strong",
        "Strong": "Pathogenic Strong",
        "Moderate": "Pathogenic Moderate",
        "Supporting": "Pathogenic Supporting",
        
        # Benign evidence adjustments
        "Standalone": "Benign Standalone",
        "StrongBenign": "Benign Strong",
        "SupportingBenign": "Benign Supporting",
        
        # General adjustment modifiers
        "Upgraded": "Strength Increased",
        "Downgraded": "Strength Decreased",
        "NotMet": "Criterion Not Met",
    }
    
    # Zygosity mappings
    ZYGOSITY_MAP = {
        "heterozygous": "Heterozygous",
        "homozygous": "Homozygous",
        "comp-het": "Compound heterozygous",
        "hemi": "Hemizygous",
        "homoplasmic": "Homoplasmic",
        "heteroplasmic": "Heteroplasmic",
    }
    
    # Segregation analysis mappings
    SEGREGATION_ANALYSIS_NORM = {
        "notPerformed": "not-performed",
        "deNovo": "de-novo",
        "fromFather": "from-father",
        "fromMother": "from-mother",
        "fromMotherAndFather": "from-both-parents",
    }
    
    SEGREGATION_ANALYSIS_MAP = {
        "not-performed": "Not performed",
        "de-novo": "De novo",
        "from-father": "Transmitted from father",
        "from-mother": "Transmitted from mother",
        "from-both-parents": "Transmitted from father and mother",
    }
    
    # Inheritance mappings
    INHERITANCE_MAP = {
        "dominant": "Dominant",
        "recessive": "Recessive",
        "X-linked": "X-linked",
        "mitochondrial": "Mitochondrial",
        "unclear": "Unclear"
    }
    
    # CNV type mappings
    CNV_TYPE_MAP = {
        "gain": "Gain",
        "loss": "Loss"
    }
    
    # Genomic test mappings
    GENOMIC_TEST_MAP = {
        "wgs": "genome-short-read",
        "wgs_lr": "genome-long-read"
    }
    
    GENOMIC_DISPLAY_MAP = {
        "panel": "Panel",
        "exome": "Exome", 
        "genome-short-read": "Genome short-read",
        "genome-long-read": "Genome long-read",
        "single": "Single",
        "karyotyping": "Karyotyping",
        "array": "Array",
        "other": "Other"
    }
    
    # ACMG criteria grouped by modifier - cleaner organization
    ACMG_MODIFIER_GROUPS = {
        "pvs": {"PVS1"},
        "ps": {"PS1", "PS2", "PS3", "PS4"},
        "pm": {"PM1", "PM2", "PM3", "PM4", "PM5", "PM6"},
        "pp": {"PP1", "PP2", "PP3", "PP4", "PP5"},
        "ba": {"BA1"},
        "bs": {"BS1", "BS2", "BS3", "BS4"},
        "bp": {"BP1", "BP2", "BP3", "BP4", "BP5", "BP6", "BP7"}
    }


class MappingHelper:
    """Helper class for safe mapping lookups with defaults."""
    
    @staticmethod
    def get_display(mapping: Dict[str, str], key: str, default: str = "Unknown") -> str:
        """Safely get display value from mapping with default fallback."""
        return mapping.get(key, default)
    
    @staticmethod
    def get_gender_display(gender_code: str) -> str:
        """Get gender display value."""
        return MappingHelper.get_display(KDKMappings.GENDER_DISPLAY, gender_code, "Unbekannt")
    
    @staticmethod
    def get_insurance_display(insurance_code: str) -> str:
        """Get insurance type display value."""
        return MappingHelper.get_display(KDKMappings.INSURANCE_TYPE, insurance_code, "Unbekannt")
    
    @staticmethod
    def get_family_control_code(diagnostic_extent: str) -> str:
        """Get family control level code."""
        return MappingHelper.get_display(KDKMappings.FC_MATCHING, diagnostic_extent, "no-record")
    
    @staticmethod
    def get_family_control_display(fc_level: str) -> str:
        """Get family control level display value."""
        return MappingHelper.get_display(KDKMappings.FAMILY_CONTROL_MAPPING, fc_level, "Keine Angabe")
    
    @staticmethod
    def get_acmg_class_display(acmg_class: str) -> str:
        """Get ACMG class display value."""
        return MappingHelper.get_display(KDKMappings.ACMG_CLASS_MAP, acmg_class, "Uncertain significance")
    
    @staticmethod
    def get_significance_display(significance_code: str) -> str:
        """Get diagnostic significance display value."""
        return MappingHelper.get_display(KDKMappings.SIGNIFICANCE_MAP, significance_code, "")
    
    @staticmethod
    def get_acmg_criteria_display(criteria_code: str) -> str:
        """Get ACMG criteria display value."""
        return MappingHelper.get_display(KDKMappings.ACMG_CRITERIA_MAPPING, criteria_code, "")
    
    @staticmethod
    def get_acmg_modifier_display(modifier_code: str) -> str:
        """Get ACMG modifier display value."""
        return MappingHelper.get_display(KDKMappings.ACMG_MODIFIER_MAPPING, modifier_code, "")
    
    @staticmethod
    def get_zygosity_display(zygosity_code: str) -> str:
        """Get zygosity display value."""
        return MappingHelper.get_display(KDKMappings.ZYGOSITY_MAP, zygosity_code.lower(), "")
    
    @staticmethod
    def get_segregation_analysis_code(segregation_raw: str) -> str:
        """Get normalized segregation analysis code."""
        return MappingHelper.get_display(KDKMappings.SEGREGATION_ANALYSIS_NORM, segregation_raw, "")
    
    @staticmethod
    def get_segregation_analysis_display(segregation_code: str) -> str:
        """Get segregation analysis display value."""
        return MappingHelper.get_display(KDKMappings.SEGREGATION_ANALYSIS_MAP, segregation_code, "")
    
    @staticmethod
    def get_inheritance_display(inheritance_code: str) -> str:
        """Get mode of inheritance display value."""
        return MappingHelper.get_display(KDKMappings.INHERITANCE_MAP, inheritance_code, "")
    
    @staticmethod
    def get_cnv_type_display(cnv_type_code: str) -> str:
        """Get CNV type display value."""
        return MappingHelper.get_display(KDKMappings.CNV_TYPE_MAP, cnv_type_code, "")
    
    @staticmethod
    def get_genomic_test_code(library_type: str) -> str:
        """Get genomic test code."""
        return MappingHelper.get_display(KDKMappings.GENOMIC_TEST_MAP, library_type.lower(), "other")
    
    @staticmethod
    def get_genomic_test_display(test_code: str) -> str:
        """Get genomic test display value."""
        return MappingHelper.get_display(KDKMappings.GENOMIC_DISPLAY_MAP, test_code, "Other")
    
    @staticmethod
    def parse_research_consent_reason(no_scope_justification: Any) -> str:
        """Parse research consent missing reason from various formats."""
        if isinstance(no_scope_justification, str):
            justification_text = no_scope_justification.lower()
            
            if "patient" in justification_text and ("unable" in justification_text or "nicht möglich" in justification_text):
                return "patient-inability"
            elif "patient" in justification_text and ("refus" in justification_text or "abgelehnt" in justification_text):
                return "patient-refusal"
            elif "not returned" in justification_text or "nicht abgegeben" in justification_text:
                return "consent-not-returned"
            elif "technical" in justification_text or "technisch" in justification_text:
                return "technical-issues"
            elif "organizational" in justification_text or "organisatorisch" in justification_text:
                return "organizational-issues"
            else:
                return "other-patient-reason"
                
        elif isinstance(no_scope_justification, dict):
            return no_scope_justification.get("reason", "other-patient-reason")
        else:
            return "other-patient-reason"
    
    @staticmethod
    def get_acmg_criteria_modifier(criteria_code: str) -> str:
        
        criteria_upper = criteria_code.upper()
        
        # Search through modifier groups to find the criteria
        for modifier, criteria_set in KDKMappings.ACMG_MODIFIER_GROUPS.items():
            if criteria_upper in criteria_set:
                return modifier
        
        return "" 
    @staticmethod
    def get_criteria_by_modifier(modifier_code: str) -> set:
        
        return KDKMappings.ACMG_MODIFIER_GROUPS.get(modifier_code.lower(), set())
  