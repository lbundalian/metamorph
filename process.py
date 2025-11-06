# metamorph batch processor - clean architecture
# Processes all JSON files in a directory
# Converts each file to *original_name*_converted.json
# Logs errors and provides detailed reporting

import sys
import os
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime

# add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.metamorph.models.kdk import KDK
from src.metamorph.morphers.kdk_morpher import KDKMorpher

def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """Setup logging for batch processing"""
    Path(log_dir).mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(log_dir) / f"batch_process_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    return logging.getLogger(__name__)

def process_single_file(input_file: Path, output_dir: Path, target_schema: str, morpher: KDKMorpher, logger: logging.Logger) -> dict:
    """Process a single JSON file and return result summary"""
    result = {
        'file': input_file.name,
        'file_path': str(input_file),
        'success': False,
        'error': None,
        'error_type': None,
        'error_stage': None,
        'traceback': None,
        'output_file': None,
        'validation_status': None,
        'validation_message': None
    }
    
    try:
        # Generate output filename: original_name_converted.json
        output_filename = f"{input_file.stem}_converted.json"
        output_file = output_dir / output_filename
        result['output_file'] = str(output_file)
        
        logger.info(f"Processing {input_file.name}...")
        
        # Step 1: Create KDK object
        try:
            result['error_stage'] = 'KDK_PARSING'
            kdk = KDK(str(input_file))
            logger.info(f"  KDK object created from {input_file.name}")
        except Exception as e:
            result['error_type'] = 'PARSING_ERROR'
            raise e
        
        # Step 2: Transform to target schema
        try:
            result['error_stage'] = 'TRANSFORMATION'
            transformed_object = morpher.morph(kdk, target_schema)
            logger.info(f"  Transformed to {target_schema} schema")
        except Exception as e:
            result['error_type'] = 'TRANSFORMATION_ERROR'
            raise e
        
        # Step 3: Save the result
        try:
            result['error_stage'] = 'SAVING'
            save_success = morpher.save(transformed_object, str(output_file))
            if not save_success:
                raise Exception("Failed to save transformed object")
            logger.info(f"  Saved to {output_filename}")
        except Exception as e:
            result['error_type'] = 'SAVE_ERROR'
            raise e
        
        # Step 4: Validate against API
        try:
            result['error_stage'] = 'VALIDATION'
            is_valid, message = morpher.validate(transformed_object, target_schema)
            result['validation_status'] = 'VALID' if is_valid else 'INVALID'
            result['validation_message'] = message
            
            if is_valid:
                logger.info(f"  Validation SUCCESS: {message}")
            else:
                logger.warning(f"  Validation WARNING: {message}")
        except Exception as e:
            result['error_type'] = 'VALIDATION_ERROR'
            # Don't fail the entire process for validation errors
            result['validation_status'] = 'ERROR'
            result['validation_message'] = str(e)
            logger.warning(f"  Validation ERROR: {e}")
        
        result['success'] = True
        

        # Step 5: Add metadata
        try:
            submission_data = morpher._add_metadata(transformed_object, kdk)
        except Exception as e:
            raise Exception(f"Metadata addition failed: {e}")

    except Exception as e:
        error_msg = str(e)
        result['error'] = error_msg
        result['traceback'] = traceback.format_exc()
        logger.error(f"  ERROR processing {input_file.name}: {error_msg}")
    
    return result

def display_failure_analysis(failed_results: list) -> None:
    """Display detailed analysis of failed files"""
    if not failed_results:
        return
    
    print("\n" + "=" * 70)
    print("FAILURE ANALYSIS")
    print("=" * 70)
    
    # Group failures by error type
    error_groups = {}
    for result in failed_results:
        error_type = result.get('error_type', 'UNKNOWN_ERROR')
        if error_type not in error_groups:
            error_groups[error_type] = []
        error_groups[error_type].append(result)
    
    # Display statistics
    print(f"Total failed files: {len(failed_results)}")
    print(f"Error types found: {len(error_groups)}")
    print()
    
    # Show error type breakdown
    print("ERROR TYPE BREAKDOWN:")
    print("-" * 40)
    for error_type, failures in error_groups.items():
        percentage = (len(failures) / len(failed_results)) * 100
        print(f"  {error_type}: {len(failures)} files ({percentage:.1f}%)")
    print()
    
    # Detailed failure information
    for error_type, failures in error_groups.items():
        print(f"DETAILED {error_type} FAILURES:")
        print("-" * 50)
        
        for i, failure in enumerate(failures, 1):
            print(f"{i}. File: {failure['file']}")
            print(f"   Path: {failure['file_path']}")
            print(f"   Stage: {failure.get('error_stage', 'Unknown')}")
            print(f"   Error: {failure['error']}")
            
            # Show first few lines of traceback for debugging
            if failure.get('traceback'):
                traceback_lines = failure['traceback'].split('\n')
                relevant_lines = [line for line in traceback_lines if 
                                line.strip() and not line.startswith('  File') or 
                                'metamorph' in line][:3]
                if relevant_lines:
                    print(f"   Debug: {'; '.join(relevant_lines)}")
            print()
        
        # Common error patterns
        if len(failures) > 1:
            print(f"COMMON PATTERNS FOR {error_type}:")
            print("-" * 30)
            
            # Analyze common error messages
            error_messages = [f['error'] for f in failures]
            unique_errors = list(set(error_messages))
            
            for unique_error in unique_errors[:5]:  # Show top 5 unique errors
                count = error_messages.count(unique_error)
                if count > 1:
                    print(f"  '{unique_error}' - {count} files")
            print()

