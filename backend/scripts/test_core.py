"""
Quick Test Script for Backend

Tests basic functionality without needing full database setup.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core import schema, operations, utils, version_manager

def test_schema_validation():
    """Test schema validation"""
    print("Testing schema validation...")
    
    test_data = {
        "name": "Test Domain",
        "description": "Test description",
        "version": "1.0.0"
    }
    
    try:
        schema.validate_domain_pack(test_data)
        print("✅ Schema validation works!")
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False
    
    return True


def test_operations():
    """Test operations"""
    print("\nTesting operations...")
    
    data = {
        "name": "Test",
        "description": "Test",
        "version": "1.0.0",
        "key_terms": []
    }
    
    try:
        # Test add operation
        operation = {
            "action": "add",
            "path": ["key_terms"],
            "value": "test_term"
        }
        
        new_data = operations.apply_operation(data, operation)
        
        if "test_term" in new_data["key_terms"]:
            print("✅ Operations work!")
            return True
        else:
            print("❌ Operation didn't apply correctly")
            return False
            
    except Exception as e:
        print(f"❌ Operations failed: {e}")
        return False


def test_version_manager():
    """Test version bumping"""
    print("\nTesting version manager...")
    
    data = {"version": "1.0.0"}
    
    try:
        version_manager.bump_version(data, "patch")
        
        if data["version"] == "1.0.1":
            print("✅ Version manager works!")
            return True
        else:
            print(f"❌ Version bump incorrect: {data['version']}")
            return False
            
    except Exception as e:
        print(f"❌ Version manager failed: {e}")
        return False


def test_utils():
    """Test utils"""
    print("\nTesting utils...")
    
    try:
        # Test YAML parsing
        yaml_content = "name: Test\ndescription: Test\nversion: 1.0.0"
        parsed = utils.parse_yaml(yaml_content)
        
        # Test serialization
        serialized = utils.serialize_yaml(parsed)
        
        # Test file type detection
        file_type = utils.detect_file_type("test.yaml")
        
        if file_type == "yaml":
            print("✅ Utils work!")
            return True
        else:
            print(f"❌ File type detection incorrect: {file_type}")
            return False
            
    except Exception as e:
        print(f"❌ Utils failed: {e}")
        return False


def main():
    print("=" * 50)
    print("Backend Core Logic Tests")
    print("=" * 50)
    
    tests = [
        test_schema_validation,
        test_operations,
        test_version_manager,
        test_utils
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 50)
    
    if all(results):
        print("\n✅ All core logic tests passed!")
        print("\nNext steps:")
        print("1. Initialize database: python scripts/init_db.py")
        print("2. Run server: uvicorn app.main:app --reload")
        print("3. Test API: http://localhost:8000/docs")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
