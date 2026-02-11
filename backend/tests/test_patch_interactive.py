"""
Interactive test script for Domain Pack Patch Operations
Run with: python test_patch_interactive.py
"""
import requests
import json
from typing import Dict, Any

API_BASE = "http://localhost:8000"

class DomainPatchTester:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.domain_id = None
    
    def create_domain(self, name: str = "Test Domain") -> Dict[str, Any]:
        """Create a new domain for testing."""
        data = {
            "name": name,
            "description": "Testing patch operations",
            "version": "1.0.0"
        }
        response = requests.post(f"{API_BASE}/domains", headers=self.headers, json=data)
        if response.status_code in [200, 201]:
            domain = response.json()
            self.domain_id = domain["id"]
            print(f"✅ Created domain: {domain['name']} (ID: {self.domain_id})")
            return domain
        else:
            print(f"❌ Error creating domain: {response.json()}")
            return None
    
    def get_domain(self) -> Dict[str, Any]:
        """Get current domain configuration."""
        if not self.domain_id:
            print("❌ No domain ID set. Create a domain first.")
            return None
        
        response = requests.get(f"{API_BASE}/domains/{self.domain_id}", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error getting domain: {response.json()}")
            return None
    
    def update_domain(self, config_json: Dict[str, Any]) -> Dict[str, Any]:
        """Update domain with new configuration."""
        if not self.domain_id:
            print("❌ No domain ID set. Create a domain first.")
            return None
        
        data = {"config_json": config_json}
        response = requests.put(f"{API_BASE}/domains/{self.domain_id}", headers=self.headers, json=data)
        if response.status_code == 200:
            print("✅ Domain updated successfully")
            return response.json()
        else:
            print(f"❌ Error updating domain: {response.json()}")
            return None
    
    def print_config(self, config: Dict[str, Any]):
        """Pretty print configuration."""
        print("\n" + "="*60)
        print("📋 Current Configuration")
        print("="*60)
        print(f"Entities: {len(config.get('entities', []))}")
        for i, entity in enumerate(config.get('entities', [])):
            print(f"  {i}. {entity['name']} ({entity['type']})")
        
        print(f"\nRelationships: {len(config.get('relationships', []))}")
        for i, rel in enumerate(config.get('relationships', [])):
            print(f"  {i}. {rel['name']}: {rel['from']} -> {rel['to']}")
        
        print(f"\nExtraction Patterns: {len(config.get('extraction_patterns', []))}")
        print(f"Key Terms: {len(config.get('key_terms', []))}")
        print("="*60 + "\n")
    
    def test_add_entity(self):
        """Test adding a new entity."""
        print("\n🧪 Test: Add Entity")
        domain = self.get_domain()
        if not domain:
            return
        
        config = domain["config_json"]
        
        # Add Patient entity
        config["entities"].append({
            "name": "Patient",
            "type": "PATIENT",
            "description": "A patient in the healthcare system",
            "attributes": [
                {"name": "name", "description": "Patient full name"},
                {"name": "age", "description": "Patient age"}
            ],
            "synonyms": ["Individual", "Person"]
        })
        
        updated = self.update_domain(config)
        if updated:
            self.print_config(updated["config_json"])
            print(f"Entity Count: {updated['entity_count']}")
    
    def test_add_relationship(self):
        """Test adding a relationship."""
        print("\n🧪 Test: Add Relationship")
        domain = self.get_domain()
        if not domain:
            return
        
        config = domain["config_json"]
        
        # First, ensure we have entities
        if len(config.get("entities", [])) < 2:
            print("⚠️  Need at least 2 entities. Adding them first...")
            config["entities"].extend([
                {
                    "name": "Patient",
                    "type": "PATIENT",
                    "description": "A patient",
                    "attributes": [],
                    "synonyms": []
                },
                {
                    "name": "Doctor",
                    "type": "DOCTOR",
                    "description": "A doctor",
                    "attributes": [],
                    "synonyms": []
                }
            ])
        
        # Add relationship
        config["relationships"].append({
            "name": "TREATED_BY",
            "from": "PATIENT",
            "to": "DOCTOR",
            "description": "Patient is treated by a doctor",
            "attributes": [
                {"name": "date", "description": "Treatment date"}
            ]
        })
        
        updated = self.update_domain(config)
        if updated:
            self.print_config(updated["config_json"])
            print(f"Relationship Count: {updated['relationship_count']}")
    
    def test_update_entity(self):
        """Test updating an entity."""
        print("\n🧪 Test: Update Entity Description")
        domain = self.get_domain()
        if not domain:
            return
        
        config = domain["config_json"]
        
        if len(config.get("entities", [])) == 0:
            print("⚠️  No entities to update. Add one first.")
            return
        
        # Update first entity's description
        config["entities"][0]["description"] = "Updated: A person receiving medical care"
        
        updated = self.update_domain(config)
        if updated:
            self.print_config(updated["config_json"])
    
    def test_remove_entity(self):
        """Test removing an entity."""
        print("\n🧪 Test: Remove Entity")
        domain = self.get_domain()
        if not domain:
            return
        
        config = domain["config_json"]
        
        if len(config.get("entities", [])) == 0:
            print("⚠️  No entities to remove.")
            return
        
        removed = config["entities"].pop(0)
        print(f"Removing: {removed['name']}")
        
        updated = self.update_domain(config)
        if updated:
            self.print_config(updated["config_json"])
            print(f"Entity Count: {updated['entity_count']}")


def main():
    print("="*60)
    print("🧪 Domain Pack Patch Operations Tester")
    print("="*60)
    
    # Get token
    email = input("Enter email: ")
    password = input("Enter password: ")
    
    # Login
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.json()}")
        return
    
    token = response.json()["access_token"]
    print("✅ Login successful!\n")
    
    # Create tester
    tester = DomainPatchTester(token)
    
    # Create domain
    tester.create_domain("Healthcare Test Domain")
    
    # Run tests
    while True:
        print("\n" + "="*60)
        print("Choose a test:")
        print("1. Add Entity")
        print("2. Add Relationship")
        print("3. Update Entity")
        print("4. Remove Entity")
        print("5. View Current Config")
        print("6. Exit")
        print("="*60)
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == "1":
            tester.test_add_entity()
        elif choice == "2":
            tester.test_add_relationship()
        elif choice == "3":
            tester.test_update_entity()
        elif choice == "4":
            tester.test_remove_entity()
        elif choice == "5":
            domain = tester.get_domain()
            if domain:
                tester.print_config(domain["config_json"])
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
