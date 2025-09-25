# FastAPI main application with KDK to RD conversion endpoints
from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import sys
import os
from pathlib import Path
import tempfile
import json
import traceback

# add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.metamorph.models.kdk import KDK
from src.metamorph.morphers.kdk_morpher import KDKMorpher
from src.metamorph.utils.validate_api import validate_with_api

# create FastAPI app
app = FastAPI(
    title="Metamorph KDK to RD Converter API",
    description="API for converting KDK JSON to RD format with validation capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# mount static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# pydantic models for request/response  
class KDKInput(BaseModel):
    """Direct KDK JSON input model - accepts exact KDK JSON format"""
    case: Optional[Dict[str, Any]] = Field(None, description="KDK case data")
    metaData: Optional[Dict[str, Any]] = Field(None, description="KDK metadata")
    plan: Optional[Dict[str, Any]] = Field(None, description="KDK plan data")
    
    # allow for any additional fields that might be in KDK JSON
    class Config:
        extra = "allow"  # allow additional fields
    
    def get_kdk_data(self) -> Dict[str, Any]:
        """Get complete KDK data as dictionary"""
        return self.dict(exclude_unset=True)

class ValidationResult(BaseModel):
    """Validation result model"""
    is_valid: bool = Field(..., description="Whether validation passed")
    message: str = Field(..., description="Validation message")
    errors: Optional[List[str]] = Field(None, description="List of validation errors if any")

class ConversionResult(BaseModel):
    """Conversion result model"""
    success: bool = Field(..., description="Whether conversion was successful")
    rd_data: Optional[Dict[str, Any]] = Field(None, description="Converted RD data")
    error: Optional[str] = Field(None, description="Error message if conversion failed")

class ConvertAndValidateResult(BaseModel):
    """Combined conversion and validation result"""
    conversion: ConversionResult = Field(..., description="Conversion result")
    validation: ValidationResult = Field(..., description="Validation result")

# global morpher instance
morpher = KDKMorpher()

@app.get("/", response_class=HTMLResponse, summary="Landing Page")
async def landing_page():
    """Metamorph landing page with logo and API navigation"""
    template_path = Path(__file__).parent / "templates" / "index.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/api-info", summary="API Info (JSON)")
async def api_info():
    """Get API information in JSON format"""
    return {
        "message": "Metamorph KDK to RD Converter API",
        "version": "1.0.0",
        "endpoints": {
            "JSON Input": {
                "convert": "/convert - Convert KDK JSON to RD format",
                "validate-kdk": "/validate-kdk - Validate KDK JSON input",
                "convert-and-validate": "/convert-and-validate - Convert and validate in one step"
            },
            "File Upload": {
                "convert": "/convert/upload - Convert KDK JSON file to RD format",
                "validate-kdk": "/validate-kdk/upload - Validate KDK JSON file",
                "convert-and-validate": "/convert-and-validate/upload - Convert and validate KDK file in one step"
            },
            "Common": {
                "validate-rd": "/validate-rd - Validate RD JSON output",
                "health": "/health - Health check",
                "docs": "/docs - API documentation (Swagger UI)",
                "redoc": "/redoc - API documentation (ReDoc)"
            }
        }
    }

@app.post("/convert", 
          response_model=ConversionResult,
          summary="Convert KDK to RD (JSON)",
          description="Convert KDK JSON format to RD format via direct JSON input")
async def convert_kdk_to_rd(kdk_input: KDKInput):
    """
    Convert KDK JSON to RD format via direct JSON input
    
    Send your KDK JSON directly in the request body with the exact structure:
    ```json
    {
      "case": { ... },
      "metaData": { ... },
      "plan": { ... }
    }
    ```
    
    Returns the converted RD data or error information
    """
    try:
        # create KDK object from input data
        kdk_data = kdk_input.get_kdk_data()
        kdk_obj = KDK(kdk_data)
        
        # convert to RD format
        rd_data = morpher.morph(kdk_obj, 'RD')
        
        return ConversionResult(
            success=True,
            rd_data=rd_data,
            error=None
        )
        
    except Exception as e:
        return ConversionResult(
            success=False,
            rd_data=None,
            error=str(e)
        )

@app.post("/convert/upload", 
          response_model=ConversionResult,
          summary="Convert KDK to RD (File Upload)",
          description="Convert KDK JSON format to RD format via file upload")
