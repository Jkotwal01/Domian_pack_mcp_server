// Mock data for domain packs - for UI testing without backend

export const mockDomainPacks = [
  {
    id: "legal-001",
    session_id: "legal-001",
    name: "Legal",
    description: "Legal domain pack for contract analysis and legal document processing",
    version: "1.2.0",
    stats: {
      entities: 8,
      relationships: 12,
      extraction_patterns: 5,
      key_terms: 15
    }
  },
  {
    id: "healthcare-001",
    session_id: "healthcare-001",
    name: "Healthcare",
    description: "Healthcare domain pack for medical records and patient data",
    version: "1.0.0",
    stats: {
      entities: 12,
      relationships: 18,
      extraction_patterns: 8,
      key_terms: 25
    }
  },
  {
    id: "automotive-001",
    session_id: "automotive-001",
    name: "Automotive",
    description: "Automotive domain pack for vehicle specifications and manufacturing",
    version: "2.1.0",
    stats: {
      entities: 15,
      relationships: 22,
      extraction_patterns: 10,
      key_terms: 30
    }
  },
  {
    id: "manufacturing-001",
    session_id: "manufacturing-001",
    name: "Manufacturing",
    description: "Manufacturing domain pack for supply chain and production processes",
    version: "1.5.0",
    stats: {
      entities: 10,
      relationships: 16,
      extraction_patterns: 6,
      key_terms: 20
    }
  }
];

