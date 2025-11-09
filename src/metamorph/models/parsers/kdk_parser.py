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
from .mappings import Mappings, MappingHelper
from ...utils.ordolib import ORDOMapper

class KDKParser:
    # parser to convert raw KDK JSON to KDK model objects

    # def __init__(self):
    #     self.mapper = ORDOMapper()
    
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



        # Parse model project consent provisions
        for scope in project_consent_meta.get("scope", []):
            provision = Provision(
                purpose=MappingHelper.get_purpose_code(scope.get("domain", "")),
                date=scope.get("date", ""),
                type=scope.get("type", "")
            )

           
            provisions.append(provision)

        consent = Consent(
            date=project_consent_meta.get("presentationDate", ""),
            version=project_consent_meta.get("version", ""),
            provisions=provisions
        )
        
        # Parse research consents with noScopeJustification handling
        research_consents = metadata.get("researchConsents", [])
        research_consent_missing = None
        
        # Check for noScopeJustification in research consents
        for research_consent in research_consents:
            no_scope_justification = research_consent.get("noScopeJustification")
            if no_scope_justification:
                # If noScopeJustification exists, empty the research_consents list
                research_consents = []
                
                research_consent_missing = MappingHelper.get_research_consent_reason(no_scope_justification)['code']
                
                break  # Exit loop after finding the first noScopeJustification

        return Metadata(
            type=submission_type,
            transferTAN=transfer_tan,
            healthInsuranceType=insurance,
            modelProjectConsent=consent,
            researchConsents=research_consents,  # Empty list if noScopeJustification found
            reasonResearchConsentMissing=research_consent_missing  # Mapped reason or None
        )


    def _parse_patient(self, meta_data: Dict[str, Any]) -> Patient:
        
        # Parse gender
        gender_code = meta_data.get("gender", "unknown")
        gender_display = MappingHelper.get_gender_display(gender_code)
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
        
        # Parse vital status - FOR REVIEW
        vital_status = VitalStatus(code="alive", display="Lebend")
        
        # Extract patient ID from reference if available??? - now am generating UUID
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
                # if diagnosis:
                #     diagnoses.append(diagnosis)
                diagnosis_list.append(diagnosis)
            
            diagnosis = self._create_diagnosis_from_dict(diagnosis_list, diagnosis_rd)


        return diagnosis
    
    def _parse_insurance(self, metadata: Dict[str, Any]) -> HealthInsurance:
        """Parse diagnosis information from case data."""

        insurance_code = "UNK"

        insurance_code = metadata.get("coverageType", {})
        if insurance_code:
            insurance = HealthInsurance(Coding(
                code=insurance_code,
                display=MappingHelper.get_insurance_display(insurance_code)
                )
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
                # code=f"ORPHA:{diag_dict.get('code', '')}",
                code=diag_dict.get('code', ''),
                version=diag_dict.get("version", ""),
                display=diag_dict.get("display", "")
            )
        elif "ALPHA" in diag_dict.get("system", "").upper():
            mapped_diag = AlphaIdSE(
                code=diag_dict.get("code", ""),
                version=diag_dict.get("version", ""),
                display=diag_dict.get("display", "")
            )

        
        # if isinstance(mapped_diag,Orphanet):
        #     # Ensure ORPHA code is in 'ORPHA:NNNN' format
        #     if not mapped_diag.code.startswith("ORPHA:"):
        #         mapped_diag.code = f"ORPHA:{mapped_diag.code}"
        #     is_present = self.mapper.present_in_both(mapped_diag.code)
        #     omims = self.mapper.get_omim_from_orpha(mapped_diag.code)
        #     if not is_present:
        #         mapped_diag = None
        

        return mapped_diag

    
    def _create_diagnosis_from_dict(self, diag_list: List[Dict[str, Any]], diagnosis_rd: Dict[str, Any]) -> Diagnosis:
        """Create a diagnosis object from dictionary data."""
        
        # Parse verification status
        germline_confirmed = diagnosis_rd.get("germlineDiagnosisConfirmed", False)
        
        ## FOR REVIEW: Adjust mapping as needed - VERIFICATION STATUS
        verification_status = VerificationStatus(
            code="confirmed" if germline_confirmed else "provisional",
            display=MappingHelper.get_verification_display(germline_confirmed)
        )
        
        # Parse family control level (default to duo-genome)
        family_control = FamilyControlLevel(
            code="",
            display=""
        )

        diagnostic_extent = diagnosis_rd.get("diagnosticExtent", "no-record")

        #family_control_values = MappingHelper.get_family_control(diagnostic_extent)
        
        family_control = FamilyControlLevel(
            **(sa:=MappingHelper.get_family_control(diagnostic_extent))
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
            

            ### FOR REVIEW: Adjust mapping as needed - THERAPY RECOMMENDATIONS
            for measure in preventive_measures:
                if measure.get("type") in ["genetic_counseling", "developmental_therapy"]:
                    therapy_rec = TherapyRecommendation(
                        category=TherapyCategory(code="symptomatic", display="Symptomatisch"),
                        type=TherapyType(code="other", display="Andere"),
                        issuedOn=meta_data.get("molecularBoardDecisionDate", datetime.now().strftime("%Y-%m-%d"))
                    )
                    therapy_recommendations.append(therapy_rec)
            
            ### FOR REVIEW: Adjust mapping as needed - GENETIC COUNSELING RECOMMENDATION
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

        
        if type(molecular_data) is not dict:
            molecular_data = {}
        variants = molecular_data.get("smallVariants", [])
        for variant in variants:
            criterion = variant.get("acmgCriteria", [])
            small_variant = SmallVariant(
                id=str(uuid.uuid4()),
                patient=Reference(id=patient_id, type="Patient"),
                chromosome=MappingHelper.normalize_chromosome(variant.get("chromosome", None)),
                startPosition=variant.get("startPosition", None),
                endPosition=variant.get("endPosition", None),
                ref=variant.get("ref", ""),
                alt=variant.get("alt", ""),
                gDNAChange=variant.get("gdnaChange", None),
                cDNAChange=variant.get("cdnaChange", None),
                proteinChange=variant.get("proteinChange", None),
                acmgClass=Coding(
                    code=variant.get("acmgClass", "3"),
                    display=MappingHelper.get_acmg_class_display(variant.get("acmgClass", "3")),
                    system="https://www.acmg.net/class"
                ),
                acmgCriteria=[
                    ACMGCriterion(
                        value=Coding(
                            code=c.get("value", ""),
                            display=MappingHelper.get_acmg_criteria_display(c.get("value", "")),
                            system=c.get("https://www.acmg.net/criteria/type", "")
                        ),
                        modifier=Coding(
                            code=MappingHelper.get_acmg_criteria_modifier(c.get("value", "")),
                            display=MappingHelper.get_acmg_modifier_display(MappingHelper.get_acmg_criteria_modifier(c.get("value", ""))),
                            system="https://www.acmg.net/criteria/modifier"
                        )
                    ) for c in criterion
                ],
                zygosity=Coding(
                    **(sa:=MappingHelper.get_zygosity(variant.get("zygosity", "").lower())),
                    # code=variant.get("zygosity", "").lower(),
                    # display=MappingHelper.get_zygosity(variant.get("zygosity", "").lower()),
                    system="dnpm-dip/rd/variant/zygosity"
                ),
                segregationAnalysis = Coding(
                    **(sa := MappingHelper.get_segregation_analysis(variant.get("segregationAnalysis", ""))),
                    system="ddnpm-dip/rd/variant/segregation-analysis"
                ),
                modeOfInheritance=Coding(
                    **(sa:=MappingHelper.get_inheritance(variant.get("modeOfInheritance", "unclear"))),
                    # code=inheritance_normalization.get(variant.get("modeOfInheritance", ""), "unclear"),
                    # display=inheritance_map.get(inheritance_normalization.get(variant.get("modeOfInheritance", ""), "unclear"), "Unclear"),
                    system="dnpm-dip/rd/variant/mode-of-inheritance"
                ),
                significance=Coding(
                    code=variant.get("diagnosticSignificance", ""),
                    display=MappingHelper.get_significance_display(variant.get("diagnosticSignificance", "")),
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
                    display=MappingHelper.get_cnv_type_display(variant.get("cnvType", "")),
                    system="dnpm-dip/rd/variant/cnv-type"
                ),
                gDNAChange=variant.get("gdnaChange", None),
                cDNAChange=variant.get("cdnaChange", None),
                proteinChange=variant.get("proteinChange", None),
                acmgClass=Coding(
                    code=variant.get("acmgClass", "3"),
                    display=MappingHelper.get_acmg_class_display(variant.get("acmgClass", "3")),
                    system="https://www.acmg.net/class"
                ),
                acmgCriteria=[
                    ACMGCriterion(
                        value=Coding(
                            code=c.get("value", ""),
                            display=MappingHelper.get_acmg_criteria_display(c.get("value", "")),
                            system=c.get("https://www.acmg.net/criteria/type", "")
                        ),
                        modifier=Coding(
                            code=c.get("modifier", ""),
                            display=MappingHelper.get_acmg_modifier_display(c.get("modifier", "")),
                            system="https://www.acmg.net/criteria/modifier"
                        )
                    ) for c in variant.get("acmgCriteria", [])
                ],
                zygosity=Coding(
                    code=variant.get("zygosity", "").lower(),
                    display=MappingHelper.get_zygosity(variant.get("zygosity", "").lower()),
                    system="dnpm-dip/rd/variant/zygosity"
                ),
                segregationAnalysis = Coding(
                    **(sa := MappingHelper.get_segregation_analysis(variant.get("segregationAnalysis", ""))),
                    system="ddnpm-dip/rd/variant/segregation-analysis"
                ),
                modeOfInheritance=Coding(
                    **(sa:=MappingHelper.get_inheritance(variant.get("modeOfInheritance", "unclear"))),
                    # code=inheritance_normalization.get(variant.get("modeOfInheritance", ""), "unclear"),
                    # display=inheritance_map.get(inheritance_normalization.get(variant.get("modeOfInheritance", ""), "unclear"), "Unclear"),
                    system="dnpm-dip/rd/variant/mode-of-inheritance"
                ),
                significance=Coding(
                    code=variant.get("diagnosticSignificance", ""),
                    display=MappingHelper.get_significance_display(variant.get("diagnosticSignificance", "")),
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
                    display=MappingHelper.get_acmg_class_display(variant.get("acmgClass", "3")),
                    system="https://www.acmg.net/class"
                ),
                acmgCriteria=[
                    ACMGCriterion(
                        value=Coding(
                            code=c.get("value", ""),
                            display=MappingHelper.get_acmg_criteria_display(c.get("value", "")),
                            system=c.get("https://www.acmg.net/criteria/type", "")
                        ),
                        modifier=Coding(
                            code=c.get("modifier", ""),
                            display=MappingHelper.get_acmg_modifier_display(c.get("modifier", "")),
                            system="https://www.acmg.net/criteria/modifier"
                        )
                    ) for c in variant.get("acmgCriteria", [])
                ],
                zygosity=Coding(
                    code=variant.get("zygosity", "").lower(),
                    display=MappingHelper.get_zygosity(variant.get("zygosity", "").lower()),
                    system="dnpm-dip/rd/variant/zygosity"
                ),
                segregationAnalysis = Coding(
                    **(sa := MappingHelper.get_segregation_analysis(variant.get("segregationAnalysis", ""))),
                    system="ddnpm-dip/rd/variant/segregation-analysis"
                ),
                modeOfInheritance=Coding(
                    **(sa:=MappingHelper.get_inheritance(variant.get("modeOfInheritance", "unclear"))),
                    # code=inheritance_normalization.get(variant.get("modeOfInheritance", ""), "unclear"),
                    # display=inheritance_map.get(inheritance_normalization.get(variant.get("modeOfInheritance", ""), "unclear"), "Unclear"),
                    system="dnpm-dip/rd/variant/mode-of-inheritance"
                ),
                significance=Coding(
                    code=variant.get("diagnosticSignificance", ""),
                    display=MappingHelper.get_significance_display(variant.get("diagnosticSignificance", "")),
                    system="dnpm-dip/rd/variant/significance"
                ),
                clinVarID=variant.get("clinVarID", None),
                pubMedIDs=variant.get("publications", [])
            )
            sv_variant_list.append(copy_number_variant)

        
        # Get issue date from submission
        # issued_on = meta_data.get("submission", {}).get("date", datetime.now().strftime("%Y-%m-%d"))
        issued_on = case_data.get("molecularBoardDecisionDate", datetime.now().strftime("%Y-%m-%d"))

    
        variants = {"smallVariants": small_variant_list, "copyNumberVariants": cn_variant_list, "structuralVariants": sv_variant_list}
        genomic_test_type = MappingHelper.get_genomic_test_type(diagnosis_rd.get("libraryType", "wgs").lower())
        ngs_report = NGSReport(
                sequencing=sequencing,
                variants=variants,
                issuedOn=issued_on,
                type=Coding(
                    **(sa:=MappingHelper.get_genomic_test(genomic_test_type)),
                    # code=genomic_test_type,
                    # display=MappingHelper.get_genomic_test(genomic_test_type),
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

