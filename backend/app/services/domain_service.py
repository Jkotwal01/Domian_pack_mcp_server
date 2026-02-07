import uuid
import yaml
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc

from app.db.models import DomainPack, Entity, ExtractionPattern, KeyTerm, Relationship, VersionHistory
from app.logic.schema import validate_domain_pack

class DomainService:
    def __init__(self, db: DBSession):
        self.db = db

    def get_full_domain_pack(self, domain_id: uuid.UUID) -> Dict[str, Any]:
        """Reconstruct the full Domain Pack JSON from granular tables."""
        domain = self.db.query(DomainPack).filter(DomainPack.id == domain_id).first()
        if not domain:
            raise ValueError(f"Domain pack not found: {domain_id}")

        result = {
            "name": domain.name,
            "description": domain.description,
            "version": domain.version,
            "entities": [],
            "extraction_patterns": [],
            "key_terms": [],
            "relationships": []
        }

        for entity in domain.entities:
            result["entities"].append({
                "name": entity.name,
                "type": entity.type,
                "attributes": entity.attributes,
                "synonyms": entity.synonyms or []
            })

        for p in domain.patterns:
            result["extraction_patterns"].append({
                "pattern": p.pattern,
                "entity_type": p.entity_type,
                "attribute": p.attribute,
                "confidence": p.confidence / 100.0 if p.confidence is not None else 0.0
            })

        for term in domain.terms:
            result["key_terms"].append(term.term)

        for rel in domain.relationships:
            result["relationships"].append({
                "name": rel.name,
                "from": rel.from_entity,
                "to": rel.to_entity,
                "attributes": rel.attributes or [],
                "synonyms": rel.synonyms or []
            })

        # Note: In Phase 1, we focus on these main components. 
        # Other schema sections can be added as needed or stored in a JSONB 'metadata' field if sparse.
        
        return result

    def sync_domain_from_content(self, domain_id: uuid.UUID, content: Dict[str, Any], reason: str = "Manual Update"):
        """Sync granular tables from a full JSON/YAML content object."""
        validate_domain_pack(content)
        
        domain = self.db.query(DomainPack).filter(DomainPack.id == domain_id).first()
        if not domain:
            raise ValueError(f"Domain pack not found: {domain_id}")

        # Update metadata
        domain.name = content.get("name", domain.name)
        domain.description = content.get("description", domain.description)
        domain.version = content.get("version", domain.version)

        # Clear existing granular records
        self.db.query(Entity).filter(Entity.domain_id == domain_id).delete()
        self.db.query(ExtractionPattern).filter(ExtractionPattern.domain_id == domain_id).delete()
        self.db.query(KeyTerm).filter(KeyTerm.domain_id == domain_id).delete()
        self.db.query(Relationship).filter(Relationship.domain_id == domain_id).delete()

        # Insert new Entities
        for e_data in content.get("entities", []):
            db_entity = Entity(
                domain_id=domain_id,
                name=e_data["name"],
                type=e_data["type"],
                attributes=e_data["attributes"],
                synonyms=e_data.get("synonyms", [])
            )
            self.db.add(db_entity)

        # Insert new Patterns
        for p_data in content.get("extraction_patterns", []):
            db_p = ExtractionPattern(
                domain_id=domain_id,
                pattern=p_data["pattern"],
                entity_type=p_data["entity_type"],
                attribute=p_data["attribute"],
                confidence=int(p_data["confidence"] * 100) if "confidence" in p_data else None
            )
            self.db.add(db_p)

        # Insert new Key Terms
        for term in content.get("key_terms", []):
            db_term = KeyTerm(domain_id=domain_id, term=term)
            self.db.add(db_term)

        # Insert new Relationships
        for r_data in content.get("relationships", []):
            db_rel = Relationship(
                domain_id=domain_id,
                name=r_data["name"],
                from_entity=r_data["from"],
                to_entity=r_data["to"],
                attributes=r_data.get("attributes", []),
                synonyms=r_data.get("synonyms", [])
            )
            self.db.add(db_rel)

        # Create Version Snapshot
        # Get next version number
        latest_v = self.db.query(VersionHistory).filter(VersionHistory.domain_id == domain_id).order_by(desc(VersionHistory.version_number)).first()
        new_v_num = (latest_v.version_number + 1) if latest_v else 1
        
        v_history = VersionHistory(
            domain_id=domain_id,
            version_number=new_v_num,
            content=content
        )
        self.db.add(v_history)

        self.db.commit()
        return domain

    def list_domain_packs(self) -> List[DomainPack]:
        return self.db.query(DomainPack).order_by(desc(DomainPack.updated_at)).all()

    def create_domain_pack(self, name: str, description: str, is_template: bool = False) -> DomainPack:
        domain = DomainPack(
            id=uuid.uuid4(),
            name=name,
            description=description,
            is_template=1 if is_template else 0
        )
        self.db.add(domain)
        self.db.commit()
        self.db.refresh(domain)
        return domain

