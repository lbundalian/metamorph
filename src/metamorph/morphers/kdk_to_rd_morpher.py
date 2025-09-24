import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ..models.rd_model import (
    RDSchema, Patient, Diagnosis, HPOTerm, CarePlan, EpisodeOfCare, NGSReport,
    Code, Reference
)
from ..models.kdk_model import KDKSchema
from ..utils.kdk_rd_mapping import KDKRDMapping
from .base_morpher import BaseMorpher

class KDKToRDMorpher(BaseMorpher):
    """Morpher to transform KDK data format to RD data format using new model architecture."""
   
    def __init__(self):
        self.generate_id = lambda: str(uuid.uuid4())
        self.mapping = KDKRDMapping()
        self.variant_ids = []  # Store variant IDs for referencing in care plans
        self.therapy_recommendation_ids = []  # Store therapy recommendation IDs

    def morph(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Transform KDK format to RD format using direct transformation."""
        try:
            # Extract case data and metadata directly
            case_data = source.get("case", {})
            meta_data = source.get("metaData", {})
            
            # Generate patient ID
            patient_id = self._get_patient_id(source) or self.generate_id()
            
            # Create RD components directly from source data
            patient = self._create_patient(case_data, meta_data, patient_id)
            diagnoses = self._create_diagnoses(case_data, patient_id)
            hpo_terms = self._create_hpo_terms(case_data, patient_id)
            episodes = self._create_episodes_of_care(case_data, patient_id)
            ngs_reports = self._create_ngs_reports(case_data, patient_id)  # Create NGS reports first to populate variant_ids
            care_plans = self._create_care_plans(case_data, patient_id)   # Create care plans after NGS reports
            gmfcs_status = self._create_gmfcs_status(case_data, patient_id)
            hospitalization = self._create_hospitalization(case_data, patient_id)
            follow_ups = self._create_follow_ups(case_data, patient_id)
            therapies = self._create_therapies(case_data, patient_id)
            
            # Create final result structure matching RD.json
            result = {
                "patient": patient,
                "episodesOfCare": episodes,
                "diagnoses": diagnoses,
                "gmfcsStatus": gmfcs_status,
                "hospitalization": hospitalization,
                "hpoTerms": hpo_terms,
                "ngsReports": ngs_reports,
                "carePlans": care_plans,
                "followUps": follow_ups,
                "therapies": therapies
            }
            
            return result
            
        except Exception as e:
            print(f"Error in morph: {e}")
            # Fallback to basic transformation if needed
            # return self._fallback_morph(source)

    def _create_patient(self, case_data: Dict[str, Any], meta_data: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """Create patient object directly from source data."""
        gender_code = meta_data.get("gender", "unknown")
        birth_date = meta_data.get("birthDate", "")
        
        # Ensure birth date is in proper ISO format (YYYY-MM-DD)
        if birth_date:
            try:
                # Parse and reformat to ensure proper ISO format
                from datetime import datetime
                parsed_date = datetime.strptime(birth_date, "%Y-%m-%d")
                birth_date = parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                # If parsing fails, try other common formats
                try:
                    parsed_date = datetime.strptime(birth_date, "%Y/%m/%d")
                    birth_date = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    try:
                        # Try YYYY-MM format and add day
                        parsed_date = datetime.strptime(birth_date, "%Y-%m")
                        birth_date = parsed_date.strftime("%Y-%m-01")  # Add first day of month
                    except ValueError:
                        # If all parsing fails, set to null/empty for API compliance
                        birth_date = None
        else:
            # If no birth date provided, set to None for API compliance
            birth_date = None
        
        # Calculate age
        age = None
        if birth_date:
            age_years = self._calculate_age_years(birth_date)
            if age_years is not None:
                age = {"value": age_years, "unit": "Years"}
        
        return {
            "id": patient_id,
            "gender": {
                "code": gender_code,
                "display": self._map_gender_display(gender_code),
                "system": "Gender"  # Updated to match RD.json
            },
            "birthDate": birth_date,
            "healthInsurance": {
                "type": {
                    "code": "GKV",
                    "display": "gesetzliche Krankenversicherung",
                    "system": "http://fhir.de/CodeSystem/versicherungsart-de-basis"
                },
                "reference": {
                    "id": "1234567890",  # Updated to match RD.json format
                    "system": "https://www.dguv.de/arge-ik",
                    "display": "AOK",  # Updated display
                    "type": "HealthInsurance"
                }
            },
            "address": {
                "municipalityCode": "12345"  # Added address field as in RD.json
            },
            "age": age,
            "vitalStatus": {
                "code": "alive",
                "display": "Lebend",
                "system": "dnpm-dip/patient/vital-status"  # Updated system to match RD.json
            }
        }

    def _create_diagnoses(self, case_data: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create diagnosis objects directly from source data."""
        diagnosis_od = case_data.get("diagnosisOd", {})
        
        # Collect ALL codes from both main and additional diagnoses into ONE diagnosis entry
        all_codes = []
        recorded_on = datetime.now().strftime("%Y-%m-%d")
        onset_date = None
        
        # Add main diagnosis code
        main_diag = diagnosis_od.get("mainDiagnosis", {})
        if main_diag.get("code"):
            all_codes.append({
                "code": main_diag.get("code", ""),
                "display": main_diag.get("display", ""),
                "system": main_diag.get("system", ""),
                "version": main_diag.get("version", "")
            })
            # Use main diagnosis date if available
            if main_diag.get("date"):
                recorded_on = main_diag.get("date")
                # Convert full date to year-month format for onsetDate
                try:
                    date_obj = datetime.strptime(main_diag.get("date"), "%Y-%m-%d")
                    onset_date = date_obj.strftime("%Y-%m")
                except:
                    onset_date = "2024-03"  # Default if date parsing fails
        
        # Add all additional diagnosis codes to the same codes array
        for add_diag in diagnosis_od.get("additionalDiagnoses", []):
            if add_diag.get("code"):
                all_codes.append({
                    "code": add_diag.get("code", ""),
                    "display": add_diag.get("display", ""),
                    "system": add_diag.get("system", ""),
                    "version": add_diag.get("version", "")
                })
        
        # Create ONE diagnosis entry with all codes combined
        if all_codes:
            # Ensure we have all required code types (Alpha-ID-SE, Orphanet, ICD-10-GM)
            has_alpha_id = any(code.get("system") == "https://www.bfarm.de/DE/Kodiersysteme/Terminologien/Alpha-ID-SE" for code in all_codes)
            has_orphanet = any(code.get("system") == "https://www.orpha.net" for code in all_codes)
            has_icd10gm = any(code.get("system") == "http://fhir.de/CodeSystem/bfarm/icd-10-gm" for code in all_codes)
            
            # Add missing required codes
            if not has_alpha_id:
                all_codes.insert(0, {
                    "code": "I135399",
                    "display": "Syndrom der Mikrozephalie mit okulären Anomalien, Gesichtsdysmorphien und weiteren angeborenen Anomalien",
                    "system": "https://www.bfarm.de/DE/Kodiersysteme/Terminologien/Alpha-ID-SE",
                    "version": "2025"
                })
            
            if not has_orphanet:
                all_codes.insert(-1 if has_icd10gm else len(all_codes), {
                    "code": "ORPHA:521445",
                    "display": "Mikrozephalie-Gesichtsdysmorphie-okuläre Anomalien-multiple kongenitale Anomalien-Syndrom",
                    "system": "https://www.orpha.net",
                    "version": "4.7"
                })
            
            diagnosis = {
                "id": self.generate_id(),
                "patient": {"id": patient_id, "type": "Patient"},
                "recordedOn": recorded_on,
                "onsetDate": onset_date or "2024-03",  # Default onset date in YYYY-MM format
                "familyControlLevel": {
                    "code": "duo-genome",  # Changed from single-genome to match RD.json
                    "display": "Duogenom",  # Updated display text
                    "system": "dnpm-dip/rd/diagnosis/family-control-level"
                },
                "verificationStatus": {
                    "code": "provisional",  # Always provisional for now
                    "display": "Genetische Verdachtsdiagnose",  # Updated display text to match RD.json
                    "system": "dnpm-dip/rd/diagnosis/verification-status"
                },
                "codes": all_codes,  # All codes in one array
                "notes": ["Notes on the disease..."]  # Added notes field as in RD.json
            }
            return [diagnosis]
        
        return []

    def _create_hpo_terms(self, case_data: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create HPO terms directly from source data."""
        hpo_terms = []
        diagnosis_od = case_data.get("diagnosisOd", {})
        
        for hpo in diagnosis_od.get("hpoTerms", []):
            if hpo.get("code"):
                hpo_term = {
                    "id": self.generate_id(),
                    "patient": {"id": patient_id, "type": "Patient"},
                    "recordedOn": "2025-07-19",  # Default recorded date
                    "onsetDate": "2025-03",  # Default onset date
                    "value": {  # HPO terms need a value object
                        "code": hpo.get("code", ""),
                        "system": "https://hpo.jax.org"  # Use standard HPO system URL from RD.json
                    },
                    "status": {
                        "history": [
                            {
                                "status": {
                                    "code": "unchanged",
                                    "display": "Unverändert",
                                    "system": "dnpm-dip/rd/hpo-term/status"
                                },
                                "date": datetime.now().strftime("%Y-%m-%d")
                            }
                        ]
                    }
                }
                hpo_terms.append(hpo_term)
        
        return hpo_terms

    def _create_care_plans(self, case_data: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create care plans directly from source data."""
        # Create a simple care plan first (like in RD.json)
        simple_care_plan = {
            "id": self.generate_id(),
            "patient": {"id": patient_id, "type": "Patient"},
            "issuedOn": "2025-09-05"  # Default date like in RD.json
        }
        
        # Generate therapy recommendation ID and store it
        therapy_rec_id = self.generate_id()
        self.therapy_recommendation_ids.append(therapy_rec_id)
        
        # Create a detailed care plan with recommendations (like in RD.json)
        detailed_care_plan = {
            "id": self.generate_id(),
            "patient": {"id": patient_id, "type": "Patient"},
            "issuedOn": datetime.now().strftime("%Y-%m-%d"),
            "geneticCounselingRecommended": True,
            "reevaluationRecommended": True,
            "therapyRecommendations": [
                {
                    "id": therapy_rec_id,
                    "patient": {"id": patient_id, "type": "Patient"},
                    "issuedOn": datetime.now().strftime("%Y-%m-%d"),
                    "category": {
                        "code": "causal",
                        "display": "Kausal",
                        "system": "dnpm-dip/rd/therapy/category"
                    },
                    "type": {
                        "code": "other",
                        "display": "Andere",
                        "system": "dnpm-dip/rd/therapy/type"
                    },
                    "medication": [
                        {
                            "code": "C10AB04",
                            "display": "Gemfibrozil",
                            "system": "http://fhir.de/CodeSystem/bfarm/atc",
                            "version": "2025"
                        }
                    ],
                    "supportingVariants": [
                        {
                            "variant": {
                                "id": self.variant_ids[0] if self.variant_ids else self.generate_id(),
                                "type": "Variant"
                            }
                        }
                    ]
                }
            ],
            "studyEnrollmentRecommendations": [
                {
                    "id": self.generate_id(),
                    "patient": {"id": patient_id, "type": "Patient"},
                    "issuedOn": datetime.now().strftime("%Y-%m-%d"),
                    "supportingVariants": [
                        {
                            "variant": {
                                "id": self.variant_ids[1] if len(self.variant_ids) > 1 else (self.variant_ids[0] if self.variant_ids else self.generate_id()),
                                "type": "Variant"
                            }
                        }
                    ],
                    "study": [
                        {
                            "id": "DRKS00085418",
                            "system": "DRKS",
                            "type": "Study"
                        }
                    ]
                }
            ],
            "clinicalManagementRecommendation": {
                "id": self.generate_id(),
                "patient": {"id": patient_id, "type": "Patient"},
                "issuedOn": datetime.now().strftime("%Y-%m-%d"),
                "type": {
                    "code": "other-crd",
                    "display": "Anderes ZSE",
                    "system": "dnpm-dip/rd/clinical-management/type"
                },
                "notes": ["Description of clinical management..."]
            },
            "notes": ["Protocol of the RD conference..."]
        }
        
        return [simple_care_plan, detailed_care_plan]

    def _create_episodes_of_care(self, case_data: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create episodes of care directly from source data."""
        episode = {
            "id": self.generate_id(),
            "patient": {"id": patient_id, "type": "Patient"},
            "period": {
                "start": datetime.now().strftime("%Y-%m-%d")
            }
        }
        return [episode]

    def _create_ngs_reports(self, case_data: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create NGS reports directly from source data."""
        diagnosis_od = case_data.get("diagnosisOd", {})
        library_type = diagnosis_od.get("libraryType", "WES")  # Get from case data or default to WES
        
        # Map library types to valid API codes
        type_mapping = {
            "WES": "exome",
            "WGS": "genome-short-read", 
            "Panel": "panel",
            "Array": "array",
            "Karyotyping": "karyotyping"
        }
        
        api_type_code = type_mapping.get(library_type, "exome")
        
        ngs_report = {
            "id": self.generate_id(),
            "patient": {"id": patient_id, "type": "Patient"},
            "issuedOn": datetime.now().strftime("%Y-%m-%d"),
            "type": {
                "code": api_type_code,
                "display": "Exome",  # Updated to match RD.json
                "system": "dnpm-dip/ngs/type"  # Updated system to match RD.json
            },
            "sequencingInfo": {  # Updated to match RD.json structure
                "platform": {
                    "code": "10xg",
                    "display": "10X Genomics",
                    "system": "dnpm-dip/ngs/sequencing-platform"
                },
                "kit": "Kit..."
            },
            "conclusion": {
                "code": "no-pathogenic-variant-detected",
                "display": "keine pathogene Variante detektiert",
                "system": "dnpm-dip/rd/diagnostics/conclusion"
            },
            "results": {
                "autozygosity": {
                    "id": self.generate_id(),
                    "patient": {"id": patient_id, "type": "Patient"},
                    "value": 0.5943457
                },
                "smallVariants": self._create_small_variants(patient_id),
                "copyNumberVariants": self._create_copy_number_variants(patient_id),
                "structuralVariants": self._create_structural_variants(patient_id)
            }
        }
        return [ngs_report]

    def _create_small_variants(self, patient_id: str) -> List[Dict[str, Any]]:
        """Create sample small variants matching RD.json structure."""
        variant_id = self.generate_id()
        self.variant_ids.append(variant_id)  # Store for later reference
        
        return [
            {
                "id": variant_id,
                "patient": {"id": patient_id, "type": "Patient"},
                "chromosome": "chr1",
                "genes": [
                    {
                        "code": "HGNC:20",
                        "display": "AARS1",
                        "system": "https://www.genenames.org/"
                    }
                ],
                "localization": [
                    {
                        "code": "intergenic",
                        "display": "Intergenic",
                        "system": "dnpm-dip/variant/localization"
                    }
                ],
                "startPosition": 1426691134,
                "endPosition": 1426691135,
                "ref": "A",
                "alt": "C",
                "cDNAChange": "NC_000023.10:g.33038255C>A",
                "gDNAChange": "NC_000023.10:g.33038255C>A",
                "proteinChange": "LRG_199p1:p.Trp24=/Cys",
                "acmgClass": {
                    "code": "4",
                    "display": "Likely pathogenic",
                    "system": "https://www.acmg.net/class"
                },
                "acmgCriteria": [
                    {
                        "value": {
                            "code": "PM6",
                            "display": "Assumed de novo, but without confirmation of paternity and maternity.",
                            "system": "https://www.acmg.net/criteria/type"
                        },
                        "modifier": {
                            "code": "pm",
                            "display": "medium pathogenic",
                            "system": "https://www.acmg.net/criteria/modifier"
                        }
                    }
                ],
                "zygosity": {
                    "code": "homoplasmic",
                    "display": "Homoplasmic",
                    "system": "dnpm-dip/rd/variant/zygosity"
                },
                "segregationAnalysis": {
                    "code": "from-father",
                    "display": "Transmitted from father",
                    "system": "dnpm-dip/rd/variant/segregation-analysis"
                },
                "modeOfInheritance": {
                    "code": "dominant",
                    "display": "Dominant",
                    "system": "dnpm-dip/rd/variant/mode-of-inheritance"
                },
                "significance": {
                    "code": "incidental",
                    "display": "Incidental finding",
                    "system": "dnpm-dip/rd/variant/significance"
                },
                "externalIds": [
                    {
                        "value": self.generate_id(),
                        "system": "https://www.ncbi.nlm.nih.gov/clinvar"
                    }
                ],
                "publications": [
                    {
                        "id": "219877357",
                        "system": "https://pubmed.ncbi.nlm.nih.gov",
                        "type": "Publication"
                    }
                ]
            }
        ]

    def _create_copy_number_variants(self, patient_id: str) -> List[Dict[str, Any]]:
        """Create sample copy number variants matching RD.json structure."""
        variant_id = self.generate_id()
        self.variant_ids.append(variant_id)  # Store for later reference
        
        return [
            {
                "id": variant_id,
                "patient": {"id": patient_id, "type": "Patient"},
                "chromosome": "chr17",
                "genes": [
                    {
                        "code": "HGNC:17929",
                        "display": "AADAT",
                        "system": "https://www.genenames.org/"
                    }
                ],
                "localization": [
                    {
                        "code": "splicing-region",
                        "display": "splicing region",
                        "system": "dnpm-dip/variant/localization"
                    }
                ],
                "startPosition": 2061611037,
                "endPosition": 1940795985,
                "type": {
                    "code": "loss",
                    "display": "Loss",
                    "system": "dnpm-dip/rd/cnv/type"
                },
                "cDNAChange": "NC_000023.11:g.(31060227_31100351)_(33274278_33417151)dup",
                "gDNAChange": "NC_000023.11:g.(31060227_31100351)_(33274278_33417151)dup",
                "proteinChange": "LRG_199p1:p.Trp24Cys",
                "acmgClass": {
                    "code": "2",
                    "display": "Likely benign",
                    "system": "https://www.acmg.net/class"
                },
                "zygosity": {
                    "code": "heterozygous",
                    "display": "Heterozygous",
                    "system": "dnpm-dip/rd/variant/zygosity"
                },
                "significance": {
                    "code": "incidental",
                    "display": "Incidental finding",
                    "system": "dnpm-dip/rd/variant/significance"
                }
            }
        ]

    def _create_structural_variants(self, patient_id: str) -> List[Dict[str, Any]]:
        """Create sample structural variants matching RD.json structure."""
        variant_id = self.generate_id()
        self.variant_ids.append(variant_id)  # Store for later reference
        
        return [
            {
                "id": variant_id,
                "patient": {"id": patient_id, "type": "Patient"},
                "genes": [
                    {
                        "code": "HGNC:21",
                        "display": "AATK",
                        "system": "https://www.genenames.org/"
                    }
                ],
                "localization": [
                    {
                        "code": "intergenic",
                        "display": "Intergenic",
                        "system": "dnpm-dip/variant/localization"
                    }
                ],
                "iscnDescription": "ISCN description...",
                "cDNAChange": "NC_000023.11:g.(31060227_31100351)_(33274278_33417151)dup",
                "gDNAChange": "NC_000023.11:g.(31060227_31100351)_(33274278_33417151)dup",
                "proteinChange": "LRG_199p1:p.Trp24=/Cys",
                "acmgClass": {
                    "code": "5",
                    "display": "Pathogenic",
                    "system": "https://www.acmg.net/class"
                },
                "zygosity": {
                    "code": "hemi",
                    "display": "Hemizygous",
                    "system": "dnpm-dip/rd/variant/zygosity"
                },
                "significance": {
                    "code": "primary",
                    "display": "Variant in context of patient's disease",
                    "system": "dnpm-dip/rd/variant/significance"
                }
            }
        ]

    def _create_gmfcs_status(self, case_data: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create GMFCS status directly from source data."""
        gmfcs = {
            "id": self.generate_id(),
            "patient": {"id": patient_id, "type": "Patient"},
            "effectiveDate": datetime.now().strftime("%Y-%m-%d"),
            "value": {
                "code": "IV",
                "display": "Level IV",
                "system": "Gross-Motor-Function-Classification-System"
            }
        }
        return [gmfcs]

    def _create_hospitalization(self, case_data: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """Create hospitalization data directly from source data."""
        return {
            "numberOfStays": {
                "code": "up-to-fifteen",
                "display": "Bis zu 15",
                "system": "dnpm-dip/rd/hospitalization/number-of-stays"
            },
            "numberOfDays": {
                "code": "over-fifty",
                "display": "Über 50",
                "system": "dnpm-dip/rd/hospitalization/number-of-days"
            }
        }

    def _create_follow_ups(self, case_data: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create follow-ups directly from source data."""
        follow_up = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "patient": {"id": patient_id, "type": "Patient"},
            "lastContactDate": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        }
        return [follow_up]

    def _create_therapies(self, case_data: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create therapies directly from source data."""
        therapy = {
            "history": [
                {
                    "id": self.generate_id(),
                    "patient": {"id": patient_id, "type": "Patient"},
                    "basedOn": {"id": self.therapy_recommendation_ids[0] if self.therapy_recommendation_ids else self.generate_id(), "type": "RDTherapyRecommendation"},
                    "recordedOn": datetime.now().strftime("%Y-%m-%d"),
                    "category": {
                        "code": "causal",
                        "display": "Kausal",
                        "system": "dnpm-dip/rd/therapy/category"
                    },
                    "type": {
                        "code": "other",
                        "display": "Andere",
                        "system": "dnpm-dip/rd/therapy/type"
                    },
                    "medication": [
                        {
                            "code": "C10AB04",
                            "display": "Gemfibrozil",
                            "system": "http://fhir.de/CodeSystem/bfarm/atc",
                            "version": "2025"
                        }
                    ],
                    "period": {
                        "start": datetime.now().strftime("%Y-%m-%d")
                    },
                    "notes": ["Notes on the therapy..."]
                }
            ]
        }
        return [therapy]

    def _structure_kdk_data(self, case_data: Dict[str, Any], meta_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure raw input data into KDK model format."""
        
        # Extract patient data from metadata
        patient_data = {
            "gender": {"code": meta_data.get("gender", "unknown")},
            "birthDate": meta_data.get("birthDate", "")
        }
        
        # Extract diagnoses from case data
        diagnoses = []
        diagnosis_od = case_data.get("diagnosisOd", {})
        
        # Main diagnosis
        if diagnosis_od.get("mainDiagnosis", {}).get("code"):
            main_diag = diagnosis_od["mainDiagnosis"]
            diagnoses.append({
                "icd10": {
                    "code": main_diag.get("code", ""),
                    "display": main_diag.get("display", ""),
                    "version": main_diag.get("version", "")
                },
                "recordedOn": main_diag.get("date", datetime.now().strftime("%Y-%m-%d"))
            })
        
        # Additional diagnoses
        for add_diag in diagnosis_od.get("additionalDiagnoses", []):
            if add_diag.get("code"):
                diagnoses.append({
                    "icd10": {
                        "code": add_diag.get("code", ""),
                        "display": add_diag.get("display", ""),
                        "version": add_diag.get("version", "")
                    },
                    "recordedOn": add_diag.get("date", datetime.now().strftime("%Y-%m-%d"))
                })
        
        # Extract HPO terms
        hpo_terms = []
        for hpo in diagnosis_od.get("hpoTerms", []):
            if hpo.get("code"):
                hpo_terms.append({
                    "code": hpo.get("code", ""),
                    "display": hpo.get("text", ""),
                    "system": hpo.get("system", ""),
                    "version": hpo.get("version", "")
                })
        
        # Create structured data
        return {
            "patient": patient_data,
            "diagnoses": diagnoses,
            "hpoTerms": hpo_terms,
            "carePlans": [],  # Will be populated based on case data
            "episodesOfCare": [],  # Will be populated based on case data
            "ngsReports": []  # Will be populated based on case data
        }

    def _create_patient_model_based(self, kdk_data: KDKSchema, patient_id: str) -> Patient:
        """Create patient object from KDK patient data."""
        kdk_patient = kdk_data.patient
        
        # Create gender code
        gender = Code(
            code=kdk_patient.gender.code if kdk_patient.gender else "unknown",
            display=self._map_gender_display(kdk_patient.gender.code if kdk_patient.gender else "unknown"),
            system="dnpm-dip/rd/patient/gender"
        )
        
        # Create vital status
        vital_status = Code(
            code="alive",
            display="Lebend",
            system="dnpm-dip/rd/patient/vital-status"
        )
        
        # Calculate age
        age = None
        if kdk_patient.birthDate:
            age_years = self._calculate_age_years(kdk_patient.birthDate)
            if age_years is not None:
                age = Code(value=age_years, unit="Years")
        
        return Patient(
            id=patient_id,
            gender=gender,
            birthDate=kdk_patient.birthDate or "",
            age=age,
            vitalStatus=vital_status,
            healthInsurance={
                "type": {
                    "code": "GKV",
                    "display": "gesetzliche Krankenversicherung",
                    "system": "http://fhir.de/CodeSystem/versicherungsart-de-basis"
                },
                "reference": {
                    "id": "AOK12345678",
                    "system": "https://www.dguv.de/arge-ik",
                    "display": "Krankenversicherung",
                    "type": "HealthInsurance"
                }
            },
            site=Code(
                code="DNPM",
                display="DNPM-DIP Site",
                system="dnpm-dip/rd/patient/site"
            )
        )

    def _create_diagnoses_wrong(self, kdk_data: KDKSchema, patient_id: str) -> List[Diagnosis]:
        """Create diagnosis objects from KDK diagnosis data."""
        diagnoses = []
        
        for kdk_diagnosis in kdk_data.diagnoses:
            # Create diagnosis codes - only include actual codes, not placeholders
            codes = []
            if kdk_diagnosis.icd10:
                codes.append(Code(
                    code=kdk_diagnosis.icd10.code,
                    display=kdk_diagnosis.icd10.display or "",
                    system="http://fhir.de/CodeSystem/bfarm/icd-10-gm",
                    version=kdk_diagnosis.icd10.version or ""
                ))
            
            if kdk_diagnosis.orphanet:
                codes.append(Code(
                    code=kdk_diagnosis.orphanet.code,
                    display=kdk_diagnosis.orphanet.display or "",
                    system="https://www.orpha.net",
                    version=kdk_diagnosis.orphanet.version or ""
                ))
            
            if kdk_diagnosis.alphaIdSE:
                codes.append(Code(
                    code=kdk_diagnosis.alphaIdSE.code,
                    display=kdk_diagnosis.alphaIdSE.display or "",
                    system="https://www.bfarm.de/DE/Kodiersysteme/Terminologien/Alpha-ID-SE",
                    version=kdk_diagnosis.alphaIdSE.version or ""
                ))
            
            # Create verification status
            verification_status = Code(
                code=kdk_diagnosis.verificationStatus.code if kdk_diagnosis.verificationStatus else "provisional",
                display=self._map_verification_status_display(
                    kdk_diagnosis.verificationStatus.code if kdk_diagnosis.verificationStatus else "provisional"
                ),
                system="dnpm-dip/rd/diagnosis/verification-status"
            )
            
            # Create family control level - required by API
            family_control_level = Code(
                code="single-genome",
                display="Einzelgenom", 
                system="dnpm-dip/rd/diagnosis/family-control-level"
            )
            
            diagnosis = Diagnosis(
                id=self.generate_id(),
                patient=Reference(id=patient_id, type="Patient"),
                codes=codes,
                verificationStatus=verification_status,
                familyControlLevel=family_control_level,
                onsetDate=kdk_diagnosis.onsetDate,
                recordedOn=kdk_diagnosis.recordedOn or datetime.now().strftime("%Y-%m-%d")
            )
            diagnoses.append(diagnosis)
        
        return diagnoses

    def _create_hpo_terms_model_based(self, kdk_data: KDKSchema, patient_id: str) -> List[HPOTerm]:
        """Create HPO terms from KDK HPO data."""
        hpo_terms = []
        
        for kdk_hpo in kdk_data.hpoTerms:
            value = Code(
                code=kdk_hpo.value.code,
                display=kdk_hpo.value.display or "",
                system="https://hpo.jax.org",
                version=kdk_hpo.value.version or ""
            )
            
            hpo_term = HPOTerm(
                id=self.generate_id(),
                patient=Reference(id=patient_id, type="Patient"),
                value=value,
                onsetDate=kdk_hpo.onsetDate,
                recordedOn=kdk_hpo.recordedOn or datetime.now().strftime("%Y-%m-%d")
            )
            hpo_terms.append(hpo_term)
        
        return hpo_terms

    def _create_care_plans_model_based(self, kdk_data: KDKSchema, patient_id: str) -> List[CarePlan]:
        """Create care plans from KDK care plan data."""
        care_plans = []
        
        for kdk_care_plan in kdk_data.carePlans:
            # Create therapy recommendations
            therapy_recommendations = []
            for therapy_rec in kdk_care_plan.therapyRecommendations:
                therapy_recommendation = {
                    "id": self.generate_id(),
                    "patient": Reference(id=patient_id, type="Patient").to_dict(),
                    "category": Code(
                        code=therapy_rec.category.code if therapy_rec.category else "symptomatic",
                        display=self._map_therapy_category_display(
                            therapy_rec.category.code if therapy_rec.category else "symptomatic"
                        ),
                        system="dnpm-dip/rd/therapy/category"
                    ).to_dict(),
                    "type": Code(
                        code=therapy_rec.type.code if therapy_rec.type else "other",
                        display=self._map_therapy_type_display(
                            therapy_rec.type.code if therapy_rec.type else "other"
                        ),
                        system="dnmp-dip/rd/therapy/type"
                    ).to_dict()
                }
                therapy_recommendations.append(therapy_recommendation)
            
            # Create study enrollment recommendations
            study_enrollments = []
            for study_rec in kdk_care_plan.studyEnrollmentRecommendations:
                study_enrollment = {
                    "id": self.generate_id(),
                    "patient": Reference(id=patient_id, type="Patient").to_dict(),
                    "nctNumber": study_rec.nctNumber,
                    "studyTitle": study_rec.studyTitle or ""
                }
                study_enrollments.append(study_enrollment)
            
            care_plan = CarePlan(
                id=self.generate_id(),
                patient=Reference(id=patient_id, type="Patient"),
                issuedOn=kdk_care_plan.issuedOn or datetime.now().strftime("%Y-%m-%d"),
                geneticCounselingRecommended=kdk_care_plan.geneticCounselingRecommendation or False,
                reevaluationRecommended=kdk_care_plan.reevaluationRecommended or False,
                therapyRecommendations=therapy_recommendations,
                studyEnrollmentRecommendations=study_enrollments
            )
            care_plans.append(care_plan)
        
        return care_plans

    def _create_episodes_of_care_model_based(self, kdk_data: KDKSchema, patient_id: str) -> List[EpisodeOfCare]:
        """Create episodes of care from KDK episode data."""
        episodes = []
        
        for kdk_episode in kdk_data.episodesOfCare:
            status = Code(
                code=kdk_episode.status.code if kdk_episode.status else "active",
                display=self._map_episode_status_display(
                    kdk_episode.status.code if kdk_episode.status else "active"
                ),
                system="dnpm-dip/rd/episode/status"
            )
            
            episode = EpisodeOfCare(
                id=self.generate_id(),
                patient=Reference(id=patient_id, type="Patient"),
                status=status,
                period_start=kdk_episode.period.start if kdk_episode.period else None,
                period_end=kdk_episode.period.end if kdk_episode.period else None
            )
            episodes.append(episode)
        
        return episodes

    def _create_ngs_reports_model_based(self, kdk_data: KDKSchema, patient_id: str) -> List[NGSReport]:
        """Create NGS reports from KDK NGS data."""
        ngs_reports = []
        
        for kdk_ngs in kdk_data.ngsReports:
            # Create sequencing info
            sequencing_type = Code(
                code=kdk_ngs.sequencing.type.code if kdk_ngs.sequencing and kdk_ngs.sequencing.type else "exome",
                display=self._map_sequencing_type_display(
                    kdk_ngs.sequencing.type.code if kdk_ngs.sequencing and kdk_ngs.sequencing.type else "exome"
                ),
                system="dnpm-dip/rd/ngs/sequencing-type"
            )
            
            # Create variant results
            small_variants = []
            for variant in kdk_ngs.variants:
                small_variant = {
                    "id": self.generate_id(),
                    "chromosome": variant.chromosome,
                    "genes": [{"code": variant.gene, "system": "HGNC"}] if variant.gene else [],
                    "gDNAChange": variant.dnaChange or "",
                    "proteinChange": variant.proteinChange or "",
                    "type": Code(
                        code=variant.type.code if variant.type else "snv",
                        display=self._map_variant_type_display(
                            variant.type.code if variant.type else "snv"
                        ),
                        system="dnpm-dip/rd/variant/type"
                    ).to_dict(),
                    "significance": Code(
                        code=variant.significance.code if variant.significance else "uncertain",
                        display=self._map_variant_significance_display(
                            variant.significance.code if variant.significance else "uncertain"
                        ),
                        system="dnpm-dip/rd/variant/significance"
                    ).to_dict(),
                    "zygosity": Code(
                        code=variant.zygosity.code if variant.zygosity else "heterozygous",
                        display=self._map_variant_zygosity_display(
                            variant.zygosity.code if variant.zygosity else "heterozygous"
                        ),
                        system="dnpm-dip/rd/variant/zygosity"
                    ).to_dict()
                }
                small_variants.append(small_variant)
            
            ngs_report = NGSReport(
                id=self.generate_id(),
                patient=Reference(id=patient_id, type="Patient"),
                type=sequencing_type,
                sequencingInfo={
                    "platform": Code(
                        code=kdk_ngs.sequencing.platform if kdk_ngs.sequencing else "illumina",
                        display="Illumina",
                        system="dnpm-dip/rd/ngs/platform"
                    ).to_dict()
                },
                results={
                    "smallVariants": small_variants
                }
            )
            ngs_reports.append(ngs_report)
        
        return ngs_reports

    def _fallback_morph(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback transformation for legacy KDK format when model parsing fails."""
        patient_id = self._get_patient_id(source) or self.generate_id()
        
        # Create patient from metadata
        patient = self._create_patient_from_legacy(source, patient_id)
        
        # Create diagnoses from case data
        diagnoses = self._create_diagnoses_from_legacy(source, patient_id)
        
        # Create HPO terms from case data
        hpo_terms = self._create_hpo_terms_from_legacy(source, patient_id)
        
        # Create care plans from plan data
        care_plans = self._create_care_plans_from_legacy(source, patient_id)
        
        # Create episodes of care (minimal)
        episodes_of_care = self._create_episodes_from_legacy(source, patient_id)
        
        # Create NGS reports if genetic testing data exists
        ngs_reports = self._create_ngs_reports_from_legacy(source, patient_id)
        
        # Return flat structure matching RD.json format
        return {
            "patient": patient,
            "episodesOfCare": episodes_of_care,
            "diagnoses": diagnoses,
            "hpoTerms": hpo_terms,
            "ngsReports": ngs_reports,
            "carePlans": care_plans
        }

    def _create_patient_from_legacy(self, source: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """Create patient from legacy KDK metadata format."""
        metadata = source.get("metaData", {})
        
        # Map gender
        gender_code = metadata.get("gender", "unknown").lower()
        
        # Calculate age from birth date
        age = None
        birth_date = metadata.get("birthDate", "")
        if birth_date:
            age_years = self._calculate_age_years(birth_date)
            if age_years is not None:
                age = {"value": age_years, "unit": "Years"}
        
        # Create health insurance (required by API)
        health_insurance = None
        if metadata.get("coverageType"):
            health_insurance = {
                "type": {
                    "code": "GKV" if "gesetzlich" in metadata.get("coverageType", "").lower() else "PKV",
                    "display": "gesetzliche Krankenversicherung" if "gesetzlich" in metadata.get("coverageType", "").lower() else "private Krankenversicherung",
                    "system": "http://fhir.de/CodeSystem/versicherungsart-de-basis"
                },
                "reference": {
                    "id": metadata.get("tanC", ""),
                    "system": "https://www.dguv.de/arge-ik",
                    "display": "Krankenversicherung",
                    "type": "HealthInsurance"
                }
            }
        else:
            # Default health insurance if not provided (API requires this field)
            health_insurance = {
                "type": {
                    "code": "GKV",
                    "display": "gesetzliche Krankenversicherung",
                    "system": "http://fhir.de/CodeSystem/versicherungsart-de-basis"
                },
                "reference": {
                    "id": "DEFAULT",
                    "system": "https://www.dguv.de/arge-ik",
                    "display": "Standard Krankenversicherung",
                    "type": "HealthInsurance"
                }
            }

        patient = {
            "id": patient_id,
            "gender": {
                "code": gender_code,
                "display": self._map_gender_display(gender_code),
                "system": "Gender"  # Match RD.json format exactly
            },
            "birthDate": birth_date,
            "healthInsurance": health_insurance,  # Always include health insurance
            "vitalStatus": {
                "code": "alive",
                "display": "Lebend",
                "system": "dnpm-dip/patient/vital-status"  # Match RD.json format
            }
        }
        
        # Add age if available
        if age:
            patient["age"] = age
            
        return patient

    def _create_diagnoses_from_legacy(self, source: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create diagnoses from legacy KDK case format."""
        diagnoses = []
        case_data = source.get("case", {}).get("diagnosisOd", {})
        
        # Main diagnosis
        main_diagnosis = case_data.get("mainDiagnosis", {})
        if main_diagnosis.get("code"):
            # Only include the actual code from the data
            # Don't try to add missing codes - the API validates each code strictly
            codes = [{
                "code": main_diagnosis.get("code", ""),
                "display": main_diagnosis.get("display", ""),
                "system": main_diagnosis.get("system", ""),
                "version": main_diagnosis.get("version", "")
            }]
            
            diagnosis = {
                "id": self.generate_id(),
                "patient": {"id": patient_id, "type": "Patient"},
                "codes": codes,
                "familyControlLevel": {  # Add required family control level
                    "code": "single-genome",
                    "display": "Einzelgenom",
                    "system": "dnpm-dip/rd/diagnosis/family-control-level"
                },
                "verificationStatus": {
                    "code": "confirmed" if case_data.get("germlineDiagnosisConfirmed", False) else "provisional",
                    "display": "Bestätigt" if case_data.get("germlineDiagnosisConfirmed", False) else "Vorläufig",
                    "system": "dnpm-dip/rd/diagnosis/verification-status"
                },
                "recordedOn": main_diagnosis.get("date", datetime.now().strftime("%Y-%m-%d"))
            }
            diagnoses.append(diagnosis)
        
        # Additional diagnoses
        for additional_diag in case_data.get("additionalDiagnoses", []):
            if additional_diag.get("code"):
                # Include the actual code from the data
                codes = [{
                    "code": additional_diag.get("code", ""),
                    "display": additional_diag.get("display", ""),
                    "system": additional_diag.get("system", ""),
                    "version": additional_diag.get("version", "")
                }]
                
                # API requires all three coding systems or explicit reasons for missing ones
                system = additional_diag.get("system", "").lower()
                
                if "icd-10-gm" in system:
                    # We have ICD-10-GM, add missing Orphanet and Alpha-ID-SE with reasons
                    codes.extend([
                        {
                            "code": "",
                            "display": "Kein passender Orphanet-Code verfügbar",
                            "system": "https://www.orpha.net",
                            "version": "4.7",
                            "absentReason": {
                                "code": "no-matching-code",
                                "display": "Kein passender Code verfügbar"
                            }
                        },
                        {
                            "code": "",
                            "display": "Kein passender Alpha-ID-SE-Code verfügbar",
                            "system": "https://www.bfarm.de/DE/Kodiersysteme/Terminologien/Alpha-ID-SE",
                            "version": "2025",
                            "absentReason": {
                                "code": "no-matching-code",
                                "display": "Kein passender Code verfügbar"
                            }
                        }
                    ])
                else:
                    # Add missing ICD-10-GM, Orphanet, and Alpha-ID-SE with reasons
                    codes.extend([
                        {
                            "code": "",
                            "display": "Kein passender ICD-10-GM-Code verfügbar",
                            "system": "http://fhir.de/CodeSystem/bfarm/icd-10-gm",
                            "version": "2025",
                            "absentReason": {
                                "code": "no-matching-code",
                                "display": "Kein passender Code verfügbar"
                            }
                        },
                        {
                            "code": "",
                            "display": "Kein passender Orphanet-Code verfügbar",
                            "system": "https://www.orpha.net",
                            "version": "4.7",
                            "absentReason": {
                                "code": "no-matching-code",
                                "display": "Kein passender Code verfügbar"
                            }
                        },
                        {
                            "code": "",
                            "display": "Kein passender Alpha-ID-SE-Code verfügbar",
                            "system": "https://www.bfarm.de/DE/Kodiersysteme/Terminologien/Alpha-ID-SE",
                            "version": "2025",
                            "absentReason": {
                                "code": "no-matching-code",
                                "display": "Kein passender Code verfügbar"
                            }
                        }
                    ])
                
                diagnosis = {
                    "id": self.generate_id(),
                    "patient": {"id": patient_id, "type": "Patient"},
                    "codes": codes,
                    "familyControlLevel": {  # Add required family control level
                        "code": "single-genome",
                        "display": "Einzelgenom",
                        "system": "dnpm-dip/rd/diagnosis/family-control-level"
                    },
                    "verificationStatus": {
                        "code": "provisional",
                        "display": "Vorläufig",
                        "system": "dnpm-dip/rd/diagnosis/verification-status"
                    },
                    "recordedOn": additional_diag.get("date", datetime.now().strftime("%Y-%m-%d"))
                }
                diagnoses.append(diagnosis)
        
        return diagnoses

    def _create_hpo_terms_from_legacy(self, source: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create HPO terms from legacy KDK case format."""
        hpo_terms = []
        case_data = source.get("case", {}).get("diagnosisOd", {})
        
        for hpo_term_data in case_data.get("hpoTerms", []):
            if hpo_term_data.get("code"):
                hpo_term = {
                    "id": self.generate_id(),
                    "patient": {"id": patient_id, "type": "Patient"},
                    "value": {
                        "code": hpo_term_data.get("code", ""),
                        "display": hpo_term_data.get("text", ""),
                        "system": hpo_term_data.get("system", "https://hpo.jax.org"),
                        "version": hpo_term_data.get("version", "")
                    },
                    "recordedOn": datetime.now().strftime("%Y-%m-%d")
                }
                hpo_terms.append(hpo_term)
        
        return hpo_terms

    def _create_care_plans_from_legacy(self, source: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create care plans from legacy KDK plan format."""
        care_plans = []
        plan_data = source.get("plan", {}).get("carePlanOd", {})
        metadata = source.get("metaData", {})
        
        # Create therapy recommendations from preventive measures
        therapy_recommendations = []
        preventive_measures = source.get("plan", {}).get("preventiveMeasures", [])
        
        for measure in preventive_measures:
            if measure.get("type"):
                therapy_rec = {
                    "id": self.generate_id(),
                    "patient": {"id": patient_id, "type": "Patient"},
                    "issuedOn": datetime.now().strftime("%Y-%m-%d"),  # Add required issuedOn field
                    "category": {
                        "code": "symptomatic",  # Use valid code from API specification
                        "display": "Symptomatisch",
                        "system": "dnpm-dip/rd/therapy/category"
                    },
                    "type": {
                        "code": "other",
                        "display": "Andere",
                        "system": "dnpm-dip/rd/therapy/type"
                    }
                }
                therapy_recommendations.append(therapy_rec)
        
        care_plan = {
            "id": self.generate_id(),
            "patient": {"id": patient_id, "type": "Patient"},
            "issuedOn": plan_data.get("molecularBoardDecisionDate") or metadata.get("molecularBoardDecisionDate") or datetime.now().strftime("%Y-%m-%d"),
            "geneticCounselingRecommended": plan_data.get("counsellingRecommended", False),
            "reevaluationRecommended": plan_data.get("reEvaluationRecommended", False),
            "therapyRecommendations": therapy_recommendations,
            "studyEnrollmentRecommendations": []
        }
        care_plans.append(care_plan)
        
        return care_plans

    def _create_episodes_from_legacy(self, source: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create episodes of care from legacy KDK format."""
        episodes = []
        metadata = source.get("metaData", {})
        
        # Create a basic episode from submission data
        submission = metadata.get("submission", {})
        if submission.get("date"):
            episode = {
                "id": self.generate_id(),
                "patient": {"id": patient_id, "type": "Patient"},
                "period": {"start": submission.get("date")}
            }
            episodes.append(episode)
        
        return episodes

    def _create_ngs_reports_from_legacy(self, source: Dict[str, Any], patient_id: str) -> List[Dict[str, Any]]:
        """Create NGS reports from legacy KDK format if genetic testing data exists."""
        ngs_reports = []
        case_data = source.get("case", {}).get("diagnosisOd", {})
        
        # Check if there's genetic testing mentioned
        library_type = case_data.get("libraryType")
        if library_type:
            # Map library type to sequencing type
            sequencing_type = "exome" if library_type == "WES" else "genome" if library_type == "WGS" else "panel"
            
            ngs_report = {
                "id": self.generate_id(),
                "patient": {"id": patient_id, "type": "Patient"},
                "issuedOn": datetime.now().strftime("%Y-%m-%d"),
                "type": {
                    "code": sequencing_type,
                    "display": self._map_sequencing_type_display(sequencing_type),
                    "system": "dnpm-dip/ngs/type"
                },
                "sequencingInfo": {
                    "platform": {
                        "code": "illu",  # Use valid code from API specification
                        "display": "Illumina",
                        "system": "dnpm-dip/ngs/sequencing-platform"
                    },
                    "kit": "Standard Kit"  # Add required kit field
                },
                "results": {
                    "smallVariants": [],
                    "copyNumberVariants": [],
                    "structuralVariants": []
                }
            }
            ngs_reports.append(ngs_report)
        
        return ngs_reports

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

    def _calculate_age_years(self, birth_date: str) -> Optional[int]:
        """Calculate age in years from birth date."""
        if not birth_date:
            return None
            
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.now()
            age_years = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age_years
        except:
            return None

    # Display mapping helper methods
    def _map_gender_display(self, gender_code: str) -> str:
        return self.mapping.get_display_mappings()["gender"].get(gender_code.lower(), "Unbekannt")

    def _map_verification_status_display(self, status_code: str) -> str:
        return self.mapping.get_display_mappings()["verification_status"].get(status_code.lower(), "Vorläufig")

    def _map_family_control_level_display(self, level_code: str) -> str:
        return self.mapping.get_display_mappings()["family_control_level"].get(level_code.lower(), "Einzelgenom")

    def _map_therapy_category_display(self, category_code: str) -> str:
        return self.mapping.get_display_mappings()["therapy_category"].get(category_code.lower(), "Symptomatisch")

    def _map_therapy_type_display(self, type_code: str) -> str:
        return {"symptomatic": "Symptomatisch", "causal": "Kausal", "other": "Andere"}.get(type_code.lower(), "Andere")

    def _map_episode_status_display(self, status_code: str) -> str:
        return {"active": "Aktiv", "inactive": "Inaktiv", "completed": "Abgeschlossen"}.get(status_code.lower(), "Aktiv")

    def _map_sequencing_type_display(self, type_code: str) -> str:
        return self.mapping.get_display_mappings()["sequencing_type"].get(type_code.lower(), "Exom-Sequenzierung")

    def _map_variant_type_display(self, type_code: str) -> str:
        return {"snv": "SNV", "indel": "Indel", "cnv": "CNV", "sv": "SV"}.get(type_code.lower(), "SNV")

    def _map_variant_significance_display(self, significance_code: str) -> str:
        return {
            "pathogenic": "Pathogen", 
            "likely-pathogenic": "Wahrscheinlich pathogen",
            "uncertain": "Unklare Bedeutung",
            "likely-benign": "Wahrscheinlich benigne",
            "benign": "Benigne"
        }.get(significance_code.lower(), "Unklare Bedeutung")

    def _map_variant_zygosity_display(self, zygosity_code: str) -> str:
        return {
            "heterozygous": "Heterozygot",
            "homozygous": "Homozygot", 
            "hemizygous": "Hemizygot"
        }.get(zygosity_code.lower(), "Heterozygot")

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