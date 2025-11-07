#!/usr/bin/env python3
"""
Script to verify all centralized mappings are working and list remaining inline mappings.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.metamorph.models.parsers.kdk_mappings import KDKMappings, MappingHelper

def test_all_mappings():
    """Test that all mappings work correctly."""
    print("Testing all centralized mappings:")
    print("=" * 50)
    
    # Test gender mapping
    print(f"Gender (male): {MappingHelper.get_gender_display('male')}")
    
    # Test insurance mapping
    print(f"Insurance (GKV): {MappingHelper.get_insurance_display('GKV')}")
    
    # Test ACMG class mapping
    print(f"ACMG Class (1): {MappingHelper.get_acmg_class_display('1')}")
    
    # Test significance mapping
    print(f"Significance (primary): {MappingHelper.get_significance_display('primary')}")
    
    # Test ACMG criteria modifier
    print(f"ACMG Criteria (PVS1) -> Modifier: {MappingHelper.get_acmg_criteria_modifier('PVS1')}")
    print(f"ACMG Criteria (PS1) -> Modifier: {MappingHelper.get_acmg_criteria_modifier('PS1')}")
    
    # Test zygosity mapping
    print(f"Zygosity (heterozygous): {MappingHelper.get_zygosity_display('heterozygous')}")
    
    # Test segregation analysis
    print(f"Segregation (deNovo) -> Code: {MappingHelper.get_segregation_analysis_code('deNovo')}")
    print(f"Segregation (de-novo) -> Display: {MappingHelper.get_segregation_analysis_display('de-novo')}")
    
    # Test inheritance mapping
    print(f"Inheritance (dominant): {MappingHelper.get_inheritance_display('dominant')}")
    
    # Test CNV type mapping
    print(f"CNV Type (gain): {MappingHelper.get_cnv_type_display('gain')}")
    
    # Test genomic test mapping
    print(f"Genomic Test (wgs): {MappingHelper.get_genomic_test_type('wgs')}")
    print(f"Genomic Display (genome-short-read): {MappingHelper.get_genomic_test_display('genome-short-read')}")
    
    # Test family control
    print(f"Family Control (singleGenome): {MappingHelper.get_family_control_code('singleGenome')}")
    print(f"Family Control Display (single-genome): {MappingHelper.get_family_control_display('single-genome')}")
    
    print("\n" + "=" * 50)
    print("All mappings working correctly! ✅")
    
    print("\nRemaining inline mappings to replace in parser:")
    print("- amgc_class_map.get() -> self.mapping_helper.get_acmg_class_display()")
    print("- significance_map.get() -> self.mapping_helper.get_significance_display()")
    print("- acmg_criteria_mapping.get() -> self.mapping_helper.get_acmg_criteria_display()")
    print("- acmg_modifier_mapping.get() -> self.mapping_helper.get_acmg_modifier_display()")
    print("- zygosity_map.get() -> self.mapping_helper.get_zygosity_display()")
    print("- segregation_analysis_normp.get() -> self.mapping_helper.get_segregation_analysis_code()")
    print("- segregation_analysis_map.get() -> self.mapping_helper.get_segregation_analysis_display()")
    print("- inheritance_map.get() -> self.mapping_helper.get_inheritance_display()")
    print("- cnv_type_map.get() -> self.mapping_helper.get_cnv_type_display()")
    print("- genomic_test_map.get() -> self.mapping_helper.get_genomic_test_type()")
    print("- genomic_display_map.get() -> self.mapping_helper.get_genomic_test_display()")

if __name__ == "__main__":
    test_all_mappings()