# Metamorph FastAPI Application

FastAPI web application for KDK to RD conversion with Swagger documentation.

## Features

- **Convert KDK to RD**: Convert KDK JSON format to RD format
- **Validate KDK**: Validate KDK JSON input format
- **Validate RD**: Validate RD JSON output against DNPM-DIP API
- **Convert & Validate**: Combined conversion and validation in one step
- **Swagger Documentation**: Interactive API documentation
- **Health Check**: Service health monitoring

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/convert` | POST | Convert KDK JSON to RD format |
| `/validate-kdk` | POST | Validate KDK JSON input |
| `/validate-rd` | POST | Validate RD JSON output |
| `/convert-and-validate` | POST | Convert and validate in one step |
| `/health` | GET | Health check |
| `/swagger` | GET | Swagger UI documentation |
| `/redoc` | GET | ReDoc documentation |

## Installation

1. Install dependencies:
```bash
pip install -r app/requirements.txt
```

## Running the Application

### Option 1: Using the run script
```bash
python app/run_app.py
```

### Option 2: Using uvicorn directly
```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using the main.py directly
```bash
cd app
python main.py
```

## Accessing the API

- **API Base URL**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/swagger`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## Testing the API

Use the provided test script:
```bash
python app/test_api.py
```

## Example Usage

### Convert KDK to RD
```bash
curl -X POST "http://localhost:8000/convert" \
     -H "Content-Type: application/json" \
     -d '{
       "data": {
         "case": {
           "diagnoses": [
             {
               "icd10": {"code": "Q87.8", "display": "Other specified congenital malformation syndromes"}
             }
           ]
         },
         "metaData": {
           "patient": {
             "id": "patient-123",
             "gender": {"code": "male", "display": "Male"},
             "birthDate": "1990-01-15"
           }
         }
       }
     }'
```

### Validate KDK
```bash
curl -X POST "http://localhost:8000/validate-kdk" \
     -H "Content-Type: application/json" \
     -d '{"data": {...}}'
```

### Convert and Validate
```bash
curl -X POST "http://localhost:8000/convert-and-validate" \
     -H "Content-Type: application/json" \
     -d '{"data": {...}}'
```

## Response Formats

### Conversion Response
```json
{
  "success": true,
  "rd_data": {...},
  "error": null
}
```

### Validation Response
```json
{
  "is_valid": true,
  "message": "Validation passed",
  "errors": null
}
```

### Convert and Validate Response
```json
{
  "conversion": {
    "success": true,
    "rd_data": {...},
    "error": null
  },
  "validation": {
    "is_valid": true,
    "message": "Validation passed",
    "errors": null
  }
}
```

## Configuration

Edit `config.py` to customize:
- API settings (title, version, description)
- Server settings (host, port)
- DNPM-DIP API URL
- CORS origins

## Development

The API automatically reloads when files change if you use the `--reload` flag with uvicorn.

## Error Handling

All endpoints include proper error handling and return appropriate HTTP status codes with detailed error messages.