async def convert_kdk_file_to_rd(file: UploadFile = File(..., description="KDK JSON file to convert")):
    """
    Convert KDK JSON file to RD format
    
    - **file**: KDK JSON file to upload and convert
    
    Returns the converted RD data or error information
    """
    try:
        # validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a JSON file"
            )
        
        # read file content
        content = await file.read()
        kdk_data = json.loads(content.decode('utf-8'))
        
        # create KDK object from file data
        kdk_obj = KDK(kdk_data)
        
        # convert to RD format
        rd_data = morpher.morph(kdk_obj, 'RD')
        
        return ConversionResult(
            success=True,
            rd_data=rd_data,
            error=None
        )
        
    except json.JSONDecodeError as e:
        return ConversionResult(
            success=False,
            rd_data=None,
            error=f"Invalid JSON file: {str(e)}"
        )
    except Exception as e:
        return ConversionResult(
            success=False,
            rd_data=None,
            error=str(e)
        )

@app.post("/validate-kdk",
          response_model=ValidationResult,
          summary="Validate KDK JSON (JSON input)",
          description="Validate KDK JSON input format via direct JSON input")
async def validate_kdk_json(kdk_input: KDKInput):
    """
    Validate KDK JSON input format via direct JSON input
    
    Send your KDK JSON directly in the request body with the exact structure:
    ```json
    {
      "case": { ... },
      "metaData": { ... },
      "plan": { ... }
    }
    ```
    
    Returns validation result
    """
    try:
        # try to create KDK object to validate format
        kdk_data = kdk_input.get_kdk_data()
        kdk_obj = KDK(kdk_data)
        
        # basic validation checks
        errors = []
        if not kdk_obj.schema.patient.id:
            errors.append("Patient ID is missing")
        
        if not kdk_obj.schema.diagnoses and not kdk_obj.schema.hpoTerms:
            errors.append("No diagnoses or HPO terms found")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            message="KDK validation passed" if is_valid else "KDK validation failed",
            errors=errors if errors else None
        )
        
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            message=f"KDK validation failed: {str(e)}",
            errors=[str(e)]
        )

@app.post("/validate-kdk/upload",
          response_model=ValidationResult,
          summary="Validate KDK JSON (File Upload)",
          description="Validate KDK JSON input format via file upload")
async def validate_kdk_file(file: UploadFile = File(..., description="KDK JSON file to validate")):
    """
    Validate KDK JSON file format
    
    - **file**: KDK JSON file to upload and validate
    
    Returns validation result
    """
    try:
        # validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a JSON file"
            )
        
        # read file content
        content = await file.read()
        kdk_data = json.loads(content.decode('utf-8'))
        
        # try to create KDK object to validate format
        kdk_obj = KDK(kdk_data)
        
        # basic validation checks
        errors = []
        if not kdk_obj.schema.patient.id:
            errors.append("Patient ID is missing")
        
        if not kdk_obj.schema.diagnoses and not kdk_obj.schema.hpoTerms:
            errors.append("No diagnoses or HPO terms found")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            message="KDK validation passed" if is_valid else "KDK validation failed",
            errors=errors if errors else None
        )
        
    except json.JSONDecodeError as e:
        return ValidationResult(
            is_valid=False,
            message=f"Invalid JSON file: {str(e)}",
            errors=[f"JSON parsing error: {str(e)}"]
        )
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            message=f"KDK validation failed: {str(e)}",
            errors=[str(e)]
        )
    """
    Validate KDK JSON input format
    
    - **data**: KDK JSON data to validate
    
    Returns validation result
    """
    try:
        # try to create KDK object to validate format
        kdk_data = kdk_input.get_kdk_data()
        kdk_obj = KDK(kdk_data)
        
        # basic validation checks
        errors = []
        if not kdk_obj.schema.patient.id:
            errors.append("Patient ID is missing")
        
        if not kdk_obj.schema.diagnoses and not kdk_obj.schema.hpoTerms:
            errors.append("No diagnoses or HPO terms found")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            message="KDK validation passed" if is_valid else "KDK validation failed",
            errors=errors if errors else None
        )
        
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            message=f"KDK validation failed: {str(e)}",
            errors=[str(e)]
        )

@app.post("/validate-rd",
          response_model=ValidationResult,
          summary="Validate RD JSON",
          description="Validate RD JSON output against DNPM-DIP API")
async def validate_rd_json(rd_data: Dict[str, Any]):
    """
    Validate RD JSON against DNPM-DIP API
    
    - **rd_data**: RD JSON data to validate
    
    Returns validation result from DNPM-DIP API
    """
    try:
        # create temporary file for validation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(rd_data, temp_file, indent=2)
            temp_file_path = temp_file.name
        
        try:
            # validate with API
            api_result = validate_with_api(temp_file_path)
            
            is_valid = api_result.get("validation_successful", False)
            message = api_result.get("message", "Validation completed")
            
            # extract errors if any
            errors = []
            if "api_response" in api_result and "errors" in api_result["api_response"]:
                errors = api_result["api_response"]["errors"]
            
            return ValidationResult(
                is_valid=is_valid,
                message=message,
                errors=errors if errors else None
            )
            
        finally:
            # clean up temp file
            os.unlink(temp_file_path)
            
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            message=f"RD validation failed: {str(e)}",
            errors=[str(e)]
        )

