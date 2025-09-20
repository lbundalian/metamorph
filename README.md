# Metamorph - Bfarm Schema parser

<p align="center">
  <img src="metamorph.png" alt="Metamorph Logo" width="120" height="120"/>
</p>

## Overview

Metamorph is a Python module designed for transforming medical data formats involved in genomeDE project.First iteration focuses on converting KDK (Klinische Datenknoten) to RD (Rare Disease) data structures and is designed to enable extension for future X2X conversion.


## Features

### 🔄 **Data Transformation**
- **KDK to RD Conversion**: Complete transformation from KDK format to RD-compatible structure
- **Field Mapping**: Intelligent mapping of medical data fields between formats
- **Data Validation**: Comprehensive validation for both input and output data
- **Error Handling**: Robust error handling with detailed error messages

### 📊 **Supported Data Elements**

#### Patient Demographics
- ✅ Gender (with German display names)
- ✅ Birth date
- ✅ Address (municipality code)
- ✅ Age calculation
- ✅ Health insurance information
- ✅ Vital status

#### Medical Information  
- ✅ Primary and additional diagnoses
- ✅ HPO (Human Phenotype Ontology) terms
- ✅ Diagnosis verification status
- ✅ Care plan recommendations
- ✅ Therapy recommendations
- ✅ Genetic counseling recommendations

#### Administrative Data
- ✅ Patient IDs (UUID generation)
- ✅ Recording dates
- ✅ Consent information mapping

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd metamorph

# Install in development mode
pip install -e .
```

## Quick Start

```python
from metamorph import KDKToRDMorpher
from metamorph.utils import DataValidator
import json

# Load your KDK data
with open('your_kdk_data.json', 'r') as f:
    kdk_data = json.load(f)

# Validate input data
is_valid, errors = DataValidator.validate_kdk_data(kdk_data)
if not is_valid:
    print("Validation errors:", errors)
    exit(1)

# Transform KDK to RD format
morpher = KDKToRDMorpher()
rd_result = morpher.morph(kdk_data)

# Validate transformation result
is_valid, errors = DataValidator.validate_rd_data(rd_result)
if is_valid:
    print("✅ Transformation successful!")
else:
    print("❌ Transformation validation failed:", errors)

# Save result
with open('transformed_rd_data.json', 'w') as f:
    json.dump(rd_result, f, indent=2, ensure_ascii=False)
```

## Demonstration

Run the included demonstration script to see the transformation in action:

```bash
python demo_transformation.py
```

This will:
1. Create test KDK data with realistic values
2. Validate the input data
3. Transform KDK to RD format
4. Validate the output data
5. Check transformation quality
6. Save the result to `transformed_result.json`

## Data Mapping Details

### KDK → RD Field Mappings

| KDK Path | RD Path | Notes |
|----------|---------|-------|
| `metaData.gender` | `patient.gender.code` | With German display names |
| `metaData.birthDate` | `patient.birthDate` | ISO date format |
| `metaData.addressAGS` | `patient.address.municipalityCode` | German municipality code |
| `metaData.coverageType` | `patient.healthInsurance` | GKV/PKV mapping |
| `case.diagnosisOd.mainDiagnosis` | `diagnoses[0].codes` | Primary diagnosis |
| `case.diagnosisOd.additionalDiagnoses` | `diagnoses[1..n].codes` | Additional diagnoses |
| `case.diagnosisOd.hpoTerms` | `hpoTerms` | Phenotype terms |
| `case.diagnosisOd.germlineDiagnosisConfirmed` | `diagnoses[].verificationStatus` | Confirmation status |
| `plan.carePlanOd.counsellingRecommended` | `carePlans[].geneticCounselingRecommended` | Care recommendations |
| `plan.carePlanOd.reEvaluationRecommended` | `carePlans[].reevaluationRecommended` | Follow-up plans |
| `plan.preventiveMeasures` | `carePlans[].therapyRecommendations` | Therapy suggestions |

### Generated Fields

The transformation also generates additional required fields:
- **UUIDs**: Unique identifiers for all entities
- **Timestamps**: Recording dates for medical events
- **Status Information**: Proper medical coding systems
- **Age Calculation**: Automatic age computation from birth date

## Limitations & Scope

### ✅ **What IS Transformed**
- Basic patient demographics
- Diagnosis information (ICD-10, etc.)
- HPO phenotype terms
- Care plan recommendations
- Health insurance data
- Administrative metadata

### ⚠️ **What is NOT Available in KDK** (and thus not transformed)
- **NGS/Genomic Data**: Sequencing results, variants, etc.
- **Complex Genetic Analysis**: ACMG classifications, variant details
- **Hospitalization Details**: Stay duration, frequency
- **Detailed Therapy History**: Medication details, treatment responses
- **Family History**: Genetic pedigrees
- **Laboratory Results**: Detailed lab values

This is expected since KDK and RD serve different clinical contexts - RD format is more comprehensive for rare disease genetics research.

## Project Structure

```
metamorph/
├── src/metamorph/
│   ├── __init__.py              # Main package exports
│   ├── models/
│   │   ├── base_model.py        # Base model class
│   │   ├── kdk_model.py         # KDK data model
│   │   └── rd_model.py          # RD data model
│   ├── morphers/
│   │   ├── base_morpher.py      # Base transformation class
│   │   ├── kdk_morpher.py       # Legacy KDK morpher
│   │   └── kdk_to_rd_morpher.py # Main KDK→RD transformer
│   └── utils/
│       └── validators.py        # Validation utilities
├── sample/
│   ├── KDK.json                 # Sample KDK data
│   └── RD.json                  # Sample RD data
├── demo_transformation.py       # Demonstration script
└── README.md                    # This file
```

## Validation

The library includes comprehensive validation:

### Input Validation (KDK)
- Required section presence (`case`, `metaData`, `plan`)
- Essential fields like birth date
- At least one diagnosis or HPO term

### Output Validation (RD)
- Required RD structure compliance
- Valid UUID format for IDs
- Required patient fields
- Proper diagnosis structure

### Transformation Quality
- Data preservation checks
- Field mapping verification
- Warning system for data loss

## Examples

### Example Transformation Result

**Input KDK:**
```json
{
  "metaData": {
    "gender": "male",
    "birthDate": "2020-05-15"
  },
  "case": {
    "diagnosisOd": {
      "mainDiagnosis": {
        "code": "Q87.0",
        "display": "Congenital malformation syndrome"
      }
    }
  }
}
```

**Output RD:**
```json
{
  "patient": {
    "id": "e824f40c-a075-4c16-bf58-4c79938905d8",
    "gender": {
      "code": "male",
      "display": "Männlich",
      "system": "Gender"
    },
    "birthDate": "2020-05-15",
    "age": {
      "value": 5,
      "unit": "Years"
    }
  },
  "diagnoses": [
    {
      "id": "341c5252-b316-4172-80c7-7b1aa35860df",
      "patient": {"id": "e824f40c-a075-4c16-bf58-4c79938905d8", "type": "Patient"},
      "codes": [
        {
          "code": "Q87.0",
          "display": "Congenital malformation syndrome"
        }
      ]
    }
  ]
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all validations pass
5. Submit a pull request

## License

[Add your license information here]

## Support

For questions or issues:
- Check the demonstration script: `demo_transformation.py`
- Review validation error messages
- Check sample data in `/sample/` directory

---

## Summary

**✅ YES** - This project successfully transforms KDK data to RD-like structures with:
- Comprehensive field mapping
- Data validation
- Error handling
- Quality assurance
- Documentation and examples

The transformation preserves all available medical information while generating compliant RD format output suitable for rare disease research and clinical workflows.