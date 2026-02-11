import { useState } from 'react';

/**
 * Custom hook for managing domain pack data and CRUD operations
 * Centralizes all data management logic for entities, relationships, patterns, and key terms
 */
export default function useDomainData(initialData) {
  const [domainData, setDomainData] = useState(initialData || {
    entities: [],
    relationships: [],
    extraction_patterns: [],
    key_terms: []
  });

  // Entity handlers
  const handleAddEntity = (entity) => {
    setDomainData({
      ...domainData,
      entities: [...(domainData.entities || []), entity]
    });
  };

  const handleEditEntity = (index, updatedEntity) => {
    const newEntities = [...domainData.entities];
    newEntities[index] = updatedEntity;
    setDomainData({ ...domainData, entities: newEntities });
  };

  const handleDeleteEntity = (index) => {
    if (confirm('Are you sure you want to delete this entity?')) {
      const newEntities = domainData.entities.filter((_, i) => i !== index);
      setDomainData({ ...domainData, entities: newEntities });
    }
  };

  const handleDuplicateEntity = (index) => {
    const entityToDuplicate = domainData.entities[index];
    const duplicatedEntity = {
      ...entityToDuplicate,
      name: `${entityToDuplicate.name} (Copy)`
    };
    setDomainData({
      ...domainData,
      entities: [...domainData.entities, duplicatedEntity]
    });
  };

  // Relationship handlers
  const handleAddRelationship = (relationship) => {
    setDomainData({
      ...domainData,
      relationships: [...(domainData.relationships || []), relationship]
    });
  };

  const handleEditRelationship = (index, updatedRelationship) => {
    const newRelationships = [...domainData.relationships];
    newRelationships[index] = updatedRelationship;
    setDomainData({ ...domainData, relationships: newRelationships });
  };

  const handleDeleteRelationship = (index) => {
    if (confirm('Are you sure you want to delete this relationship?')) {
      const newRelationships = domainData.relationships.filter((_, i) => i !== index);
      setDomainData({ ...domainData, relationships: newRelationships });
    }
  };

  // Extraction Pattern handlers
  const handleAddPattern = (pattern) => {
    setDomainData({
      ...domainData,
      extraction_patterns: [...(domainData.extraction_patterns || []), pattern]
    });
  };

  const handleEditPattern = (index, updatedPattern) => {
    const newPatterns = [...domainData.extraction_patterns];
    newPatterns[index] = updatedPattern;
    setDomainData({ ...domainData, extraction_patterns: newPatterns });
  };

  const handleDeletePattern = (index) => {
    if (confirm('Are you sure you want to delete this extraction pattern?')) {
      const newPatterns = domainData.extraction_patterns.filter((_, i) => i !== index);
      setDomainData({ ...domainData, extraction_patterns: newPatterns });
    }
  };

  // Key Term handlers
  const handleAddTerm = (term) => {
    if (term && !domainData.key_terms?.includes(term)) {
      setDomainData({
        ...domainData,
        key_terms: [...(domainData.key_terms || []), term]
      });
    }
  };

  const handleDeleteTerm = (index) => {
    const newTerms = domainData.key_terms.filter((_, i) => i !== index);
    setDomainData({ ...domainData, key_terms: newTerms });
  };

  return {
    domainData,
    setDomainData,
    // Entity operations
    handleAddEntity,
    handleEditEntity,
    handleDeleteEntity,
    handleDuplicateEntity,
    // Relationship operations
    handleAddRelationship,
    handleEditRelationship,
    handleDeleteRelationship,
    // Pattern operations
    handleAddPattern,
    handleEditPattern,
    handleDeletePattern,
    // Key Term operations
    handleAddTerm,
    handleDeleteTerm
  };
}