@app.post("/convert-and-validate",
          response_model=ConvertAndValidateResult,
          summary="Convert and Validate (JSON input)",
          description="Convert KDK to RD and validate the result in one step via direct JSON input")
async def convert_and_validate_kdk(kdk_input: KDKInput):
    """
    Convert KDK JSON to RD format and validate the result via direct JSON input
    
    Send your KDK JSON directly in the request body with the exact structure:
    ```json
    {
      "case": { ... },
      "metaData": { ... },
      "plan": { ... }
    }
    ```
    
    Returns both conversion and validation results
    """
    # first convert
    conversion_result = await convert_kdk_to_rd(kdk_input)
    
    # then validate if conversion was successful
    if conversion_result.success and conversion_result.rd_data:
        validation_result = await validate_rd_json(conversion_result.rd_data)
    else:
        validation_result = ValidationResult(
            is_valid=False,
            message="Cannot validate - conversion failed",
            errors=["Conversion failed"]
        )
    
    return ConvertAndValidateResult(
        conversion=conversion_result,
        validation=validation_result
    )

@app.post("/convert-and-validate/upload",
          response_model=ConvertAndValidateResult,
          summary="Convert and Validate (File Upload)",
          description="Convert KDK to RD and validate the result in one step via file upload")
async def convert_and_validate_kdk_file(file: UploadFile = File(..., description="KDK JSON file to convert and validate")):
    """
    Convert KDK JSON file to RD format and validate the result
    
    - **file**: KDK JSON file to upload, convert and validate
    
    Returns both conversion and validation results
    """
    # first convert
    conversion_result = await convert_kdk_file_to_rd(file)
    
    # then validate if conversion was successful
    if conversion_result.success and conversion_result.rd_data:
        validation_result = await validate_rd_json(conversion_result.rd_data)
    else:
        validation_result = ValidationResult(
            is_valid=False,
            message="Cannot validate - conversion failed",
            errors=["Conversion failed"]
        )
    
    return ConvertAndValidateResult(
        conversion=conversion_result,
        validation=validation_result
    )
    """
    Convert KDK JSON to RD format and validate the result
    
    - **data**: KDK JSON data to convert and validate
    
    Returns both conversion and validation results
    """
    # first convert
    conversion_result = await convert_kdk_to_rd(kdk_input)
    
    # then validate if conversion was successful
    if conversion_result.success and conversion_result.rd_data:
        validation_result = await validate_rd_json(conversion_result.rd_data)
    else:
        validation_result = ValidationResult(
            is_valid=False,
            message="Cannot validate - conversion failed",
            errors=["Conversion failed"]
        )
    
    return ConvertAndValidateResult(
        conversion=conversion_result,
        validation=validation_result
    )

@app.get("/example-kdk-format", summary="KDK JSON Format Example")
async def get_kdk_format_example():
    """Get an example of the expected KDK JSON format for the JSON input endpoints"""
    return {
        "description": "Use this exact JSON structure for the JSON input endpoints (/convert, /validate-kdk, /convert-and-validate)",
        "example_kdk_format": {
            "case": {
                "priorDiagnostic": {
                    "type": "genetic_testing",
                    "date": "2024-01-15"
                },
                "diagnosisOd": {
                    "germlineDiagnosisConfirmed": True,
                    "hpoTerms": [
                        {
                            "text": "Microcephaly",
                            "system": "https://hpo.jax.org",
                            "code": "HP:0000252",
                            "version": "2024-09-01"
                        }
                    ],
                    "mainDiagnosis": {
                        "code": "Q87.0",
                        "version": "2025",
                        "date": "2024-03-15",
                        "system": "http://fhir.de/CodeSystem/bfarm/icd-10-gm",
                        "display": "Angeborene Fehlbildungssyndrome"
                    }
                }
            },
            "metaData": {
                "patient": {
                    "id": "patient-123",
                    "gender": "male",
                    "birthDate": "1990-01-01"
                },
                "recordingDate": "2024-03-15",
                "center": "Center-001"
            },
            "plan": {
                "therapy": {
                    "type": "symptomatic",
                    "recommendations": ["Physical therapy", "Regular monitoring"]
                }
            }
        },
        "note": "This is the exact format you should use - no wrapping in 'data' field needed!"
    }

@app.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint"""
    try:
        # test that morpher is working
        test_data = {
            "case": {"diagnoses": []},
            "metaData": {"patient": {"id": "test"}},
            "plan": {}
        }
        test_kdk = KDK(test_data)
        return {"status": "healthy", "message": "API is working correctly"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)