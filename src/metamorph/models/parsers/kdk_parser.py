# KDK JSON parser - creates KDK model objects from raw JSON
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
from ..consent_model import *
from ..kdk_model import (
    Coding, KDKSchema, Patient, Gender, VitalStatus, Age, Diagnosis, ICD10GM, 
    AlphaIdSE, Orphanet, VerificationStatus, FamilyControlLevel,
    HPOTerm, HPO, CarePlan, TherapyRecommendation, TherapyCategory, 
    TherapyType, StudyEnrollmentRecommendation, GeneticCounselingRecommendation,
    EpisodeOfCare, NGSReport, Sequencing, Variant, VariantType, 
    Significance, Zygosity, DiagnosisCategory, HealthInsurance, SmallVariant,CopyNumberVariant, 
    StructuralVariant, ACMGCriterion, Reference
)
import re

class KDKParser:
    # parser to convert raw KDK JSON to KDK model objects

    def normalize_chromosome(self,chrom: str) -> str:
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

    
    def parse(self, raw_json: Dict[str, Any]) -> KDKSchema:
        # parse raw JSON into KDK schema object
        case_data = raw_json.get("case", {})
        meta_data = raw_json.get("metaData", {})
        plan_data = raw_json.get("plan", {})
        molecular_data = raw_json.get("molecular", {})
        
        meta = self._parse_metadata(meta_data)
        # create patient from metadata
        patient = self._parse_patient(meta_data)
        
        # parse diagnoses from case data
        diagnoses = self._parse_diagnoses(case_data)
        
        # parse HPO terms from case data
        hpo_terms = self._parse_hpo_terms(case_data)
        
        # parse care plans from plan data
        care_plans = self._parse_care_plans(plan_data, meta_data)
        
        # parse episodes of care
        episodes = self._parse_episodes_of_care(case_data)
        
        insurance = self._parse_insurance(meta_data)

        # parse NGS reports
        ngs_reports = self._parse_ngs_reports(patient.id,case_data, molecular_data)
        
        return KDKSchema(
            patient=patient,
            diagnoses=diagnoses,
            hpoTerms=hpo_terms,
            carePlans=care_plans,
            episodesOfCare=episodes,
            ngsReports=ngs_reports,
            recordedOn=datetime.now().strftime("%Y-%m-%d"),
            healthInsurance=insurance,
            lastUpdate=datetime.now().strftime("%Y-%m-%d"),
            metaData=meta
        )
    
    def _parse_metadata(self, metadata: Dict[str, Any]) -> Metadata:

        submission_type = metadata.get("submission", "").get("type", "")
        transfer_tan = metadata.get("tanC", "")
        insurance = self._parse_insurance(metadata)
        project_consent_meta = metadata.get("mvConsent", False)
        provisions = []

        purpose_mapping = {
            "mvSequencing": "sequencing",
            "reIdentification": "reidentification",
            "caseIdentification": "case-identification"
        }

        # {sequencing, case-identification, reidentification}
        for scope in project_consent_meta.get("scope", []):
            # policy = Consent(
            #     presentedOn=scope.get("date", ""),
            #     consented=scope.get("type", ""),
            #     lastUpdate=scope.get("date", ""),
            #     version=project_consent_meta.get("version", "")
            # )
            provision = Provision(
                purpose=purpose_mapping.get(scope.get("domain", ""), "sequencing"),
                date=scope.get("date", ""),
                type=scope.get("type", "")
            )
            provisions.append(provision)

        consent = Consent(
            date=project_consent_meta.get("presentationDate", ""),
            version=project_consent_meta.get("version", ""),
            provisions=provisions
        )
        research_consent = metadata.get("researchConsents", [])


        """Parse metadata information."""
        return Metadata(
            type=submission_type,
            transferTAN=transfer_tan,
            healthInsuranceType=insurance,
            modelProjectConsent=consent,
            researchConsent=research_consent
        )


    def _parse_patient(self, meta_data: Dict[str, Any]) -> Patient:
        """Parse patient information from metadata."""
        # Parse gender
        gender_code = meta_data.get("gender", "unknown")
        gender_display = {
            "male": "Männlich", 
            "female": "Weiblich", 
            "other": "Sonstiges"
        }.get(gender_code, "Unbekannt")
        
        gender = Gender(code=gender_code, display=gender_display)
        
        # Parse birth date and calculate age
        birth_date = meta_data.get("birthDate", "")
        if birth_date and len(birth_date) == 7:  # Format: YYYY-MM
            birth_date = birth_date + "-15"  # Append 15th day of the month
        
        age = None
        if birth_date:
            try:
                birth_datetime = datetime.strptime(birth_date, "%Y-%m-%d")
                today = datetime.now()
                age_years = today.year - birth_datetime.year - (
                    (today.month, today.day) < (birth_datetime.month, birth_datetime.day)
                )
                age = Age(value=age_years, unit="years")
            except ValueError:
                pass
        
        # Parse vital status
        vital_status = VitalStatus(code="alive", display="Lebend")
        
        # Extract patient ID from reference if available
        # patient_id = "example-patient-001"  # Default
        municipality_code = meta_data.get("addressAGS", "")
        
        patient_id = str(uuid.uuid4())
        research_consents = meta_data.get("researchConsents", [])
        if research_consents:
            try:
                patient_ref = research_consents[0].get("scope", {}).get("scope", {}).get("patient", {})
            except Exception:
                patient_ref = None
            if patient_ref and patient_ref.get("reference"):
                patient_id = patient_ref["reference"].split("/")[-1]
        
        return Patient(
            id=patient_id,
            gender=gender,
            birthDate=birth_date,
            municipalityCode=municipality_code,
            age=age,
            vitalStatus=vital_status
        )
    
    def _parse_diagnoses(self, case_data: Dict[str, Any]) -> List[Diagnosis]:
        """Parse diagnosis information from case data."""
        diagnoses = []
        diagnosis_rd = case_data.get("diagnosisRd", {})
        diagnosis_list = []
            


        # Parse main diagnosis
        main_diag = diagnosis_rd.get("mainDiagnosis", {}) or diagnosis_rd.get("diagnoses", {})
        
        if type(main_diag) is list and main_diag:
            for diag in main_diag:
                diagnosis = self._map_dict_to_rd_diagnosis(diag, diagnosis_rd)
                diagnosis_list.append(diagnosis)
            
            diagnosis = self._create_diagnosis_from_dict(diagnosis_list, diagnosis_rd)



        return diagnosis
    
    def _parse_insurance(self, metadata: Dict[str, Any]) -> HealthInsurance:
        """Parse diagnosis information from case data."""
        insurance = None

        insurance_type= {
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
        insurance_code = "UNK"

        insurance_code = metadata.get("coverageType", {})
        if insurance_code:
            insurance = HealthInsurance(Coding(
                code=insurance_code,
                display=insurance_type.get(insurance_code, "Unbekannt"))
            )            




        return insurance

    def _map_dict_to_rd_diagnosis(self, diag_dict: Dict[str, Any], diagnosis_rd: Dict[str, Any]) -> Diagnosis:
        """Map a dictionary representation of a diagnosis to a Diagnosis object."""
        mapped_diag = None

        if "ICD-10" in diag_dict.get("system", "").upper():
            mapped_diag = ICD10GM(
                code=diag_dict.get("code", ""),
                version=diag_dict.get("version", ""),
                display=diag_dict.get("display", "")
            )
        elif "ORPHA" in diag_dict.get("system", "").upper():
            mapped_diag = Orphanet(
                code=diag_dict.get("code", ""),
                version=diag_dict.get("version", ""),
                display=diag_dict.get("display", "")
            )
        elif "ALPHA" in diag_dict.get("system", "").upper():
            mapped_diag = AlphaIdSE(
                code=diag_dict.get("code", ""),
                version=diag_dict.get("version", ""),
                display=diag_dict.get("display", "")
            )

        return mapped_diag

    
    def _create_diagnosis_from_dict(self, diag_list: List[Dict[str, Any]], diagnosis_rd: Dict[str, Any]) -> Diagnosis:
        """Create a diagnosis object from dictionary data."""
        
        # Parse verification status
        germline_confirmed = diagnosis_rd.get("germlineDiagnosisConfirmed", False)
        verification_status = VerificationStatus(
            code="confirmed" if germline_confirmed else "provisional",
            display="Bestätigt" if germline_confirmed else "Verdachtsdiagnose"
        )
        
        # Parse family control level (default to duo-genome)
        family_control = FamilyControlLevel(
            code="",
            display=""
        )

        diagnostic_extent = diagnosis_rd.get("diagnosticExtent", "no-record")

        fc_matching = { 
            "singleGenome": "single-genome",
            "duoGenome": "duo-genome",
            "trioGenome": "trio-genome"
        }

        fc_level = fc_matching.get(diagnostic_extent, "no-record")

        family_control_mapping = {
            "single-genome": "Single-Genome",
            "duo-genome": "Duo-Genome", 
            "trio-genome": "Trio-Genome",
            "no-record": "Keine Angabe"
        }
        
        family_control = FamilyControlLevel(
            code=fc_level,
            display=family_control_mapping.get(fc_level, "no-record")
        )

        
        return Diagnosis(
            codings=diag_list,
            verificationStatus=verification_status,
            familyControlLevel=family_control,
            onsetDate=diagnosis_rd.get("symptomOnsetDate", ""),
            recordedOn=datetime.now().strftime("%Y-%m-%d")
        )
    
    def _parse_hpo_terms(self, case_data: Dict[str, Any]) -> List[HPOTerm]:
        """Parse HPO terms from case data."""
        hpo_terms = []
        diagnosis_rd = case_data.get("diagnosisRd", {})
        
        hpo_list = diagnosis_rd.get("phenotypes", [])
        if type(hpo_list) is list and hpo_list:
            for hpo_dict in hpo_list:
                hpo = HPO(
                    code=hpo_dict.get("code", ""),
                    version=hpo_dict.get("version", ""),
                    display=hpo_dict.get("text", "")
                )
                hpo_term = HPOTerm(
                    value=hpo,
                    recordedOn=datetime.now().strftime("%Y-%m-%d"),
                    onsetDate=datetime.now().strftime("%Y-%m")
                )    
                hpo_terms.append(hpo_term)
        
        return hpo_terms
    
    def _parse_care_plans(self, plan_data: Dict[str, Any], meta_data: Dict[str, Any]) -> List[CarePlan]:
        """Parse care plans from plan data."""
        care_plans = []
        care_plan_rd = plan_data.get("carePlanRd", {})
        
        if care_plan_rd:
            # Parse therapy recommendations from preventive measures
            therapy_recommendations = []
            preventive_measures = plan_data.get("preventiveMeasures", [])
            
            for measure in preventive_measures:
                if measure.get("type") in ["genetic_counseling", "developmental_therapy"]:
                    therapy_rec = TherapyRecommendation(
                        category=TherapyCategory(code="symptomatic", display="Symptomatisch"),
                        type=TherapyType(code="other", display="Andere"),
                        issuedOn=meta_data.get("molecularBoardDecisionDate", datetime.now().strftime("%Y-%m-%d"))
                    )
                    therapy_recommendations.append(therapy_rec)
            
            # Parse genetic counseling recommendation
            genetic_counseling = None
            if care_plan_rd.get("counsellingRecommended"):
                genetic_counseling = GeneticCounselingRecommendation(
                    reason="Genetic disorder diagnosis",
                    issuedOn=care_plan_rd.get("molecularBoardDecisionDate", datetime.now().strftime("%Y-%m-%d"))
                )
            
            care_plan = CarePlan(
                issuedOn=care_plan_rd.get("molecularBoardDecisionDate", datetime.now().strftime("%Y-%m-%d")),
                therapyRecommendations=therapy_recommendations,
                geneticCounselingRecommendation=genetic_counseling,
                reevaluationRecommended=care_plan_rd.get("reEvaluationRecommended", False)
            )
            care_plans.append(care_plan)
        
        return care_plans
    
    def _parse_episodes_of_care(self, case_data: Dict[str, Any]) -> List[EpisodeOfCare]:
        """Parse episodes of care from metadata."""
        episodes = []
        # submission = meta_data.get("submission", {})
        submission = case_data.get("priorRds", {})
        
        if submission:
            for s in submission:
                episode = EpisodeOfCare(
                    period={"start": s["zseContactDate"] + "-15"},
                    status="active"
                )
            episodes.append(episode)
        
        return episodes

    def _parse_ngs_reports(self, patient_id: str, case_data: Dict[str, Any], molecular_data: Dict[str, Any]) -> List[NGSReport]:
        """Parse NGS reports from case data."""
        ngs_reports = []
        diagnosis_rd = case_data.get("diagnosisRd", {})
        
        # Parse sequencing information
        library_type = diagnosis_rd.get("libraryType", "wgs")
        sequencing = Sequencing(
            type=library_type,
            platform=Coding(
                code="illu" if library_type in ["wgs", "wes", "panel"] else "other",
                display="Illumina" if library_type in ["wgs", "wes", "panel"] else "Other",
                system="dnpm-dip/ngs/platform"
            ),  
            kit="Kit..."         # Not provided in sample data
        )
        
        # For now, create empty variants list since no variant data in sample
        variant_list = []
        small_variant_list = []
        cn_variant_list = []
        sv_variant_list = []

        amgc_class_map = {
            "1": "Benign",
            "2": "Likely benign",
            "3": "Uncertain significance",
            "4": "Likely pathogenic",
            "5": "Pathogenic",
        }

        significance_map = {
            "primary": "Variant in context of patient's disease",
            "incidental": "Incidental finding",
            "candidate": "Candidate variant"
        }


        acmg_criteria_mapping = {
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


        acmg_modifier_mapping = {
            # Pathogenic evidence adjustments
            "VeryStrong": "Pathogenic Very Strong",
            "Strong": "Pathogenic Strong",
            "Moderate": "Pathogenic Moderate",
            "Supporting": "Pathogenic Supporting",

            # Benign evidence adjustments
            "Standalone": "Benign Standalone",
            "StrongBenign": "Benign Strong",   # some labs write "StrongBenign" to disambiguate
            "SupportingBenign": "Benign Supporting",

            # General adjustment modifiers (direction-independent)
            "Upgraded": "Strength Increased",
            "Downgraded": "Strength Decreased",
            "NotMet": "Criterion Not Met",
        }

        zygosity_map = {
            "heterozygous": "Heterozygous",
            "homozygous": "Homozygous",
            "comp-het": "Compound heterozygous",
            "hemi": "Hemizygous",
            "homoplasmic": "Homoplasmic",
            "heteroplasmic": "Heteroplasmic",
        }

        segregation_analysis_normp = {
            "notPerformed":"not-performed",
            "deNovo": "de-novo",
            "fromFather": "from-father",
            "fromMother": "from-mother",
            "fromMotherAndFather": "from-both-parents",
        }

        segregation_analysis_map = {
            "not-performed": "Not performed",
            "de-novo": "De novo",
            "from-father": "Transmitted from father",
            "from-mother": "Transmitted from mother",
            "from-both-parents": "Transmitted from father and mother",
        }

        inheritance_map = {
            "dominant": "Dominant",
            "recessive": "Recessive",
            "X-linked": "X-linked",
            "mitochondrial": "Mitochondrial",
            "unclear": "Unclear"
        }

        cnv_type_map = {
            "gain": "Gain",
            "loss": "Loss"
        }

        variants = molecular_data.get("smallVariants", [])
        for variant in variants:
            criterion = variant.get("acmgCriteria", [])
            small_variant = SmallVariant(
                id=str(uuid.uuid4()),
                patient=Reference(id=patient_id, type="Patient"),
                chromosome=self.normalize_chromosome(variant.get("chromosome", None)),
                startPosition=variant.get("startPosition", None),
                endPosition=variant.get("endPosition", None),
                ref=variant.get("ref", ""),
                alt=variant.get("alt", ""),
                gDNAChange=variant.get("gdnaChange", None),
                cDNAChange=variant.get("cdnaChange", None),
                proteinChange=variant.get("proteinChange", None),
                acmgClass=Coding(
                    code=variant.get("acmgClass", "3"),
                    display=amgc_class_map.get(variant.get("acmgClass", "3"), "Uncertain significance"),
                    system="https://www.acmg.net/class"
                ),
                acmgCriteria=[
                    ACMGCriterion(
                        value=Coding(
                            code=c.get("value", ""),
                            display=acmg_criteria_mapping.get(c.get("value", ""), ""),
                            system=c.get("https://www.acmg.net/criteria/type", "")
                        ),
                        modifier=Coding(
                            code=c.get("modifier", ""),
                            display=acmg_modifier_mapping.get(c.get("modifier", ""), ""),
                            system="https://www.acmg.net/criteria/modifier"
                        )
                    ) for c in criterion
                ],
                zygosity=Coding(
                    code=variant.get("zygosity", "").lower(),
                    display=zygosity_map.get(variant.get("zygosity", "").lower(), ""),
                    system="dnpm-dip/rd/variant/zygosity"
                ),
                segregationAnalysis=Coding(
                    code=segregation_analysis_normp.get(variant.get("segregationAnalysis", ""), ""),
                    display=segregation_analysis_map.get(segregation_analysis_normp.get(variant.get("segregationAnalysis", ""), ""), ""),
                    system="ddnpm-dip/rd/variant/segregation-analysis"
                ),
                modeOfInheritance=Coding(
                    code=variant.get("modeOfInheritance", ""),
                    display=inheritance_map.get(variant.get("modeOfInheritance", ""), ""),
                    system="dnpm-dip/rd/variant/mode-of-inheritance"
                ),
                significance=Coding(
                    code=variant.get("diagnosticSignificance", ""),
                    display=significance_map.get(variant.get("diagnosticSignificance", ""), ""),
                    system="dnpm-dip/rd/variant/significance"
                ),
                clinVarID=variant.get("clinVarID", None),
                pubMedIDs=variant.get("publications", [])
            )
            small_variant_list.append(small_variant)

        ### For copy number variants
        variants = molecular_data.get("copyNumberVariants", [])
        for variant in variants:
            copy_number_variant = CopyNumberVariant(
                id=str(uuid.uuid4()),
                patient=Reference(id=patient_id, type="Patient"),
                chromosome=self.normalize_chromosome(variant.get("chromosome", None)),
                startPosition=variant.get("startPosition", None),
                endPosition=variant.get("endPosition", None),
                type=Coding(
                    code=variant.get("cnvType", ""),
                    display=cnv_type_map.get(variant.get("cnvType", ""), ""),
                    system="dnpm-dip/rd/variant/cnv-type"
                ),
                gDNAChange=variant.get("gdnaChange", None),
                cDNAChange=variant.get("cdnaChange", None),
                proteinChange=variant.get("proteinChange", None),
                acmgClass=Coding(
                    code=variant.get("acmgClass", "3"),
                    display=amgc_class_map.get(variant.get("acmgClass", "3"), "Uncertain significance"),
                    system="https://www.acmg.net/class"
                ),
                acmgCriteria=[
                    ACMGCriterion(
                        value=Coding(
                            code=c.get("value", ""),
                            display=acmg_criteria_mapping.get(c.get("value", ""), ""),
                            system=c.get("https://www.acmg.net/criteria/type", "")
                        ),
                        modifier=Coding(
                            code=c.get("modifier", ""),
                            display=acmg_modifier_mapping.get(c.get("modifier", ""), ""),
                            system="https://www.acmg.net/criteria/modifier"
                        )
                    ) for c in variant.get("acmgCriteria", [])
                ],
                zygosity=Coding(
                    code=variant.get("zygosity", "").lower(),
                    display=zygosity_map.get(variant.get("zygosity", "").lower(), ""),
                    system="dnpm-dip/rd/variant/zygosity"
                ),
                segregationAnalysis=Coding(
                    code=segregation_analysis_normp.get(variant.get("segregationAnalysis", ""), ""),
                    display=segregation_analysis_map.get(segregation_analysis_normp.get(variant.get("segregationAnalysis", ""), ""), ""),
                    system="ddnpm-dip/rd/variant/segregation-analysis"
                ),
                modeOfInheritance=Coding(
                    code=variant.get("modeOfInheritance", ""),
                    display=inheritance_map.get(variant.get("modeOfInheritance", ""), ""),
                    system="dnpm-dip/rd/variant/mode-of-inheritance"
                ),
                significance=Coding(
                    code=variant.get("diagnosticSignificance", ""),
                    display=significance_map.get(variant.get("diagnosticSignificance", ""), ""),
                    system="dnpm-dip/rd/variant/significance"
                ),
                clinVarID=variant.get("clinVarID", None),
                pubMedIDs=variant.get("publications", [])
            )
            cn_variant_list.append(copy_number_variant)

        ### For structural variants
        variants = molecular_data.get("structuralVariants", [])
        for variant in variants:
            structural_variant = StructuralVariant(
                id=str(uuid.uuid4()),
                patient=Reference(id=patient_id, type="Patient"),
                iscnDescription=Coding(
                    code=variant.get("iscnDescription", "ISCN Description ..."),
                    display=variant.get("iscnDescription", "ISCN Description ..."),
                    system="dnpm-dip/rd/variant/iscn-description"),
                gDNAChange=variant.get("gdnaChange", None),
                cDNAChange=variant.get("cdnaChange", None),
                proteinChange=variant.get("proteinChange", None),
                acmgClass=Coding(
                    code=variant.get("acmgClass", "3"),
                    display=amgc_class_map.get(variant.get("acmgClass", "3"), "Uncertain significance"),
                    system="https://www.acmg.net/class"
                ),
                acmgCriteria=[
                    ACMGCriterion(
                        value=Coding(
                            code=c.get("value", ""),
                            display=acmg_criteria_mapping.get(c.get("value", ""), ""),
                            system=c.get("https://www.acmg.net/criteria/type", "")
                        ),
                        modifier=Coding(
                            code=c.get("modifier", ""),
                            display=acmg_modifier_mapping.get(c.get("modifier", ""), ""),
                            system="https://www.acmg.net/criteria/modifier"
                        )
                    ) for c in variant.get("acmgCriteria", [])
                ],
                zygosity=Coding(
                    code=variant.get("zygosity", "").lower(),
                    display=zygosity_map.get(variant.get("zygosity", "").lower(), ""),
                    system="dnpm-dip/rd/variant/zygosity"
                ),
                segregationAnalysis=Coding(
                    code=segregation_analysis_normp.get(variant.get("segregationAnalysis", ""), ""),
                    display=segregation_analysis_map.get(segregation_analysis_normp.get(variant.get("segregationAnalysis", ""), ""), ""),
                    system="ddnpm-dip/rd/variant/segregation-analysis"
                ),
                modeOfInheritance=Coding(
                    code=variant.get("modeOfInheritance", ""),
                    display=inheritance_map.get(variant.get("modeOfInheritance", ""), ""),
                    system="dnpm-dip/rd/variant/mode-of-inheritance"
                ),
                significance=Coding(
                    code=variant.get("diagnosticSignificance", ""),
                    display=significance_map.get(variant.get("diagnosticSignificance", ""), ""),
                    system="dnpm-dip/rd/variant/significance"
                ),
                clinVarID=variant.get("clinVarID", None),
                pubMedIDs=variant.get("publications", [])
            )
            sv_variant_list.append(copy_number_variant)

        
        # Get issue date from submission
        # issued_on = meta_data.get("submission", {}).get("date", datetime.now().strftime("%Y-%m-%d"))
        issued_on = case_data.get("molecularBoardDecisionDate", datetime.now().strftime("%Y-%m-%d"))

        genomic_test_map = {
            "wgs": "genome-short-read",
            "wgs_lr": "genome-long-read"
        }
        genomic_display_map = {
            "panel": "Panel",
            "exome": "Exome", 
            "genome-short-read": "Genome short-read",
            "genome-long-read": "Genome long-read",
            "single": "Single",
            "karyotyping": "Karyotyping",
            "array": "Array",
            "other": "Other"
        }
        variants = {"smallVariants": small_variant_list, "copyNumberVariants": cn_variant_list, "structuralVariants": sv_variant_list}
        genomic_test_type = genomic_test_map.get(diagnosis_rd.get("libraryType", "wgs").lower(), "other")
        ngs_report = NGSReport(
                sequencing=sequencing,
                variants=variants,
                issuedOn=issued_on,
                type=Coding(
                    code=genomic_test_type,
                    display=genomic_display_map.get(genomic_test_type, "Other"),
                    system="dnpm-dip/ngs/type"
                )
            )

        ngs_reports.append(ngs_report)
        
        
        return ngs_reports
    
    def parse_from_file(self, file_path: str) -> KDKSchema:
        """Parse KDK JSON file into KDK schema object."""
        import json

        
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_json = json.load(f)
        
        return self.parse(raw_json)

