# metamorph batch processor - clean architecture
# Processes all JSON files in a directory
# Converts each file to *original_name*_converted.json
# Logs errors and provides detailed reporting

import sys
import os
import json
import logging
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
        'success': False,
        'error': None,
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
        
        kdk = KDK(str(input_file))
        logger.info(f"  ✓ KDK object created from {input_file.name}")
        
        # Step 2: Transform to target schema
        transformed_object = morpher.morph(kdk, target_schema)
        logger.info(f"  ✓ Transformed to {target_schema} schema")
        
        # Step 3: Save the result
        save_success = morpher.save(transformed_object, str(output_file))
        if not save_success:
            raise Exception("Failed to save transformed object")
        logger.info(f"  ✓ Saved to {output_filename}")
        
        # Step 4: Validate against API
        is_valid, message = morpher.validate(transformed_object, target_schema)
        result['validation_status'] = 'VALID' if is_valid else 'INVALID'
        result['validation_message'] = message
        
        if is_valid:
            logger.info(f"  ✅ Validation SUCCESS: {message}")
        else:
            logger.warning(f"  ⚠️  Validation WARNING: {message}")
        
        result['success'] = True
        
    except Exception as e:
        error_msg = str(e)
        result['error'] = error_msg
        logger.error(f"  ❌ ERROR processing {input_file.name}: {error_msg}")
    
    return result

def batch_process(input_dir: str, output_dir: str = "output", target_schema: str = "RD") -> None:
    """Process all JSON files in input directory"""
    
    # Setup logging
    logger = setup_logging()
    
    print("🚀 Metamorph - Batch Processor")
    print("=" * 70)
    print(f"📂 Input directory: {input_dir}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🎯 Target schema: {target_schema}")
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
    successful_count = 0
    failed_count = 0
    
    for json_file in json_files:
        result = process_single_file(json_file, output_path, target_schema, morpher, logger)
        results.append(result)
        
        if result['success']:
            successful_count += 1
        else:
            failed_count += 1
    
    # Generate summary report
    print("\n" + "=" * 70)
    print("📋 BATCH PROCESSING SUMMARY")
    print("=" * 70)
    print(f"Total files processed: {len(json_files)}")
    print(f"✅ Successful: {successful_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Success rate: {(successful_count/len(json_files)*100):.1f}%")
    
    if failed_count > 0:
        print(f"\n❌ FAILED FILES:")
        for result in results:
            if not result['success']:
                print(f"   • {result['file']}: {result['error']}")
    
    if successful_count > 0:
        print(f"\n✅ SUCCESSFUL FILES:")
        for result in results:
            if result['success']:
                validation_icon = "✅" if result['validation_status'] == 'VALID' else "⚠️"
                print(f"   • {result['file']} → {Path(result['output_file']).name} {validation_icon}")
    
    # Validation summary
    valid_count = sum(1 for r in results if r.get('validation_status') == 'VALID')
    invalid_count = sum(1 for r in results if r.get('validation_status') == 'INVALID')
    
    if successful_count > 0:
        print(f"\n🔍 VALIDATION SUMMARY:")
        print(f"   ✅ Valid against API: {valid_count}")
        print(f"   ⚠️  Invalid/Warnings: {invalid_count}")
    
    # Log file location
    print(f"\n📝 Detailed logs saved to: logs/batch_process_*.log")
    
    logger.info("Batch processing completed")

def main():
    """Main entry point for batch processing"""
    
    if len(sys.argv) < 2:
        print("Usage: python batch_main.py <input_directory> [output_directory] [target_schema]")
        print("Example: python batch_main.py sample/data/ output/ RD")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    target_schema = sys.argv[3] if len(sys.argv) > 3 else "RD"
    
    try:
        batch_process(input_dir, output_dir, target_schema)
    except KeyboardInterrupt:
        print("\n⚠️  Batch processing interrupted by user")
    except Exception as e:
        print(f"❌ Critical error in batch processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()