export const mockDomainData = {
  "legal-001": {
    json: {
      name: "Legal",
      description: "Legal domain pack for contract analysis and legal document processing",
      version: "1.2.0",
      entities: [
        {
          name: "Contract",
          type: "LEGAL_DOCUMENT",
          description: "A legally binding agreement between two or more parties",
          attributes: [
            { name: "contract_id", description: "Unique identifier for the contract" },
            { name: "effective_date", description: "Date when the contract becomes effective" },
            { name: "expiration_date", description: "Date when the contract expires" },
            { name: "contract_value", description: "Total monetary value of the contract" }
          ],
          synonyms: ["Agreement", "Legal Agreement", "Binding Contract"]
        },
        {
          name: "Party",
          type: "LEGAL_ENTITY",
          description: "An individual or organization involved in a legal agreement",
          attributes: [
            { name: "party_name", description: "Full legal name of the party" },
            { name: "party_type", description: "Type of party (individual, corporation, etc.)" },
            { name: "jurisdiction", description: "Legal jurisdiction of the party" }
          ],
          synonyms: ["Signatory", "Contracting Party", "Legal Entity"]
        },
        {
          name: "Clause",
          type: "CONTRACT_COMPONENT",
          description: "A specific provision or section within a contract",
          attributes: [
            { name: "clause_number", description: "Section or clause number" },
            { name: "clause_type", description: "Type of clause (termination, liability, etc.)" },
            { name: "clause_text", description: "Full text of the clause" }
          ],
          synonyms: ["Provision", "Section", "Article"]
        },
        {
          name: "Obligation",
          type: "LEGAL_REQUIREMENT",
          description: "A duty or requirement that a party must fulfill",
          attributes: [
            { name: "obligation_description", description: "Description of the obligation" },
            { name: "due_date", description: "Deadline for fulfilling the obligation" },
            { name: "responsible_party", description: "Party responsible for the obligation" }
          ],
          synonyms: ["Duty", "Requirement", "Commitment"]
        }
      ],
      relationships: [
        {
          name: "SIGNS",
          from: "Party",
          to: "Contract",
          description: "A party signs and agrees to a contract",
          attributes: [
            { name: "signature_date", description: "Date when the party signed" }
          ]
        },
        {
          name: "CONTAINS",
          from: "Contract",
          to: "Clause",
          description: "A contract contains one or more clauses",
          attributes: []
        },
        {
          name: "IMPOSES",
          from: "Clause",
          to: "Obligation",
          description: "A clause imposes obligations on parties",
          attributes: []
        },
        {
          name: "BOUND_BY",
          from: "Party",
          to: "Obligation",
          description: "A party is bound by specific obligations",
          attributes: [
            { name: "binding_date", description: "Date when obligation becomes binding" }
          ]
        }
      ],
      extraction_patterns: [
        {
          pattern: "\\b\\d{1,2}/\\d{1,2}/\\d{4}\\b",
          entity_type: "Contract",
          attribute: "effective_date",
          extract_full_match: true,
          confidence: 0.95
        },
        {
          pattern: "\\$[\\d,]+(?:\\.\\d{2})?",
          entity_type: "Contract",
          attribute: "contract_value",
          extract_full_match: true,
          confidence: 0.90
        },
        {
          pattern: "(?i)section\\s+\\d+(?:\\.\\d+)*",
          entity_type: "Clause",
          attribute: "clause_number",
          extract_full_match: true,
          confidence: 0.85
        }
      ],
      key_terms: [
        "contract",
        "agreement",
        "party",
        "signatory",
        "clause",
        "provision",
        "obligation",
        "liability",
        "indemnification",
        "termination",
        "force majeure",
        "jurisdiction",
        "governing law",
        "dispute resolution",
        "confidentiality"
      ]
    },
    yaml: `name: "Legal"
description: "Legal domain pack for contract analysis and legal document processing"
version: "1.2.0"

entities:
  - name: "Contract"
    type: "LEGAL_DOCUMENT"
    description: "A legally binding agreement between two or more parties"
    attributes:
      - name: "contract_id"
        description: "Unique identifier for the contract"
    synonyms:
      - "Agreement"
      - "Legal Agreement"`
  },
  "healthcare-001": {
    json: {
      name: "Healthcare",
      description: "Healthcare domain pack for medical records and patient data",
      version: "1.0.0",
      entities: [
        {
          name: "Patient",
          type: "PERSON",
          description: "An individual receiving medical care",
          attributes: [
            { name: "patient_id", description: "Unique patient identifier" },
            { name: "date_of_birth", description: "Patient's date of birth" },
            { name: "blood_type", description: "Patient's blood type" }
          ],
          synonyms: ["Individual", "Subject"]
        },
        {
          name: "Diagnosis",
          type: "MEDICAL_CONDITION",
          description: "A medical condition identified by a healthcare provider",
          attributes: [
            { name: "diagnosis_code", description: "ICD-10 or similar code" },
            { name: "diagnosis_date", description: "Date of diagnosis" },
            { name: "severity", description: "Severity level of the condition" }
          ],
          synonyms: ["Condition", "Disease", "Illness"]
        }
      ],
      relationships: [
        {
          name: "HAS_DIAGNOSIS",
          from: "Patient",
          to: "Diagnosis",
          description: "A patient has been diagnosed with a condition",
          attributes: []
        }
      ],
      extraction_patterns: [
        {
          pattern: "\\b[A-Z]\\d{2}\\.\\d{1,2}\\b",
          entity_type: "Diagnosis",
          attribute: "diagnosis_code",
          extract_full_match: true,
          confidence: 0.92
        }
      ],
      key_terms: [
        "patient",
        "diagnosis",
        "treatment",
        "medication",
        "prescription",
        "vital signs",
        "medical history"
      ]
    },
    yaml: `name: "Healthcare"
description: "Healthcare domain pack for medical records and patient data"
version: "1.0.0"`
  },
  "automotive-001": {
    json: {
      name: "Automotive",
      description: "Automotive domain pack for vehicle specifications and manufacturing",
      version: "2.1.0",
      entities: [
        {
          name: "Vehicle",
          type: "PRODUCT",
          description: "A motorized transportation device",
          attributes: [
            { name: "vin", description: "Vehicle Identification Number" },
            { name: "make", description: "Vehicle manufacturer" },
            { name: "model", description: "Vehicle model name" },
            { name: "year", description: "Manufacturing year" }
          ],
          synonyms: ["Automobile", "Car", "Motor Vehicle"]
        },
        {
          name: "Component",
          type: "PART",
          description: "A part or component of a vehicle",
          attributes: [
            { name: "part_number", description: "Unique part identifier" },
            { name: "component_name", description: "Name of the component" },
            { name: "manufacturer", description: "Component manufacturer" }
          ],
          synonyms: ["Part", "Assembly", "Module"]
        }
      ],
      relationships: [
        {
          name: "CONTAINS",
          from: "Vehicle",
          to: "Component",
          description: "A vehicle contains various components",
          attributes: [
            { name: "quantity", description: "Number of components" }
          ]
        }
      ],
      extraction_patterns: [
        {
          pattern: "\\b[A-HJ-NPR-Z0-9]{17}\\b",
          entity_type: "Vehicle",
          attribute: "vin",
          extract_full_match: true,
          confidence: 0.98
        }
      ],
      key_terms: [
        "vehicle",
        "engine",
        "transmission",
        "chassis",
        "suspension",
        "braking system",
        "electrical system"
      ]
    },
    yaml: `name: "Automotive"
description: "Automotive domain pack for vehicle specifications and manufacturing"
version: "2.1.0"`
  }
};

export const createMockDomain = (name, description, version = "1.0.0") => {
  const id = `${name.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}`;
  return {
    id,
    session_id: id,
    name,
    description,
    version,
    stats: {
      entities: 0,
      relationships: 0,
      extraction_patterns: 0,
      key_terms: 0
    }
  };
};
