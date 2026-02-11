"""
Comprehensive test suite for ALL domain config operations
Tests CRUD operations for every key and value in the domain configuration

Run with: python test_all_operations.py
"""
import requests
import json
from typing import Dict, Any, List
from datetime import datetime


API_BASE = "http://localhost:8000"


class ComprehensiveDomainTester:
    """Test all CRUD operations on domain configuration."""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.domain_id = None
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} | {test_name}"
        if message:
            result += f" | {message}"
        self.test_results.append(result)
        print(result)
    
    def create_domain(self, name: str = "Comprehensive Test Domain") -> bool:
        """Create a new test domain."""
        data = {
            "name": name,
            "description": "Testing all operations",
            "version": "1.0.0"
        }
        response = requests.post(f"{API_BASE}/domains", headers=self.headers, json=data)
        if response.status_code in [200, 201]:
            domain = response.json()
            self.domain_id = domain["id"]
            self.log_test("Create Domain", True, f"ID: {self.domain_id}")
            return True
        else:
            self.log_test("Create Domain", False, str(response.json()))
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get current domain configuration."""
        response = requests.get(f"{API_BASE}/domains/{self.domain_id}", headers=self.headers)
        if response.status_code == 200:
            return response.json()["config_json"]
        return None
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update domain configuration."""
        data = {"config_json": config}
        response = requests.put(f"{API_BASE}/domains/{self.domain_id}", headers=self.headers, json=data)
        return response.status_code == 200
    
    # ========================================================================
    # METADATA TESTS (name, description, version)
    # ========================================================================
    
    def test_update_domain_name(self):
        """Test updating domain name."""
        config = self.get_config()
        original_name = config["name"]
        config["name"] = "Updated Domain Name"
        
        success = self.update_config(config)
        updated_config = self.get_config()
        
        if success and updated_config["name"] == "Updated Domain Name":
            self.log_test("Update Domain Name", True)
            # Restore
            config["name"] = original_name
            self.update_config(config)
        else:
            self.log_test("Update Domain Name", False)
    
    def test_update_domain_description(self):
        """Test updating domain description."""
        config = self.get_config()
        config["description"] = "Updated comprehensive description"
        
        success = self.update_config(config)
        updated_config = self.get_config()
        
        self.log_test("Update Domain Description", 
                     success and updated_config["description"] == "Updated comprehensive description")
    
    def test_update_domain_version(self):
        """Test updating domain version."""
        config = self.get_config()
        config["version"] = "2.0.0"
        
        success = self.update_config(config)
        updated_config = self.get_config()
        
        self.log_test("Update Domain Version", 
                     success and updated_config["version"] == "2.0.0")
    
    # ========================================================================
    # ENTITY TESTS
    # ========================================================================
    
    def test_add_entity(self):
        """Test adding a new entity."""
        config = self.get_config()
        new_entity = {
            "name": "TestEntity",
            "type": "TEST_ENTITY",
            "description": "A test entity",
            "attributes": [
                {"name": "test_attr", "description": "Test attribute"}
            ],
            "synonyms": ["TestSynonym"]
        }
        config["entities"].append(new_entity)
        
        success = self.update_config(config)
        updated_config = self.get_config()
        
        entity_added = any(e["type"] == "TEST_ENTITY" for e in updated_config["entities"])
        self.log_test("Add Entity", success and entity_added)
    
    def test_update_entity_name(self):
        """Test updating entity name."""
        config = self.get_config()
        if len(config["entities"]) > 0:
            config["entities"][0]["name"] = "UpdatedEntityName"
            success = self.update_config(config)
            updated_config = self.get_config()
            self.log_test("Update Entity Name", 
                         success and updated_config["entities"][0]["name"] == "UpdatedEntityName")
        else:
            self.log_test("Update Entity Name", False, "No entities to update")
    
    def test_update_entity_type(self):
        """Test updating entity type."""
        config = self.get_config()
        if len(config["entities"]) > 0:
            original_type = config["entities"][0]["type"]
            config["entities"][0]["type"] = "UPDATED_TYPE"
            success = self.update_config(config)
            updated_config = self.get_config()
            
            if success and updated_config["entities"][0]["type"] == "UPDATED_TYPE":
                self.log_test("Update Entity Type", True)
                # Restore
                config["entities"][0]["type"] = original_type
                self.update_config(config)
            else:
                self.log_test("Update Entity Type", False)
        else:
            self.log_test("Update Entity Type", False, "No entities to update")
    
    def test_update_entity_description(self):
        """Test updating entity description."""
        config = self.get_config()
        if len(config["entities"]) > 0:
            config["entities"][0]["description"] = "Updated entity description"
            success = self.update_config(config)
            self.log_test("Update Entity Description", success)
        else:
            self.log_test("Update Entity Description", False, "No entities")
    
    def test_add_entity_attribute(self):
        """Test adding attribute to entity."""
        config = self.get_config()
        if len(config["entities"]) > 0:
            new_attr = {"name": "new_attribute", "description": "A new attribute"}
            config["entities"][0]["attributes"].append(new_attr)
            success = self.update_config(config)
            updated_config = self.get_config()
            
            attr_added = any(a["name"] == "new_attribute" for a in updated_config["entities"][0]["attributes"])
            self.log_test("Add Entity Attribute", success and attr_added)
        else:
            self.log_test("Add Entity Attribute", False, "No entities")
    
    def test_update_entity_attribute_name(self):
        """Test updating entity attribute name."""
        config = self.get_config()
        if len(config["entities"]) > 0 and len(config["entities"][0]["attributes"]) > 0:
            config["entities"][0]["attributes"][0]["name"] = "updated_attr_name"
            success = self.update_config(config)
            self.log_test("Update Entity Attribute Name", success)
        else:
            self.log_test("Update Entity Attribute Name", False, "No attributes")
    
    def test_update_entity_attribute_description(self):
        """Test updating entity attribute description."""
        config = self.get_config()
        if len(config["entities"]) > 0 and len(config["entities"][0]["attributes"]) > 0:
            config["entities"][0]["attributes"][0]["description"] = "Updated attribute description"
            success = self.update_config(config)
            self.log_test("Update Entity Attribute Description", success)
        else:
            self.log_test("Update Entity Attribute Description", False, "No attributes")
    
    def test_remove_entity_attribute(self):
        """Test removing entity attribute."""
        config = self.get_config()
        if len(config["entities"]) > 0 and len(config["entities"][0]["attributes"]) > 0:
            attr_count_before = len(config["entities"][0]["attributes"])
            config["entities"][0]["attributes"].pop()
            success = self.update_config(config)
            updated_config = self.get_config()
            
            attr_count_after = len(updated_config["entities"][0]["attributes"])
            self.log_test("Remove Entity Attribute", success and attr_count_after == attr_count_before - 1)
        else:
            self.log_test("Remove Entity Attribute", False, "No attributes")
    
    def test_add_entity_synonym(self):
        """Test adding synonym to entity."""
        config = self.get_config()
        if len(config["entities"]) > 0:
            config["entities"][0]["synonyms"].append("NewSynonym")
            success = self.update_config(config)
            updated_config = self.get_config()
            
            synonym_added = "NewSynonym" in updated_config["entities"][0]["synonyms"]
            self.log_test("Add Entity Synonym", success and synonym_added)
        else:
            self.log_test("Add Entity Synonym", False, "No entities")
    
    def test_remove_entity_synonym(self):
        """Test removing synonym from entity."""
        config = self.get_config()
        if len(config["entities"]) > 0 and len(config["entities"][0]["synonyms"]) > 0:
            synonym_count_before = len(config["entities"][0]["synonyms"])
            config["entities"][0]["synonyms"].pop()
            success = self.update_config(config)
            updated_config = self.get_config()
            
            synonym_count_after = len(updated_config["entities"][0]["synonyms"])
            self.log_test("Remove Entity Synonym", success and synonym_count_after == synonym_count_before - 1)
        else:
            self.log_test("Remove Entity Synonym", False, "No synonyms")
    
    def test_remove_entity(self):
        """Test removing an entity."""
        config = self.get_config()
        if len(config["entities"]) > 0:
            entity_count_before = len(config["entities"])
            config["entities"].pop()
            success = self.update_config(config)
            updated_config = self.get_config()
            
            entity_count_after = len(updated_config["entities"])
            self.log_test("Remove Entity", success and entity_count_after == entity_count_before - 1)
        else:
            self.log_test("Remove Entity", False, "No entities to remove")
    
    # ========================================================================
    # RELATIONSHIP TESTS
    # ========================================================================
    
    def test_add_relationship(self):
        """Test adding a new relationship."""
        config = self.get_config()
        
        # Ensure we have at least 2 entities
        if len(config["entities"]) < 2:
            config["entities"].extend([
                {
                    "name": "EntityA",
                    "type": "ENTITY_A",
                    "description": "First entity",
                    "attributes": [],
                    "synonyms": []
                },
                {
                    "name": "EntityB",
                    "type": "ENTITY_B",
                    "description": "Second entity",
                    "attributes": [],
                    "synonyms": []
                }
            ])
            self.update_config(config)
            config = self.get_config()
        
        new_relationship = {
            "name": "TEST_RELATIONSHIP",
            "from": config["entities"][0]["type"],
            "to": config["entities"][1]["type"],
            "description": "A test relationship",
            "attributes": [
                {"name": "test_rel_attr", "description": "Test relationship attribute"}
            ]
        }
        config["relationships"].append(new_relationship)
        
        success = self.update_config(config)
        updated_config = self.get_config()
        
        rel_added = any(r["name"] == "TEST_RELATIONSHIP" for r in updated_config["relationships"])
        self.log_test("Add Relationship", success and rel_added)
    
    def test_update_relationship_name(self):
        """Test updating relationship name."""
        config = self.get_config()
        if len(config["relationships"]) > 0:
            config["relationships"][0]["name"] = "UPDATED_RELATIONSHIP"
            success = self.update_config(config)
            updated_config = self.get_config()
            self.log_test("Update Relationship Name", 
                         success and updated_config["relationships"][0]["name"] == "UPDATED_RELATIONSHIP")
        else:
            self.log_test("Update Relationship Name", False, "No relationships")
    
    def test_update_relationship_from(self):
        """Test updating relationship 'from' field."""
        config = self.get_config()
        if len(config["relationships"]) > 0 and len(config["entities"]) > 0:
            config["relationships"][0]["from"] = config["entities"][0]["type"]
            success = self.update_config(config)
            self.log_test("Update Relationship From", success)
        else:
            self.log_test("Update Relationship From", False, "No relationships or entities")
    
    def test_update_relationship_to(self):
        """Test updating relationship 'to' field."""
        config = self.get_config()
        if len(config["relationships"]) > 0 and len(config["entities"]) > 1:
            config["relationships"][0]["to"] = config["entities"][1]["type"]
            success = self.update_config(config)
            self.log_test("Update Relationship To", success)
        else:
            self.log_test("Update Relationship To", False, "No relationships or entities")
    
    def test_update_relationship_description(self):
        """Test updating relationship description."""
        config = self.get_config()
        if len(config["relationships"]) > 0:
            config["relationships"][0]["description"] = "Updated relationship description"
            success = self.update_config(config)
            self.log_test("Update Relationship Description", success)
        else:
            self.log_test("Update Relationship Description", False, "No relationships")
    
    def test_add_relationship_attribute(self):
        """Test adding attribute to relationship."""
        config = self.get_config()
        if len(config["relationships"]) > 0:
            new_attr = {"name": "new_rel_attr", "description": "New relationship attribute"}
            config["relationships"][0]["attributes"].append(new_attr)
            success = self.update_config(config)
            updated_config = self.get_config()
            
            attr_added = any(a["name"] == "new_rel_attr" for a in updated_config["relationships"][0]["attributes"])
            self.log_test("Add Relationship Attribute", success and attr_added)
        else:
            self.log_test("Add Relationship Attribute", False, "No relationships")
    
    def test_update_relationship_attribute_name(self):
        """Test updating relationship attribute name."""
        config = self.get_config()
        if len(config["relationships"]) > 0 and len(config["relationships"][0]["attributes"]) > 0:
            config["relationships"][0]["attributes"][0]["name"] = "updated_rel_attr"
            success = self.update_config(config)
            self.log_test("Update Relationship Attribute Name", success)
        else:
            self.log_test("Update Relationship Attribute Name", False, "No relationship attributes")
    
    def test_update_relationship_attribute_description(self):
        """Test updating relationship attribute description."""
        config = self.get_config()
        if len(config["relationships"]) > 0 and len(config["relationships"][0]["attributes"]) > 0:
            config["relationships"][0]["attributes"][0]["description"] = "Updated rel attr description"
            success = self.update_config(config)
            self.log_test("Update Relationship Attribute Description", success)
        else:
            self.log_test("Update Relationship Attribute Description", False, "No relationship attributes")
    
    def test_remove_relationship_attribute(self):
        """Test removing relationship attribute."""
        config = self.get_config()
        if len(config["relationships"]) > 0 and len(config["relationships"][0]["attributes"]) > 0:
            attr_count_before = len(config["relationships"][0]["attributes"])
            config["relationships"][0]["attributes"].pop()
            success = self.update_config(config)
            updated_config = self.get_config()
            
            attr_count_after = len(updated_config["relationships"][0]["attributes"])
            self.log_test("Remove Relationship Attribute", success and attr_count_after == attr_count_before - 1)
        else:
            self.log_test("Remove Relationship Attribute", False, "No relationship attributes")
    
    def test_remove_relationship(self):
        """Test removing a relationship."""
        config = self.get_config()
        if len(config["relationships"]) > 0:
            rel_count_before = len(config["relationships"])
            config["relationships"].pop()
            success = self.update_config(config)
            updated_config = self.get_config()
            
            rel_count_after = len(updated_config["relationships"])
            self.log_test("Remove Relationship", success and rel_count_after == rel_count_before - 1)
        else:
            self.log_test("Remove Relationship", False, "No relationships to remove")
    
    # ========================================================================
    # EXTRACTION PATTERN TESTS
    # ========================================================================
    
    def test_add_extraction_pattern(self):
        """Test adding extraction pattern."""
        config = self.get_config()
        
        # Ensure we have an entity
        if len(config["entities"]) == 0:
            config["entities"].append({
                "name": "TestEntity",
                "type": "TEST_ENTITY",
                "description": "Test",
                "attributes": [{"name": "test_attr", "description": "Test"}],
                "synonyms": []
            })
            self.update_config(config)
            config = self.get_config()
        
        new_pattern = {
            "pattern": r"\\bTEST\\d+\\b",
            "entity_type": config["entities"][0]["type"],
            "attribute": "test_attr",
            "extract_full_match": True,
            "confidence": 0.85
        }
        config["extraction_patterns"].append(new_pattern)
        
        success = self.update_config(config)
        updated_config = self.get_config()
        
        pattern_added = any(p["pattern"] == r"\\bTEST\\d+\\b" for p in updated_config["extraction_patterns"])
        self.log_test("Add Extraction Pattern", success and pattern_added)
    
    def test_update_extraction_pattern_regex(self):
        """Test updating extraction pattern regex."""
        config = self.get_config()
        if len(config["extraction_patterns"]) > 0:
            config["extraction_patterns"][0]["pattern"] = r"\\bUPDATED\\d+\\b"
            success = self.update_config(config)
            self.log_test("Update Extraction Pattern Regex", success)
        else:
            self.log_test("Update Extraction Pattern Regex", False, "No patterns")
    
    def test_update_extraction_pattern_entity_type(self):
        """Test updating extraction pattern entity_type."""
        config = self.get_config()
        if len(config["extraction_patterns"]) > 0 and len(config["entities"]) > 0:
            config["extraction_patterns"][0]["entity_type"] = config["entities"][0]["type"]
            success = self.update_config(config)
            self.log_test("Update Extraction Pattern Entity Type", success)
        else:
            self.log_test("Update Extraction Pattern Entity Type", False, "No patterns or entities")
    
    def test_update_extraction_pattern_attribute(self):
        """Test updating extraction pattern attribute."""
        config = self.get_config()
        if len(config["extraction_patterns"]) > 0:
            config["extraction_patterns"][0]["attribute"] = "updated_attr"
            success = self.update_config(config)
            self.log_test("Update Extraction Pattern Attribute", success)
        else:
            self.log_test("Update Extraction Pattern Attribute", False, "No patterns")
    
    def test_update_extraction_pattern_extract_full_match(self):
        """Test updating extraction pattern extract_full_match."""
        config = self.get_config()
        if len(config["extraction_patterns"]) > 0:
            current_value = config["extraction_patterns"][0]["extract_full_match"]
            config["extraction_patterns"][0]["extract_full_match"] = not current_value
            success = self.update_config(config)
            self.log_test("Update Extraction Pattern Extract Full Match", success)
        else:
            self.log_test("Update Extraction Pattern Extract Full Match", False, "No patterns")
    
    def test_update_extraction_pattern_confidence(self):
        """Test updating extraction pattern confidence."""
        config = self.get_config()
        if len(config["extraction_patterns"]) > 0:
            config["extraction_patterns"][0]["confidence"] = 0.95
            success = self.update_config(config)
            updated_config = self.get_config()
            self.log_test("Update Extraction Pattern Confidence", 
                         success and updated_config["extraction_patterns"][0]["confidence"] == 0.95)
        else:
            self.log_test("Update Extraction Pattern Confidence", False, "No patterns")
    
    def test_remove_extraction_pattern(self):
        """Test removing extraction pattern."""
        config = self.get_config()
        if len(config["extraction_patterns"]) > 0:
            pattern_count_before = len(config["extraction_patterns"])
            config["extraction_patterns"].pop()
            success = self.update_config(config)
            updated_config = self.get_config()
            
            pattern_count_after = len(updated_config["extraction_patterns"])
            self.log_test("Remove Extraction Pattern", success and pattern_count_after == pattern_count_before - 1)
        else:
            self.log_test("Remove Extraction Pattern", False, "No patterns to remove")
    
    # ========================================================================
    # KEY TERMS TESTS
    # ========================================================================
    
    def test_add_key_term(self):
        """Test adding a key term."""
        config = self.get_config()
        config["key_terms"].append("new_test_term")
        
        success = self.update_config(config)
        updated_config = self.get_config()
        
        term_added = "new_test_term" in updated_config["key_terms"]
        self.log_test("Add Key Term", success and term_added)
    
    def test_update_key_term(self):
        """Test updating a key term."""
        config = self.get_config()
        if len(config["key_terms"]) > 0:
            config["key_terms"][0] = "updated_term"
            success = self.update_config(config)
            updated_config = self.get_config()
            self.log_test("Update Key Term", success and "updated_term" in updated_config["key_terms"])
        else:
            self.log_test("Update Key Term", False, "No key terms")
    
    def test_remove_key_term(self):
        """Test removing a key term."""
        config = self.get_config()
        if len(config["key_terms"]) > 0:
            term_count_before = len(config["key_terms"])
            config["key_terms"].pop()
            success = self.update_config(config)
            updated_config = self.get_config()
            
            term_count_after = len(updated_config["key_terms"])
            self.log_test("Remove Key Term", success and term_count_after == term_count_before - 1)
        else:
            self.log_test("Remove Key Term", False, "No key terms to remove")
    
    def test_replace_all_key_terms(self):
        """Test replacing entire key_terms array."""
        config = self.get_config()
        new_terms = ["term1", "term2", "term3", "term4"]
        config["key_terms"] = new_terms
        
        success = self.update_config(config)
        updated_config = self.get_config()
        
        self.log_test("Replace All Key Terms", success and updated_config["key_terms"] == new_terms)
    
    # ========================================================================
    # RUN ALL TESTS
    # ========================================================================
    
    def run_all_tests(self):
        """Run all test cases."""
        print("\n" + "="*70)
        print("🧪 COMPREHENSIVE DOMAIN CONFIG OPERATION TESTS")
        print("="*70 + "\n")
        
        # Metadata tests
        print("\n📝 METADATA TESTS")
        print("-" * 70)
        self.test_update_domain_name()
        self.test_update_domain_description()
        self.test_update_domain_version()
        
        # Entity tests
        print("\n🏢 ENTITY TESTS")
        print("-" * 70)
        self.test_add_entity()
        self.test_update_entity_name()
        self.test_update_entity_type()
        self.test_update_entity_description()
        self.test_add_entity_attribute()
        self.test_update_entity_attribute_name()
        self.test_update_entity_attribute_description()
        self.test_remove_entity_attribute()
        self.test_add_entity_synonym()
        self.test_remove_entity_synonym()
        self.test_remove_entity()
        
        # Relationship tests
        print("\n🔗 RELATIONSHIP TESTS")
        print("-" * 70)
        self.test_add_relationship()
        self.test_update_relationship_name()
        self.test_update_relationship_from()
        self.test_update_relationship_to()
        self.test_update_relationship_description()
        self.test_add_relationship_attribute()
        self.test_update_relationship_attribute_name()
        self.test_update_relationship_attribute_description()
        self.test_remove_relationship_attribute()
        self.test_remove_relationship()
        
        # Extraction pattern tests
        print("\n🔍 EXTRACTION PATTERN TESTS")
        print("-" * 70)
        self.test_add_extraction_pattern()
        self.test_update_extraction_pattern_regex()
        self.test_update_extraction_pattern_entity_type()
        self.test_update_extraction_pattern_attribute()
        self.test_update_extraction_pattern_extract_full_match()
        self.test_update_extraction_pattern_confidence()
        self.test_remove_extraction_pattern()
        
        # Key terms tests
        print("\n🔑 KEY TERMS TESTS")
        print("-" * 70)
        self.test_add_key_term()
        self.test_update_key_term()
        self.test_remove_key_term()
        self.test_replace_all_key_terms()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if "✅ PASS" in r)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print("="*70 + "\n")
        
        if failed_tests > 0:
            print("Failed Tests:")
            for result in self.test_results:
                if "❌ FAIL" in result:
                    print(f"  {result}")


def main():
    """Main entry point."""
    print("="*70)
    print("🧪 COMPREHENSIVE DOMAIN CONFIG TESTER")
    print("="*70 + "\n")
    
    # Get credentials
    email = input("Enter email: ")
    password = input("Enter password: ")
    
    # Login
    print("\n🔐 Logging in...")
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.json()}")
        return
    
    token = response.json()["access_token"]
    print("✅ Login successful!\n")
    
    # Create tester and run tests
    tester = ComprehensiveDomainTester(token)
    
    if tester.create_domain():
        tester.run_all_tests()
    else:
        print("❌ Failed to create test domain. Exiting.")


if __name__ == "__main__":
    main()
