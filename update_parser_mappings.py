#!/usr/bin/env python3
"""
Script to systematically replace all inline mapping usages in kdk_parser.py
"""

import sys
import os
import re

def replace_mapping_usages(file_path):
    """Replace all inline mapping usages with centralized mapping helper calls."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define replacement patterns
    replacements = [
        # ACMG class mapping
        (r'amgc_class_map\.get\(([^,]+),\s*"[^"]*"\)', r'self.mapping_helper.get_acmg_class_display(\1)'),
        
        # Significance mapping
        (r'significance_map\.get\(([^,]+),\s*"[^"]*"\)', r'self.mapping_helper.get_significance_display(\1)'),
        
        # ACMG criteria mapping
        (r'acmg_criteria_mapping\.get\(([^,]+),\s*"[^"]*"\)', r'self.mapping_helper.get_acmg_criteria_display(\1)'),
        
        # ACMG modifier mapping
        (r'acmg_modifier_mapping\.get\(([^,]+),\s*"[^"]*"\)', r'self.mapping_helper.get_acmg_modifier_display(\1)'),
        
        # Zygosity mapping
        (r'zygosity_map\.get\(([^,]+),\s*"[^"]*"\)', r'self.mapping_helper.get_zygosity_display(\1)'),
        
        # Segregation analysis code mapping (two-step process)
        (r'segregation_analysis_normp\.get\(([^,]+),\s*"[^"]*"\)', r'self.mapping_helper.get_segregation_analysis_code(\1)'),
        
        # Inheritance mapping
        (r'inheritance_map\.get\(([^,]+),\s*"[^"]*"\)', r'self.mapping_helper.get_inheritance_display(\1)'),
        
        # CNV type mapping
        (r'cnv_type_map\.get\(([^,]+),\s*"[^"]*"\)', r'self.mapping_helper.get_cnv_type_display(\1)'),
        
        # Genomic test mapping
        (r'genomic_test_map\.get\(([^,]+),\s*"[^"]*"\)', r'self.mapping_helper.get_genomic_test_type(\1)'),
        
        # Genomic display mapping
        (r'genomic_display_map\.get\(([^,]+),\s*"[^"]*"\)', r'self.mapping_helper.get_genomic_test_display(\1)'),
    ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Handle the complex segregation analysis display mapping
    # Replace patterns like: segregation_analysis_map.get(segregation_analysis_normp.get(...), "")
    content = re.sub(
        r'segregation_analysis_map\.get\(self\.mapping_helper\.get_segregation_analysis_code\(([^)]+)\),\s*"[^"]*"\)',
        r'self.mapping_helper.get_segregation_analysis_display(self.mapping_helper.get_segregation_analysis_code(\1))',
        content
    )
    
    return content

def remove_inline_mappings(content):
    """Remove all inline mapping definitions."""
    
    # Patterns to remove inline mapping definitions
    mapping_patterns = [
        r'\s*amgc_class_map\s*=\s*\{[^}]+\}\s*',
        r'\s*significance_map\s*=\s*\{[^}]+\}\s*',
        r'\s*acmg_criteria_mapping\s*=\s*\{[^}]+\}\s*',
        r'\s*acmg_modifier_mapping\s*=\s*\{[^}]+\}\s*',
        r'\s*zygosity_map\s*=\s*\{[^}]+\}\s*',
        r'\s*segregation_analysis_normp\s*=\s*\{[^}]+\}\s*',
        r'\s*segregation_analysis_map\s*=\s*\{[^}]+\}\s*',
        r'\s*inheritance_map\s*=\s*\{[^}]+\}\s*',
        r'\s*cnv_type_map\s*=\s*\{[^}]+\}\s*',
        r'\s*genomic_test_map\s*=\s*\{[^}]+\}\s*',
        r'\s*genomic_display_map\s*=\s*\{[^}]+\}\s*',
    ]
    
    for pattern in mapping_patterns:
        content = re.sub(pattern, '\n', content, flags=re.DOTALL | re.MULTILINE)
    
    return content

def main():
    """Main function to process the kdk_parser.py file."""
    file_path = r'c:\Users\rosen\Downloads\metamorph\src\metamorph\models\parsers\kdk_parser.py'
    
    print("Processing kdk_parser.py...")
    print("Step 1: Replacing mapping usages...")
    
    # Replace mapping usages
    content = replace_mapping_usages(file_path)
    
    print("Step 2: Removing inline mapping definitions...")
    
    # Remove inline mapping definitions
    content = remove_inline_mappings(content)
    
    # Clean up extra whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully updated kdk_parser.py!")
    print("All inline mappings have been replaced with centralized mapping helper calls.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())