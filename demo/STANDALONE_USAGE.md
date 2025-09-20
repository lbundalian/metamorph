# Standalone Usage Guide - No Installation Required

## ✅ **YES! You can use Metamorph without installing it as a package!**

The metamorph library is designed to work directly from source code without requiring package installation. Here's how to use it:

## 📁 **Directory Structure Required**
```
metamorph/
├── src/
│   └── metamorph/
│       ├── models/
│       ├── morphers/
│       └── utils/
├── demo/
├── sample/
└── your_script.py
```

## 🚀 **Method 1: Use the Demo Script (Recommended)**

Simply run the demo script directly from the project directory:

```bash
# Basic conversion
python demo/demo_kdk_to_rd_converter.py sample/KDK.json

# With validation
python demo/demo_kdk_to_rd_converter.py sample/KDK.json --validate

# Custom output file
python demo/demo_kdk_to_rd_converter.py input.json output.json --validate --verbose
```

## 🔧 **Method 2: Direct Import in Your Script**

Create your own Python script in the metamorph directory:

```python
#!/usr/bin/env python3
import os
import sys
import json

# Add src directory to Python path (REQUIRED for standalone usage)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now you can import metamorph modules
from metamorph.morphers.kdk_to_rd_morpher import KDKToRDMorpher
from metamorph.utils.rd_schema_converter import RDSchemaConverter

# Load your KDK data
with open('your_kdk_file.json', 'r', encoding='utf-8') as f:
    kdk_data = json.load(f)

# Transform to RD format
morpher = KDKToRDMorpher()
rd_result = morpher.morph(kdk_data)

# Validate the result (optional)
converter = RDSchemaConverter()
is_valid, errors, warnings = converter.validate_schema_compliance(rd_result)

# Save the result
with open('output_rd.json', 'w', encoding='utf-8') as f:
    json.dump(rd_result, f, indent=2, ensure_ascii=False)

print("✅ Conversion completed!")
```

## 📋 **Method 3: Run the Standalone Example**

```bash
python standalone_example.py
```

This will show you a complete working example with sample data.

## 🔗 **Key Points for Standalone Usage**

### ✅ **Requirements**
- Python 3.8 or higher
- No additional packages required (uses only Python standard library)
- All source files must be in their original directory structure

### ✅ **Critical Code Pattern**
Always add this at the top of your scripts:
```python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
```

### ✅ **File Paths**
- Run scripts from the main metamorph directory
- Use relative paths for input/output files
- The demo script handles path resolution automatically

## 🎯 **Tested Scenarios**

All of these work without package installation:

✅ **Simple KDK files** (like `sample/KDK.json`)
✅ **Complex medical cases** (like `sample/2508261858_Case_250825_E2E2_KDK.json`)
✅ **Custom output paths**
✅ **Schema validation**
✅ **Large datasets** (50+ HPO terms, 20+ diagnoses)

## 🔧 **Troubleshooting**

### Problem: `ModuleNotFoundError: No module named 'metamorph'`
**Solution**: Make sure you're running from the metamorph project directory and have the `sys.path.insert()` line.

### Problem: `FileNotFoundError`
**Solution**: Use relative paths from the metamorph directory or absolute paths.

### Problem: Import errors
**Solution**: Ensure the `src/` directory structure is intact.

## 🌟 **Advantages of Standalone Usage**

- ✅ **No installation required** - just download and run
- ✅ **No dependency management** - works with standard Python
- ✅ **Easy distribution** - share the entire project folder
- ✅ **Development friendly** - modify source code directly
- ✅ **Portable** - works on any system with Python

## 📞 **Quick Start Command**

```bash
# Download/clone the project, then:
cd metamorph
python demo/demo_kdk_to_rd_converter.py sample/KDK.json --validate
```

That's it! No pip install, no virtual environments, no package management - just direct usage! 🎉