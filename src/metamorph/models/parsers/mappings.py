# KDK Parser Mappings - Centralized constant mappings for KDK parser
from typing import Dict, Any
import re

class Mappings:
    
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
    
    # Verification status
    VERIFICATION_MAPPING = {
        "unconfirmed": "Keine genetische Diagnosestellung",
        "provisional": "Genetische Verdachtsdiagnose",
        "partial": "Klinischer Phanotyp nur partiell gelost",
        "confirmed": "Genetische Diagnose bestatigt"

    }

    # Family control level mappings
    FAMILY_CONTROL_MATCHING = { 
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

    # Therapy
    THERAPY_CATEGORY_MAP = {
        "symptomatic": "Symptomatisch",
        "causal": "Kausal",
    }

    THERAPY_TYPE_MAP = {
        "drug": "Medikamentos",
        "systemic-medication": "Medikaments systemisch",
        "targeted-medication": "Medikamentos zielgerichtet",
        "prevention-medication": "Medikamentos Prävention",
        "genetic": "Gentherapie",
        "prophylactic": "Prophylaxe",
        "early-detection": "Fruherkennung",
        "combination": "Kombinationstherapie",
        "nutrition": "Ernahrung",
        "other": "Andere"
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
    def get_purpose_code(purpose_code) -> str:
        purpose = ''
        purpose = Mappings.PURPOSE_MAPPING.get(purpose_code, "")
        return purpose

    @staticmethod
    def get_display(mapping: Dict[str, str], key: str, default: str = "Unknown") -> str:
        """Safely get display value from mapping with default fallback."""
        return mapping.get(key, default)
    
    @staticmethod
    def get_gender_display(gender_code: str) -> str:
        gender = ''
        gender =  MappingHelper.get_display(Mappings.GENDER_DISPLAY, gender_code, "Unbekannt")        
        return gender
    
    @staticmethod
    def get_insurance_display(insurance_code: str) -> str:
        insurance = ''
        insurance = MappingHelper.get_display(Mappings.INSURANCE_TYPE, insurance_code, "Unbekannt")
        return insurance
    
    @staticmethod
    def get_verification_display(verification_code: str) -> str:
        verification = ''
        verification = MappingHelper.get_display(Mappings.VERIFICATION_MAPPING, verification_code, "Keine Angabe")
        return verification

    # @staticmethod
    # def get_family_control_code(diagnostic_extent: str) -> str:
    #     norm_extent = re.sub(r'[\s\-_]+', '', diagnostic_extent.lower())
    #     code = Mappings.FAMILY_CONTROL_MATCHING.get(norm_extent, "no-record")
    #     return code

    @staticmethod
    def get_family_control(diagnostic_extent: str) -> Dict[str, str]:

        family_control = {}
        
        if not diagnostic_extent:
            return {"code": "no-record", "display": "Keine Angabe"}
        

        if diagnostic_extent in Mappings.FAMILY_CONTROL_MAPPING.keys():
            display = MappingHelper.get_display(Mappings.FAMILY_CONTROL_MAPPING, diagnostic_extent, "Keine Angabe")
            family_control["code"] = diagnostic_extent
            family_control["display"] = display
            return family_control

        norm_extent = re.sub(r'[\s\-_]+', '', diagnostic_extent.lower())
        
        # Pattern matching with regex
        if re.match(r'^single.*genom.*$', norm_extent):
            code = "single-genome"
        elif re.match(r'^duo.*genom.*$', norm_extent):
            code = "duo-genome"
        elif re.match(r'^trio.*genom.*$', norm_extent):
            code = "trio-genome"
        elif re.match(r'^(solo|individual|patient).*$', norm_extent):
            code = "single-genome"
        elif re.match(r'^(pair|two|2).*$', norm_extent):
            code = "duo-genome"
        elif re.match(r'^(triple|three|3).*$', norm_extent):
            code = "trio-genome"
        else:
            code = "no-record"
        
        display = MappingHelper.get_display(Mappings.FAMILY_CONTROL_MAPPING, code, "Keine Angabe")
        family_control["code"] = code
        family_control["display"] = display
        
        return family_control
    
    @staticmethod
    def get_therapy_category_display(category_code: str) -> str:
        therapy = ''
        therapy = MappingHelper.get_display(Mappings.THERAPY_CATEGORY_MAP, category_code, "")
        return therapy
    
    @staticmethod
    def get_therapy_type_display(category_code: str) -> str:
        therapy = ''
        therapy = MappingHelper.get_display(Mappings.THERAPY_TYPE_MAP, category_code, "")
        return therapy
    
    @staticmethod
    def get_acmg_class_display(acmg_class: str) -> str:
        acmg_class = ''
        acmg_class = MappingHelper.get_display(Mappings.ACMG_CLASS_MAP, acmg_class, "Uncertain significance")
        return acmg_class

    @staticmethod
    def get_significance_display(significance_code: str) -> str:
        sig = ''
        sig = MappingHelper.get_display(Mappings.SIGNIFICANCE_MAP, significance_code, "")
        return sig
    
    @staticmethod
    def get_acmg_criteria_display(criteria_code: str) -> str:
        acmg_criteria = ''
        acmg_criteria = MappingHelper.get_display(Mappings.ACMG_CRITERIA_MAPPING, criteria_code, "")
        return acmg_criteria
    
    @staticmethod
    def get_acmg_modifier_display(modifier_code: str) -> str:
        """Get ACMG modifier display value."""
        acmg_modifier = ''
        acmg_modifier = MappingHelper.get_display(Mappings.ACMG_MODIFIER_MAPPING, modifier_code, "")
        return acmg_modifier
    

    @staticmethod
    def get_segregation_analysis(seg: str) -> Dict[str, str]:
        segregation = {}
        norm_seg = re.sub(r'[\s\-_]+', '', seg.lower())

        if re.match(r'^not.*perform(ed)?$', norm_seg):
            code = "not-performed"
        elif re.match(r'^de.*novo$', norm_seg):
            code = "de-novo"
        elif re.match(r'^(from.*)?(father|paternal)$', norm_seg):
            code = "from-father"
        elif re.match(r'^(from.*)?(mother|maternal)$', norm_seg):
            code = "from-mother"
        elif re.match(r'^(from.*)?(both|mother.*father|father.*mother|parents|biparental)$', norm_seg):
            code = "from-both-parents"
        
        seg_display = Mappings.SEGREGATION_ANALYSIS_MAP.get(code, "")
        segregation["code"] = code
        segregation["display"] = seg_display

        return segregation  
        

    @staticmethod
    def get_zygosity(zygosity_code: str) -> Dict[str, str]:
        zygosity = {}
        norm_zygosity = re.sub(r'[\s\-_]+', '', zygosity_code.lower())
        if norm_zygosity in Mappings.ZYGOSITY_MAP.keys():
            display = MappingHelper.get_display(Mappings.ZYGOSITY_MAP, zygosity_code, "")
        else:

            if re.match(r'^hetero.*zyg.*$', norm_zygosity):
                code = MappingHelper.get_display(Mappings.ZYGOSITY_MAP, "heterozygous", "")
            elif re.match(r'^homo.*zyg.*$', norm_zygosity):
                code = MappingHelper.get_display(Mappings.ZYGOSITY_MAP, "homozygous", "")
            elif re.match(r'^(comp.*het|compound.*het).*$', norm_zygosity):
                code = MappingHelper.get_display(Mappings.ZYGOSITY_MAP, "comp-het", "")
            elif re.match(r'^hemi.*$', norm_zygosity):
                code = MappingHelper.get_display(Mappings.ZYGOSITY_MAP, "hemi", "")
            elif re.match(r'^homo.*plas.*$', norm_zygosity):
                code = MappingHelper.get_display(Mappings.ZYGOSITY_MAP, "homoplasmic", "")
            elif re.match(r'^hetero.*plas.*$', norm_zygosity):
                code = MappingHelper.get_display(Mappings.ZYGOSITY_MAP, "heteroplasmic", "")
            
            display = MappingHelper.get_display(Mappings.ZYGOSITY_MAP, code, "")
        
        zygosity["code"] = zygosity_code
        zygosity["display"] = display   
        
        return zygosity
    

    
    @staticmethod
    def get_inheritance(inheritance_code: str) -> Dict[str, str]:
        """Get mode of inheritance display value with pattern matching."""
        inheritance = {}
        
        if not inheritance_code:
            return {"code": "", "display": ""}
        
        # Check if already in correct format
        if inheritance_code in Mappings.INHERITANCE_MAP.keys():
            display = MappingHelper.get_display(Mappings.INHERITANCE_MAP, inheritance_code, "")
            inheritance["code"] = inheritance_code
            inheritance["display"] = display
            return inheritance
        
        normalized = re.sub(r'[\s\-_]+', '', inheritance_code.lower())
        
        if re.match(r'^dom.*$', normalized):
            code = "dominant"
        elif re.match(r'^rec.*$', normalized):
            code = "recessive"
        elif re.match(r'^(x.*link|xchrom).*$', normalized):
            code = "X-linked"
        elif re.match(r'^(mito.*|mt).*$', normalized):
            code = "mitochondrial"
        elif re.match(r'^(uncl|unk|unknown).*$', normalized):
            code = "unclear"
        else:
            code = inheritance_code.lower()
        
        display = MappingHelper.get_display(Mappings.INHERITANCE_MAP, code, "")
        inheritance["code"] = code
        inheritance["display"] = display
        
        return inheritance
    
    @staticmethod
    def get_cnv_type_display(cnv_type_code: str) -> str:
        """Get CNV type display value."""
        return MappingHelper.get_display(Mappings.CNV_TYPE_MAP, cnv_type_code, "")
    
    @staticmethod
    def get_genomic_test_type(library_type: str) -> str:
        test_type = ''
        test_type = MappingHelper.get_display(Mappings.GENOMIC_TEST_MAP, library_type.lower(), "other")
        return test_type
    
    @staticmethod
    def get_genomic_test(test_code: str) -> Dict[str, str]:
        genomic_test = {}
        code = test_code.lower()
        display = MappingHelper.get_display(Mappings.GENOMIC_DISPLAY_MAP, code, "Other")
        genomic_test["code"] = code
        genomic_test["display"] = display
        return genomic_test

    @staticmethod
    def get_research_consent_reason(no_scope_justification: Any) -> Dict[str, str]:
        
        reason = {}

        if isinstance(no_scope_justification, str):
            justification_text = no_scope_justification.lower()
            
            if "patient" in justification_text and ("unable" in justification_text or "nicht möglich" in justification_text):
                code = "patient-inability"
            elif "patient" in justification_text and ("refus" in justification_text or "abgelehnt" in justification_text):
                code = "patient-refusal"
            elif "not returned" in justification_text or "nicht abgegeben" in justification_text:
                code = "consent-not-returned"
            elif "technical" in justification_text or "technisch" in justification_text:
                code = "technical-issues"
            elif "organizational" in justification_text or "organisatorisch" in justification_text:
                code = "organizational-issues"
            else:
                code ="other-patient-reason"
                
        elif isinstance(no_scope_justification, dict):
            code = no_scope_justification.get("reason", "other-patient-reason")
        else:
            code = "other-patient-reason"
        
        display = Mappings.REASON_MAPPING.get(code, "other-patient-reason")
        reason["code"] = code
        reason["display"] = display
        
        return reason
    


    @staticmethod
    def get_acmg_criteria_modifier(criteria_code: str) -> str:
        
        criteria_upper = criteria_code.upper()
        
        # Search through modifier groups to find the criteria
        for modifier, criteria_set in Mappings.ACMG_MODIFIER_GROUPS.items():
            if criteria_upper in criteria_set:
                return modifier
        
        return "" 
    @staticmethod
    def get_criteria_by_modifier(modifier_code: str) -> set:
        
        return Mappings.ACMG_MODIFIER_GROUPS.get(modifier_code.lower(), set())

    @staticmethod
    def normalize_chromosome(chrom: str) -> str:
        if not chrom:
            raise ValueError("Chromosome value cannot be empty")

        c = chrom.strip().lower()
        c = re.sub(r"^(chr|chromosome|chrm|chro|chrom)\s*", "", c)

        if c in {"m", "mt", "mitochondria"}:
            return "chrM"

        if c in {"x", "23"}:
            return "chrX"
        if c in {"y", "24"}:
            return "chrY"

        match = re.match(r"^0*(\d{1,2})$", c)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 22:
                return f"chr{num}"
            raise ValueError(f"Invalid chromosome number: {num}")

        raise ValueError(f"Unrecognized chromosome format: {chrom}")