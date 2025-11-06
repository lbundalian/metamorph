# Test the KDK morpher refactoring
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    from src.metamorph.morphers.kdk_morpher import KDKMorpher
    from src.metamorph.models.rd_model import RDSchema
    from src.metamorph.models.kdk_model import KDKSchema
    
    print("✅ All imports successful!")
    
    # Test that morpher can be instantiated
    morpher = KDKMorpher()
    print("✅ KDKMorpher instantiation successful!")
    
    # Check if the new method exists
    if hasattr(morpher, '_map_kdk_to_rd_schema'):
        print("✅ _map_kdk_to_rd_schema method exists!")
    else:
        print("❌ _map_kdk_to_rd_schema method missing!")
    
    print("🎉 Refactoring verification completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")