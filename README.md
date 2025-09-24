# Metamorph - Medical Data Transformation Library

<p align="center">
  <img src="metamorph.png" alt="Metamorph Logo" width="120" height="120"/>
</p>

## Overview

Metamorph is a clean, extensible Python library for transforming medical data formats. Built with a clean architecture pattern, it currently focuses on converting KDK (Klinische Datenknoten) to RD (Rare Disease) data structures with full DNPM-DIP API validation support.

## 🏗️ Clean Architecture

The project follows a clean architecture pattern for maximum maintainability and extensibility:

```
metamorph/
├── main.py                 # Main entry point
├── src/metamorph/          # Core library
│   ├── models/             # Schema classes and data models
│   │   ├── parsers/        # Data parsers (KDKParser)
│   │   ├── kdk.py          # KDK main class with auto-parsing
│   │   ├── kdk_model.py    # KDK data models
│   │   └── rd_model.py     # RD data models  
│   ├── morphers/           # Data transformation scripts
│   │   ├── kdk_morpher.py  # Main KDKMorpher API
│   │   └── kdk_to_rd_morpher.py # Detailed KDK→RD transformation
│   └── utils/              # Utilities and validation
│       └── validate_api.py # DNPM-DIP API validation
├── tests/                  # Test suite
└── sample/                 # Sample data files
```


## ✨ Features

### 🔄 **Clean API Design**
- **Auto-parsing**: `KDK(json)` automatically parses JSON to structured objects
- **Simple Transformation**: `KDKMorpher(kdk_obj, 'RD')` for clean conversions
- **Extensible**: Designed for future schema support (FHIR, HL7, etc.)
- **Production Ready**: Full DNPM-DIP API validation integration

### 🏥 **Medical Data Support**

#### Patient Demographics
- ✅ Gender (with localized German display names)
- ✅ Birth date (ISO format with validation)
- ✅ Address (municipality codes)
- ✅ Age calculation from birth date
- ✅ Health insurance information (GKV/PKV)
- ✅ Vital status tracking

#### Clinical Information  
- ✅ ICD-10-GM diagnosis codes
- ✅ Alpha-ID-SE topography/histology codes
- ✅ HPO (Human Phenotype Ontology) terms
- ✅ Diagnosis verification status
- ✅ Family control levels
- ✅ NGS sequencing reports

#### Care Management
- ✅ Care plan recommendations
- ✅ Therapy recommendations (categori zed)
- ✅ Genetic counseling recommendations
- ✅ Study enrollment recommendations
- ✅ Follow-up tracking

### 🔒 **Validation & Quality**
- ✅ **DNPM-DIP API Integration**: Real-time validation against production API
- ✅ **Schema Compliance**: Strict adherence to RD schema requirements
- ✅ **Data Integrity**: Comprehensive input/output validation
- ✅ **Error Handling**: Detailed error messages and recovery

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/lbundalian/metamorph.git
cd metamorph

# Install dependencies
pip install -r requirements-test.txt

# Install in development mode (optional)
pip install -e .
```

### Basic Usage

The clean architecture provides a simple, intuitive API:

```python
from src.metamorph.models.kdk import KDK
from src.metamorph.morphers.kdk_morpher import KDKMorpher

# 1. Auto-parse KDK data (from file or dict)
kdk = KDK("path/to/your/kdk_data.json")  # Auto-parses JSON to KDK model

# 2. Transform to target schema  
morpher = KDKMorpher()
rd_object = morpher.morph(kdk, 'RD')  # Clean API: (kdk_obj, target_schema)

# 3. Save and validate
morpher.save(rd_object, "output/result.json")
is_valid, message = morpher.validate(rd_object)

if is_valid:
    print("✅ Transformation successful and API validated!")
else:
    print(f"❌ Validation failed: {message}")
```

### Run the Demo

```bash
# Run the main demonstration
python main.py
```

This will:
1. 📖 Parse KDK data using auto-parsing
2. 🔄 Transform to RD format using clean API  
3. 💾 Save output to `output/main_output.json`
4. 🔍 Validate against DNPM-DIP API
5. 📊 Display comprehensive results

## 🔧 Development

### Architecture Principles

- **models/**: Contains schema classes and parsers
- **morphers/**: Contains transformation logic between schemas
- **utils/**: Contains validation and utility functions
- **Clean API**: Simple, intuitive method signatures
- **Extensible**: Easy to add new target schemas (FHIR, HL7, etc.)

### Running Tests

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src/metamorph
```

### API Validation

The library integrates with DNPM-DIP API for real-time validation:

```python
# Validate against production API
is_valid, message = morpher.validate(rd_object, 'RD')
```

API endpoint: `https://preview.dnpm-dip.net/api/rd/etl/patient-record:validate`

## 🎯 Supported Schemas

### Current Support
- ✅ **KDK** → **RD**: Full implementation with API validation

### Planned Support  
- 🔄 **KDK** → **FHIR**: Future implementation
- 🔄 **KDK** → **HL7**: Future implementation
- 🔄 **RD** → **FHIR**: Future implementation

## 📁 Sample Data

The `sample/` directory contains:
- `sample/confidential/`: Real anonymized patient data
- `sample/dummy/`: Test data for development

## 📊 Output

Generated files are saved to `output/`:
- `main_output.json`: Main transformation result
- Various test outputs and validation results
## 🗂️ Data Mapping

### Key KDK → RD Transformations

| KDK Source | RD Target | Transformation |
|------------|-----------|----------------|
| `metaData.gender` | `patient.gender` | With German localization |
| `metaData.birthDate` | `patient.birthDate` | ISO format validation |
| `case.diagnosisOd.mainDiagnosis` | `diagnoses[].icd10` | ICD-10-GM mapping |
| `case.diagnosisOd.hpoTerms` | `hpoTerms[]` | HPO term preservation |
| `plan.carePlanOd.*` | `carePlans[]` | Care recommendations |
| `case.diagnosisOd.topography` | `diagnoses[].alphaIdSE` | Alpha-ID-SE codes |

### Auto-Generated Elements
- ✅ **UUIDs**: Unique identifiers for all entities  
- ✅ **Timestamps**: Proper medical event dating
- ✅ **Age Calculation**: From birth date
- ✅ **Status Codes**: DNPM-DIP compliant statuses

## 🎯 Project Status

### ✅ **Current Implementation**
- **Clean Architecture**: Full implementation with organized structure
- **KDK → RD**: Complete transformation with API validation
- **Auto-parsing**: Seamless JSON to object conversion  
- **Production Ready**: DNPM-DIP API integration and validation
- **Test Coverage**: Comprehensive test suite

### 🔄 **Future Roadmap**
- **Additional Schemas**: FHIR, HL7 support
- **Bi-directional**: RD → KDK transformation
- **Enhanced Validation**: More detailed clinical validation rules
- **Performance**: Batch processing capabilities

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/new-schema`
3. **Commit** changes: `git commit -am 'Add FHIR support'`  
4. **Push** to branch: `git push origin feature/new-schema`
5. **Submit** a Pull Request

### Development Setup
```bash
git clone https://github.com/lbundalian/metamorph.git
cd metamorph
pip install -r requirements-test.txt
python -m pytest tests/ -v  # Run tests
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **DNPM-DIP**: For providing the validation API
- **genomeDE**: Medical data standards and requirements  
- **Contributors**: All developers who helped build this clean architecture

---

**Metamorph** - *Clean, extensible medical data transformation* 🏥➡️📊
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