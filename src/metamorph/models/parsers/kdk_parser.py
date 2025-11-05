# KDK JSON parser - creates KDK model objects from raw JSON
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
from ..kdk_model import (
    KDKSchema, Patient, Gender, VitalStatus, Age, Diagnosis, ICD10GM, 
    AlphaIdSE, Orphanet, VerificationStatus, FamilyControlLevel,
    HPOTerm, HPO, CarePlan, TherapyRecommendation, TherapyCategory, 
    TherapyType, StudyEnrollmentRecommendation, GeneticCounselingRecommendation,
    EpisodeOfCare, NGSReport, Sequencing, Variant, VariantType, 
    Significance, Zygosity, DiagnosisCategory
)

class KDKParser:
    # parser to convert raw KDK JSON to KDK model objects
    
    def parse(self, raw_json: Dict[str, Any]) -> KDKSchema:
        # parse raw JSON into KDK schema object
        case_data = raw_json.get("case", {})
        meta_data = raw_json.get("metaData", {})
        plan_data = raw_json.get("plan", {})
        
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
        
        # parse NGS reports
        ngs_reports = self._parse_ngs_reports(case_data, meta_data)
        
        return KDKSchema(
            patient=patient,
            diagnoses=diagnoses,
            hpoTerms=hpo_terms,
            carePlans=care_plans,
            episodesOfCare=episodes,
            ngsReports=ngs_reports,
            recordedOn=datetime.now().strftime("%Y-%m-%d"),
            lastUpdate=datetime.now().strftime("%Y-%m-%d")
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

        diagnostic_extent = diagnosis_rd.get("diagnosticExtent", "single-genome")

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
                    period={"start": s["zseContactDate"]},
                    status="active"
                )
            episodes.append(episode)
        
        return episodes
    
    def _parse_ngs_reports(self, case_data: Dict[str, Any], meta_data: Dict[str, Any]) -> List[NGSReport]:
        """Parse NGS reports from case data."""
        ngs_reports = []
        diagnosis_rd = case_data.get("diagnosisRd", {})
        
        # Parse sequencing information
        library_type = diagnosis_rd.get("libraryType", "WES")
        sequencing = Sequencing(
            type=library_type,
            platform="Unknown",  # Not provided in sample data
            kit="Unknown"         # Not provided in sample data
        )
        
        # For now, create empty variants list since no variant data in sample
        variants = []
        # variants = meta_data.get("molecular", []).get("variants", [])
        
        # Get issue date from submission
        issued_on = meta_data.get("submission", {}).get("date", datetime.now().strftime("%Y-%m-%d"))
        
        ngs_report = NGSReport(
            sequencing=sequencing,
            variants=variants,
            issuedOn=issued_on
        )
        ngs_reports.append(ngs_report)
        
        return ngs_reports
    
    def parse_from_file(self, file_path: str) -> KDKSchema:
        """Parse KDK JSON file into KDK schema object."""
        import json

        
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_json = json.load(f)
        
        return self.parse(raw_json)