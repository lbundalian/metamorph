# example usage of the FastAPI API
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

# example KDK data
example_kdk_data = {
    "case": {
        "diagnoses": [
            {
                "icd10": {"code": "Q87.8", "display": "Other specified congenital malformation syndromes"},
                "orphanet": {"code": "ORPHA:199", "display": "Cornelia de Lange syndrome"}
            }
        ],
        "hpoTerms": [
            {
                "value": {"code": "HP:0001156", "display": "Brachydactyly"}
            }
        ]
    },
    "metaData": {
        "patient": {
            "id": "patient-123",
            "gender": {"code": "male", "display": "Male"},
            "birthDate": "1990-01-15"
        }
    },
    "plan": {
        "therapyRecommendations": []
    }
}

def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_convert_kdk():
    """Test KDK to RD conversion"""
    print("🔄 Testing KDK to RD conversion...")
    response = requests.post(
        f"{BASE_URL}/convert",
        json={"data": example_kdk_data}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result['success']}")
    if result['success']:
        print("✅ Conversion successful!")
        return result['rd_data']
    else:
        print(f"❌ Conversion failed: {result['error']}")
        return None
    print("-" * 50)

def test_validate_kdk():
    """Test KDK validation"""
    print("✅ Testing KDK validation...")
    response = requests.post(
        f"{BASE_URL}/validate-kdk",
        json={"data": example_kdk_data}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Valid: {result['is_valid']}")
    print(f"Message: {result['message']}")
    if result['errors']:
        print(f"Errors: {result['errors']}")
    print("-" * 50)

def test_validate_rd(rd_data):
    """Test RD validation"""
    if not rd_data:
        print("❌ No RD data to validate")
        return
    
    print("🔍 Testing RD validation...")
    response = requests.post(
        f"{BASE_URL}/validate-rd",
        json=rd_data
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Valid: {result['is_valid']}")
    print(f"Message: {result['message']}")
    if result['errors']:
        print(f"Errors: {result['errors']}")
    print("-" * 50)

def test_convert_and_validate():
    """Test combined conversion and validation"""
    print("🚀 Testing convert and validate...")
    response = requests.post(
        f"{BASE_URL}/convert-and-validate",
        json={"data": example_kdk_data}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    
    # conversion result
    conv = result['conversion']
    print(f"Conversion Success: {conv['success']}")
    if not conv['success']:
        print(f"Conversion Error: {conv['error']}")
    
    # validation result
    val = result['validation']
    print(f"Validation Valid: {val['is_valid']}")
    print(f"Validation Message: {val['message']}")
    if val['errors']:
        print(f"Validation Errors: {val['errors']}")
    print("-" * 50)

if __name__ == "__main__":
    print("🧪 Testing Metamorph API endpoints...")
    print("=" * 60)
    
    try:
        # test health check
        test_health_check()
        
        # test KDK validation
        test_validate_kdk()
        
        # test conversion
        rd_data = test_convert_kdk()
        
        # test RD validation
        test_validate_rd(rd_data)
        
        # test combined
        test_convert_and_validate()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running:")
        print("   python app/run_app.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")