def save_failure_report(failed_results: list, output_dir: str) -> None:
    """Save detailed failure report to JSON file"""
    if not failed_results:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Path(output_dir) / f"failure_report_{timestamp}.json"
    
    # Create detailed report
    report = {
        "timestamp": timestamp,
        "total_failures": len(failed_results),
        "summary": {},
        "failures": failed_results
    }
    
    # Add summary statistics
    error_types = {}
    for failure in failed_results:
        error_type = failure.get('error_type', 'UNKNOWN_ERROR')
        error_types[error_type] = error_types.get(error_type, 0) + 1
    
    report["summary"] = {
        "error_types": error_types,
        "most_common_error": max(error_types.items(), key=lambda x: x[1]) if error_types else None
    }
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Detailed failure report saved to: {report_file}")
    except Exception as e:
        print(f"Warning: Could not save failure report: {e}")

def batch_process(input_dir: str, output_dir: str = "output", target_schema: str = "RD") -> None:
    """Process all JSON files in input directory"""
    
    # Setup logging
    logger = setup_logging()
    
    print("Metamorph - Batch Processor")
    print("=" * 70)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Target schema: {target_schema}")
    print("=" * 70)
    
    # Validate input directory
    input_path = Path(input_dir)
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return
    
    if not input_path.is_dir():
        logger.error(f"Input path is not a directory: {input_dir}")
        return
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    logger.info(f"Output directory created/verified: {output_dir}")
    
    # Find all JSON files
    json_files = list(input_path.glob("*.json"))
    if not json_files:
        logger.warning(f"No JSON files found in {input_dir}")
        return
    
    logger.info(f"Found {len(json_files)} JSON files to process")
    
    # Initialize morpher
    morpher = KDKMorpher()
    
    # Process files
    results = []
    successful_results = []
    failed_results = []
    
    for json_file in json_files:
        result = process_single_file(json_file, output_path, target_schema, morpher, logger)
        results.append(result)
        
        if result['success']:
            successful_results.append(result)
        else:
            failed_results.append(result)
    
    # Generate summary report
    print("\n" + "=" * 70)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 70)
    print(f"Total files processed: {len(json_files)}")
    print(f"Successful: {len(successful_results)}")
    print(f"Failed: {len(failed_results)}")
    print(f"Success rate: {(len(successful_results)/len(json_files)*100):.1f}%")
    
    if successful_results:
        print(f"\nSUCCESSFUL FILES:")
        for result in successful_results:
            validation_icon = "VALID" if result['validation_status'] == 'VALID' else "WARNING"
            print(f"   {result['file']} -> {Path(result['output_file']).name} [{validation_icon}]")
    
    # Validation summary
    valid_count = sum(1 for r in successful_results if r.get('validation_status') == 'VALID')
    invalid_count = sum(1 for r in successful_results if r.get('validation_status') == 'INVALID')
    
    if successful_results:
        print(f"\nVALIDATION SUMMARY:")
        print(f"   Valid against API: {valid_count}")
        print(f"   Invalid/Warnings: {invalid_count}")
    
    # Display detailed failure analysis
    if failed_results:
        display_failure_analysis(failed_results)
        save_failure_report(failed_results, output_dir)
    
    # Log file location
    print(f"\nDetailed logs saved to: logs/batch_process_*.log")
    
    logger.info("Batch processing completed")

def main():
    """Main entry point for batch processing"""
    
    if len(sys.argv) < 2:
        print("Usage: python process.py <input_directory> [output_directory] [target_schema]")
        print("Example: python process.py sample/data/ output/ RD")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    target_schema = sys.argv[3] if len(sys.argv) > 3 else "RD"
    
    try:
        batch_process(input_dir, output_dir, target_schema)
    except KeyboardInterrupt:
        print("\nBatch processing interrupted by user")
    except Exception as e:
        print(f"Critical error in batch processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()