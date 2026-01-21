"""
Example Usage of Domain Pack MCP Server

This script demonstrates how to use the MCP server tools.
"""

import json
from tools import (
    create_session_tool,
    apply_change_tool,
    apply_batch_tool,
    rollback_tool,
    export_domain_pack_tool,
    get_session_info_tool
)


def example_1_create_session():
    """Example 1: Create a new session with minimal domain pack"""
    print("\n" + "="*60)
    print("Example 1: Create Session")
    print("="*60)
    
    minimal_yaml = """
name: Legal
description: Legal and compliance domain
version: 1.0.0
entities:
  - name: Client
    type: CLIENT
    attributes:
      - name
      - contact_info
    synonyms:
      - customer
      - party
key_terms:
  - litigation
  - settlement
"""
    
    result = create_session_tool(minimal_yaml, "yaml")
    print(f"✓ Session created: {result['session_id']}")
    print(f"  Version: {result['version']}")
    
    return result['session_id']


def example_2_add_entity(session_id):
    """Example 2: Add a new entity"""
    print("\n" + "="*60)
    print("Example 2: Add New Entity")
    print("="*60)
    
    operation = {
        "action": "add",
        "path": ["entities"],
        "value": {
            "name": "Attorney",
            "type": "ATTORNEY",
            "attributes": ["name", "bar_number", "specialization"],
            "synonyms": ["lawyer", "counsel", "advocate"]
        }
    }
    
    result = apply_change_tool(
        session_id,
        operation,
        "Added Attorney entity for legal representation"
    )
    
    print(f"✓ Entity added successfully")
    print(f"  New version: {result['version']}")
    print(f"  Changes: {result['diff']['summary']['total_changes']}")


def example_3_update_version(session_id):
    """Example 3: Update version number"""
    print("\n" + "="*60)
    print("Example 3: Update Version")
    print("="*60)
    
    operation = {
        "action": "replace",
        "path": ["version"],
        "value": "2.0.0"
    }
    
    result = apply_change_tool(
        session_id,
        operation,
        "Major version update with new entities"
    )
    
    print(f"✓ Version updated to 2.0.0")
    print(f"  New version: {result['version']}")


def example_4_batch_operations(session_id):
    """Example 4: Apply multiple operations atomically"""
    print("\n" + "="*60)
    print("Example 4: Batch Operations")
    print("="*60)
    
    operations = [
        {
            "action": "merge",
            "path": ["key_terms"],
            "value": ["contract", "arbitration", "mediation"]
        },
        {
            "action": "replace",
            "path": ["description"],
            "value": "Comprehensive legal and compliance domain with enhanced entities"
        }
    ]
    
    result = apply_batch_tool(
        session_id,
        operations,
        "Added key terms and updated description"
    )
    
    print(f"✓ Batch applied successfully")
    print(f"  Operations: {result['operations_count']}")
    print(f"  New version: {result['version']}")


def example_5_rollback(session_id):
    """Example 5: Rollback to previous version"""
    print("\n" + "="*60)
    print("Example 5: Rollback")
    print("="*60)
    
    result = rollback_tool(session_id, 2)
    
    print(f"✓ Rolled back to version 2")
    print(f"  New version: {result['version']}")
    print(f"  Rolled back to: {result['rolled_back_to']}")


def example_6_export(session_id):
    """Example 6: Export domain pack"""
    print("\n" + "="*60)
    print("Example 6: Export Domain Pack")
    print("="*60)
    
    # Export as YAML
    result_yaml = export_domain_pack_tool(session_id, "yaml")
    print(f"✓ Exported as YAML ({len(result_yaml['content'])} bytes)")
    
    # Export as JSON
    result_json = export_domain_pack_tool(session_id, "json")
    print(f"✓ Exported as JSON ({len(result_json['content'])} bytes)")
    
    # Save to file
    with open("exported_domain_pack.yaml", "w") as f:
        f.write(result_yaml['content'])
    print("✓ Saved to exported_domain_pack.yaml")


def example_7_session_info(session_id):
    """Example 7: Get session information"""
    print("\n" + "="*60)
    print("Example 7: Session Information")
    print("="*60)
    
    result = get_session_info_tool(session_id)
    
    print(f"✓ Session ID: {result['session']['session_id']}")
    print(f"  Current version: {result['current_version']}")
    print(f"  File type: {result['session']['file_type']}")
    print(f"  Created: {result['session']['created_at']}")
    print(f"  Total versions: {len(result['versions'])}")


def example_8_complex_workflow(session_id):
    """Example 8: Complex workflow with validation"""
    print("\n" + "="*60)
    print("Example 8: Complex Workflow")
    print("="*60)
    
    # Step 1: Assert current version
    operation1 = {
        "action": "assert",
        "path": ["version"],
        "equals": "2.0.0"
    }
    
    result1 = apply_change_tool(
        session_id,
        operation1,
        "Validated version before update"
    )
    print("✓ Version assertion passed")
    
    # Step 2: Add relationship
    operation2 = {
        "action": "add",
        "path": ["relationships"],
        "value": {
            "name": "REPRESENTS",
            "from": "ATTORNEY",
            "to": "CLIENT",
            "attributes": ["retainer_date", "case_type"],
            "synonyms": ["acts_for", "counsel_for"]
        }
    }
    
    result2 = apply_change_tool(
        session_id,
        operation2,
        "Added REPRESENTS relationship"
    )
    print(f"✓ Relationship added (version {result2['version']})")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Domain Pack MCP Server - Usage Examples")
    print("="*60)
    
    try:
        # Example 1: Create session
        session_id = example_1_create_session()
        
        # Example 2: Add entity
        example_2_add_entity(session_id)
        
        # Example 3: Update version
        example_3_update_version(session_id)
        
        # Example 4: Batch operations
        example_4_batch_operations(session_id)
        
        # Example 5: Rollback
        example_5_rollback(session_id)
        
        # Example 6: Export
        example_6_export(session_id)
        
        # Example 7: Session info
        example_7_session_info(session_id)
        
        # Example 8: Complex workflow
        example_8_complex_workflow(session_id)
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
