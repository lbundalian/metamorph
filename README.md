# Metamorph - Medical Data Transformation Library

<p align="center">
  <img src="metamorph.png" alt="Metamorph Logo" width="120" height="120"/>
</p>

## Overview

Metamorph is a clean, extensible Python library for transforming medical data formats. Built with a clean architecture pattern, it currently focuses on converting KDK (Klinische Datenknoten) to RD (Rare Disease) data structures with full DNPM-DIP API validation support.


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



## 📁 Sample Data

The `sample/` directory contains:
- `sample/confidential/`: Real anonymized patient data
- `sample/dummy/`: Test data for development



### Development Setup
```bash
git clone https://github.com/lbundalian/metamorph.git
cd metamorph
pip install -r requirements-test.txt
python -m pytest tests/ -v  # Run tests
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

