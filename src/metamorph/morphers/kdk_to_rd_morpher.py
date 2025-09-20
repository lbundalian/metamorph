import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..models.rd_model import RDSchema, Patient, Diagnosis, HPOTerm, CarePlan
from ..models.kdk_model import KDKSchema
from .base_morpher import BaseMorpher

class KDKToRDMorpher(BaseMorpher):
    """Morpher to transform KDK data format to RD data format."""
   
    def __init__(self):
        self.generate_id = lambda: str(uuid.uuid4())

    def morph(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Transform KDK format to RD format."""
        patient_id = self._get_patient_id(source) or self.generate_id()
        
        # Create patient from KDK metadata
        patient = self._create_patient(source, patient_id)
        
        # Create main components
        diagnoses = self._create_diagnoses(source, patient_id)
        hpo_terms = self._create_hpo_terms(source, patient_id)
        care_plans = self._create_care_plans(source, patient_id)
        
        # Create RD schema
        rd_schema = RDSchema(
            patient=patient,
            diagnoses=diagnoses,
            hpoTerms=hpo_terms,
            carePlans=care_plans
        )

        return rd_schema.to_dict()

    def _create_patient(self, source: Dict[str, Any], patient_id: str) -> Patient:
        """Create patient object from KDK metadata."""
        metadata = source.get("metaData", {})
        
        # Map gender
        gender_code = metadata.get("gender", "").lower()
        gender_display = self._map_gender_display(gender_code)
        
        return Patient(
            id=patient_id,
            gender={
                "code": gender_code,
                "display": gender_display,
                "system": "Gender"
            },
            birthDate=metadata.get("birthDate", ""),
            address={
                "municipalityCode": metadata.get("addressAGS", "")
            },
            # Add health insurance if available
            healthInsurance=self._create_health_insurance(metadata) if metadata.get("coverageType") else None,
            # Calculate age if birth date is available
            age=self._calculate_age(metadata.get("birthDate", "")) if metadata.get("birthDate") else None,
            vitalStatus={
                "code": "alive",
                "display": "Lebend", 
                "system": "dnpm-dip/patient/vital-status"
            }
        )

    def _create_diagnoses(self, source: Dict[str, Any], patient_id: str) -> List[Diagnosis]:
        """Create diagnosis objects from KDK case data."""
        diagnoses = []
        case_data = source.get("case", {}).get("diagnosisOd", {})
        
        # Main diagnosis
        main_diagnosis = case_data.get("mainDiagnosis", {})
        if main_diagnosis.get("code"):
            diagnosis = Diagnosis(
                id=self.generate_id(),
                patient={"id": patient_id, "type": "Patient"},
                recordedOn=main_diagnosis.get("date", datetime.now().strftime("%Y-%m-%d")),
                codes=[{
                    "code": main_diagnosis.get("code", ""),
                    "display": main_diagnosis.get("display", ""),
                    "system": main_diagnosis.get("system", ""),
                    "version": main_diagnosis.get("version", "")
                }],
                verificationStatus={
                    "code": "confirmed" if case_data.get("germlineDiagnosisConfirmed", False) else "provisional",
                    "display": "Bestätigt" if case_data.get("germlineDiagnosisConfirmed", False) else "Vorläufig",
                    "system": "dnpm-dip/rd/diagnosis/verification-status"
                }
            )
            diagnoses.append(diagnosis)
        
        # Additional diagnoses
        for additional_diag in case_data.get("additionalDiagnoses", []):
            if additional_diag.get("code"):
                diagnosis = Diagnosis(
                    id=self.generate_id(),
                    patient={"id": patient_id, "type": "Patient"},
                    recordedOn=additional_diag.get("date", datetime.now().strftime("%Y-%m-%d")),
                    codes=[{
                        "code": additional_diag.get("code", ""),
                        "display": additional_diag.get("display", ""),
                        "system": additional_diag.get("system", ""),
                        "version": additional_diag.get("version", "")
                    }]
                )
                diagnoses.append(diagnosis)
        
        return diagnoses

    def _create_hpo_terms(self, source: Dict[str, Any], patient_id: str) -> List[HPOTerm]:
        """Create HPO terms from KDK case data."""
        hpo_terms = []
        case_data = source.get("case", {}).get("diagnosisOd", {})
        
        for hpo_term_data in case_data.get("hpoTerms", []):
            if hpo_term_data.get("code"):
                hpo_term = HPOTerm(
                    id=self.generate_id(),
                    patient={"id": patient_id, "type": "Patient"},
                    recordedOn=datetime.now().strftime("%Y-%m-%d"),
                    value={
                        "code": hpo_term_data.get("code", ""),
                        "system": hpo_term_data.get("system", "https://hpo.jax.org")
                    },
                    status={
                        "history": [{
                            "status": {
                                "code": "unchanged",
                                "display": "Unverändert",
                                "system": "dnpm-dip/rd/hpo-term/status"
                            },
                            "date": datetime.now().strftime("%Y-%m-%d")
                        }]
                    }
                )
                hpo_terms.append(hpo_term)
        
        return hpo_terms

    def _create_care_plans(self, source: Dict[str, Any], patient_id: str) -> List[CarePlan]:
        """Create care plans from KDK plan data."""
        care_plans = []
        plan_data = source.get("plan", {}).get("carePlanOd", {})
        
        care_plan = CarePlan(
            id=self.generate_id(),
            patient={"id": patient_id, "type": "Patient"},
            issuedOn=plan_data.get("molecularBoardDecisionDate", datetime.now().strftime("%Y-%m-%d")),
            geneticCounselingRecommended=plan_data.get("counsellingRecommended", False),
            reevaluationRecommended=plan_data.get("reEvaluationRecommended", False),
            therapyRecommendations=self._create_therapy_recommendations(source, patient_id)
        )
        care_plans.append(care_plan)
        
        return care_plans

    def _create_therapy_recommendations(self, source: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create therapy recommendations from preventive measures."""
        therapy_recommendations = []
        preventive_measures = source.get("plan", {}).get("preventiveMeasures", [])
        
        for measure in preventive_measures:
            if measure.get("type"):
                therapy_rec = {
                    "id": self.generate_id(),
                    "patient": {"id": patient_id, "type": "Patient"},
                    "issuedOn": datetime.now().strftime("%Y-%m-%d"),
                    "category": {
                        "code": "preventive",
                        "display": "Präventiv",
                        "system": "dnpm-dip/rd/therapy/category"
                    },
                    "type": {
                        "code": "other",
                        "display": "Andere",
                        "system": "dnpm-dip/rd/therapy/type"
                    }
                }
                therapy_recommendations.append(therapy_rec)
        
        return therapy_recommendations

    def _create_health_insurance(self, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create health insurance info from metadata."""
        coverage_type = metadata.get("coverageType", "")
        if not coverage_type:
            return None
            
        return {
            "type": {
                "code": "GKV" if "gesetzlich" in coverage_type.lower() else "PKV",
                "display": "gesetzliche Krankenversicherung" if "gesetzlich" in coverage_type.lower() else "private Krankenversicherung",
                "system": "http://fhir.de/CodeSystem/versicherungsart-de-basis"
            },
            "reference": {
                "id": metadata.get("tanC", ""),
                "system": "https://www.dguv.de/arge-ik",
                "display": "Krankenversicherung",
                "type": "HealthInsurance"
            }
        }

    def _calculate_age(self, birth_date: str) -> Optional[Dict[str, Any]]:
        """Calculate age from birth date."""
        if not birth_date:
            return None
            
        try:
            from datetime import datetime
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.now()
            age_years = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            
            return {
                "value": age_years,
                "unit": "Years"
            }
        except:
            return None

    def _map_gender_display(self, gender_code: str) -> str:
        """Map gender code to display value."""
        gender_map = {
            "male": "Männlich",
            "female": "Weiblich", 
            "other": "Anderes",
            "unknown": "Unbekannt"
        }
        return gender_map.get(gender_code.lower(), "Unbekannt")
    
    # def _get_patient_id(self, source: Dict[str, Any]) -> str:
    #     """Get patient ID from research content reference in metadata."""
    #     metadata = source.get("metaData", {})
    #     patient = metadata.get("researchConsents")[0].get("scope").get("scope").get("patient").get("reference")
    #     return patient
    
    def _get_patient_id(self, source: Dict[str, Any]) -> Optional[str]:
        """Get patient ID from research content reference in metadata with safe navigation."""
        try:
            metadata = source.get("metaData", {})
            research_consents = metadata.get("researchConsents", [])
            
            if not research_consents:
                return None
                
            for consent in research_consents:
                scope = consent.get("scope", {})
                if isinstance(scope, dict):
                    inner_scope = scope.get("scope", {})
                    if isinstance(inner_scope, dict):
                        patient = inner_scope.get("patient", {})
                        if isinstance(patient, dict):
                            reference = patient.get("reference")
                            if reference:
                                # Extract ID from reference (e.g., "Patient/123" -> "123")
                                return reference.split("/")[-1] if "/" in reference else reference
            
            return None
        except (AttributeError, KeyError, IndexError, TypeError):
            return None

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate the transformed RD data."""
        required_fields = ["patient", "diagnoses", "hpoTerms", "carePlans"]
        
        # Check if all required top-level fields exist
        if not all(field in data for field in required_fields):
            return False
            
        # Validate patient has required fields
        patient = data.get("patient", {})
        if not all(field in patient for field in ["id", "gender", "birthDate"]):
            return False
            
        return True