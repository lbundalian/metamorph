import uuid
from datetime import datetime
from typing import Dict, Any, List
from ..models.rd_model import RDSchema, Patient, Diagnosis, HPOTerm, CarePlan
from .base_morpher import BaseMorpher

class KDKMorpher(BaseMorpher):
   
    def __init__(self):
        self.generate_id = lambda: str(uuid.uuid4())

    def morph(self, source: Dict[str, Any]) -> Dict[str, Any]:
        patient_id = self.generate_id()
        
        # Create patient
        patient = Patient(
            id=patient_id,
            gender={
                "code": source["metaData"]["gender"],
                "display": "",
                "system": "Gender"
            },
            birthDate=source["metaData"]["birthDate"],
            address={
                "municipalityCode": source["metaData"]["addressAGS"]
            }
        )

        # Create schema
        schema = RDSchema(
            patient=patient,
            diagnoses=[self._create_diagnosis(source, patient_id)],
            hpoTerms=self._create_hpo_terms(source, patient_id),
            carePlans=[self._create_care_plan(source, patient_id)]
        )

        return schema.to_dict()

    def _create_diagnosis(self, source: Dict[str, Any], patient_id: str) -> Diagnosis:
        main_diagnosis = source["case"]["diagnosisOd"]["mainDiagnosis"]
        return Diagnosis(
            id=self.generate_id(),
            patient={"id": patient_id, "type": "Patient"},
            recordedOn=main_diagnosis.get("date", ""),
            codes=[main_diagnosis]
        )

    def _create_hpo_terms(self, source: Dict[str, Any], patient_id: str) -> List[HPOTerm]:
        return [
            HPOTerm(
                id=self.generate_id(),
                patient={"id": patient_id, "type": "Patient"},
                recordedOn=datetime.now().strftime("%Y-%m-%d"),
                value={"code": term["code"], "system": term["system"]}
            )
            for term in source["case"]["diagnosisOd"]["hpoTerms"]
        ]

    def _create_care_plan(self, source: Dict[str, Any], patient_id: str) -> CarePlan:
        care_plan_data = source["plan"]["carePlanOd"]
        return CarePlan(
            id=self.generate_id(),
            patient={"id": patient_id, "type": "Patient"},
            issuedOn=datetime.now().strftime("%Y-%m-%d"),
            geneticCounselingRecommended=care_plan_data.get("counsellingRecommended", False),
            reevaluationRecommended=care_plan_data.get("reEvaluationRecommended", False)
        )

    def validate(self, data: Dict[str, Any]) -> bool:
        required_keys = ["patient", "diagnoses", "hpoTerms", "carePlans"]
        return all(key in data for key in required_keys)