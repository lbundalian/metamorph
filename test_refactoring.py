# Test to verify the KDK parser refactoring
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.metamorph.models.parsers.kdk_parser import KDKParser
from src.metamorph.models.parsers.kdk_mappings import KDKMappings, MappingHelper

def test_mappings():
    """Test that our mappings are working correctly."""
    
    # Test gender mapping
    assert MappingHelper.get_gender_display("male") == "Männlich"
    assert MappingHelper.get_gender_display("female") == "Weiblich"
    assert MappingHelper.get_gender_display("unknown") == "Unbekannt"
    
    # Test insurance mapping
    assert MappingHelper.get_insurance_display("GKV") == "Gesetzliche Krankenversicherung"
    assert MappingHelper.get_insurance_display("UNK") == "Unbekannt"
    
    # Test ACMG class mapping
    assert MappingHelper.get_acmg_class_display("5") == "Pathogenic"
    assert MappingHelper.get_acmg_class_display("3") == "Uncertain significance"
    
    # Test zygosity mapping
    assert MappingHelper.get_zygosity_display("heterozygous") == "Heterozygous"
    assert MappingHelper.get_zygosity_display("homozygous") == "Homozygous"
    
    # Test research consent reason parsing
    assert MappingHelper.parse_research_consent_reason("patient refusal") == "patient-refusal"
    assert MappingHelper.parse_research_consent_reason({"reason": "technical-issues"}) == "technical-issues"
    
    print("✅ All mapping tests passed!")

def test_parser_initialization():
    """Test that the parser can be initialized correctly."""
    parser = KDKParser()
    assert parser is not None
    print("✅ Parser initialization test passed!")

if __name__ == "__main__":
    test_mappings()
    test_parser_initialization()
    print("🎉 All tests passed! The refactoring is working correctly.")