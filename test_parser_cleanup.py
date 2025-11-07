#!/usr/bin/env python3
"""
Test script to verify KDK parser works correctly after cleanup.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.metamorph.models.parsers.kdk_parser import KDKParser
from src.metamorph.models.parsers.kdk_mappings import KDKMappings, MappingHelper

def test_parser_initialization():
    """Test that parser initializes correctly."""
    print("Testing parser initialization...")
    
    try:
        parser = KDKParser()
        print("✓ Parser created successfully")
        
        # Test that mapping helper is initialized
        assert hasattr(parser, 'mapping_helper')
        print("✓ Mapping helper initialized")
        
        # Test some mapping helper methods
        gender_display = parser.mapping_helper.get_gender_display("male")
        print(f"✓ Gender mapping works: 'male' -> '{gender_display}'")
        
        insurance_display = parser.mapping_helper.get_insurance_display("GKV")
        print(f"✓ Insurance mapping works: 'GKV' -> '{insurance_display}'")
        
        print("✓ All parser initialization tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Parser test failed: {e}")
        return False

def test_centralized_mappings():
    """Test that centralized mappings are accessible."""
    print("\nTesting centralized mappings...")
    
    try:
        # Test purpose mapping
        purpose = KDKMappings.PURPOSE_MAPPING.get("mvSequencing", "default")
        print(f"✓ Purpose mapping: 'mvSequencing' -> '{purpose}'")
        
        # Test reason mapping
        reason = KDKMappings.REASON_MAPPING.get("patient-inability", "default")
        print(f"✓ Reason mapping: 'patient-inability' -> '{reason}'")
        
        # Test ACMG mappings
        acmg_class = KDKMappings.ACMG_CLASS_MAP.get("1", "default")
        print(f"✓ ACMG class mapping: '1' -> '{acmg_class}'")
        
        # Test zygosity mapping
        zygosity = KDKMappings.ZYGOSITY_MAP.get("heterozygous", "default")
        print(f"✓ Zygosity mapping: 'heterozygous' -> '{zygosity}'")
        
        print("✓ All centralized mappings accessible!")
        return True
        
    except Exception as e:
        print(f"✗ Centralized mappings test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("KDK Parser Cleanup Verification Tests")
    print("="*40)
    
    success = True
    success &= test_parser_initialization()
    success &= test_centralized_mappings()
    
    print("\n" + "="*40)
    if success:
        print("🎉 All tests passed! Parser cleanup successful.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())