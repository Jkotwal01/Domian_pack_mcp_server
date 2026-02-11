# Frontend-Backend Integration Guide

## ✅ What's Been Updated

The frontend has been fully connected to the backend API with all routes properly configured.

### 🔧 Changes Made

#### 1. **API Service Updated** (`src/services/api.js`)
- ✅ Removed incorrect `/api/v1` prefix
- ✅ Updated all endpoints to match backend routes:
  - `/auth/login` → Login
  - `/auth/signup` → Registration  
  - `/auth/me` → Get current user
  - `/domains` → Domain CRUD operations
- ✅ Added helper functions for all domain operations:
  - Entities (add, update, delete)
  - Relationships (add, update, delete)
  - Extraction Patterns (add, update, delete)
  - Key Terms (add, delete)
- ✅ Commented out chatbot functionality for later implementation
- ✅ Added backward compatibility with deprecated session functions

#### 2. **Environment Configuration**
- Backend URL: `http://localhost:8000` (configured in `.env`)
- No API version prefix needed

---

## 📋 Available API Functions

### Authentication
```javascript
import { login, register, getCurrentUser, logout } from './services/api';

// Login
const response = await login('user@example.com', 'password');
// Returns: { access_token, token_type, user }

// Register
await register({ email: 'user@example.com', password: 'password' });

// Get current user
const user = await getCurrentUser();

// Logout
logout();
```

### Domain Management
```javascript
import { 
  createDomain, 
  getDomain, 
  listDomains, 
  updateDomain, 
  deleteDomain 
} from './services/api';

// Create domain
const domain = await createDomain('Healthcare Domain', 'Medical entities');
// Returns: { id, name, description, version, config_json, ... }

// Get domain
const domain = await getDomain(domainId);

// List all domains
const domains = await listDomains();

// Update domain
const updated = await updateDomain(domainId, configJson);

// Delete domain
await deleteDomain(domainId);
```

### Entity Operations
```javascript
import { addEntity, updateEntity, deleteEntity } from './services/api';

// Add entity
const entity = {
  name: 'Patient',
  type: 'PATIENT',
  description: 'A patient',
  attributes: [
    { name: 'name', description: 'Patient name' }
  ],
  synonyms: ['Individual']
};
await addEntity(domainId, entity);

// Update entity
await updateEntity(domainId, entityIndex, updatedEntity);

// Delete entity
await deleteEntity(domainId, entityIndex);
```

### Relationship Operations
```javascript
import { addRelationship, updateRelationship, deleteRelationship } from './services/api';

// Add relationship
const relationship = {
  name: 'TREATED_BY',
  from: 'PATIENT',
  to: 'DOCTOR',
  description: 'Patient treated by doctor',
  attributes: [
    { name: 'date', description: 'Treatment date' }
  ]
};
await addRelationship(domainId, relationship);

// Update relationship
await updateRelationship(domainId, relationshipIndex, updatedRelationship);

// Delete relationship
await deleteRelationship(domainId, relationshipIndex);
```

### Extraction Pattern Operations
```javascript
import { addExtractionPattern, updateExtractionPattern, deleteExtractionPattern } from './services/api';

// Add pattern
const pattern = {
  pattern: '\\bDr\\. [A-Z][a-z]+\\b',
  entity_type: 'DOCTOR',
  attribute: 'name',
  extract_full_match: true,
  confidence: 0.9
};
await addExtractionPattern(domainId, pattern);

// Update pattern
await updateExtractionPattern(domainId, patternIndex, updatedPattern);

// Delete pattern
await deleteExtractionPattern(domainId, patternIndex);
```

### Key Terms Operations
```javascript
import { addKeyTerm, deleteKeyTerm } from './services/api';

// Add key term
await addKeyTerm(domainId, 'diagnosis');

// Delete key term
await deleteKeyTerm(domainId, termIndex);
```

### Health & Stats
```javascript
import { checkHealth, getStats } from './services/api';

// Check backend health
const health = await checkHealth();
// Returns: { status: 'healthy' }

// Get LLM stats
const stats = await getStats();
// Returns: { llm_monitoring: { total_calls, average_response_time, ... } }
```

---

## 🚫 Chatbot Functions (Commented Out)

The following chatbot functions are commented out and will be implemented later:

```javascript
// createChatSession(domainConfigId)
// sendChatMessage(sessionId, message)
// getChatHistory(sessionId)
// closeChatSession(sessionId)
```

To use them later, uncomment the functions in `src/services/api.js`.

---

## 🔄 Backend Routes Reference

| Frontend Function | Backend Endpoint | Method | Description |
|------------------|------------------|--------|-------------|
| `login()` | `/auth/login` | POST | User login |
| `register()` | `/auth/signup` | POST | User registration |
| `getCurrentUser()` | `/auth/me` | GET | Get current user |
| `createDomain()` | `/domains` | POST | Create domain |
| `listDomains()` | `/domains` | GET | List all domains |
| `getDomain(id)` | `/domains/{id}` | GET | Get domain by ID |
| `updateDomain(id)` | `/domains/{id}` | PUT | Update domain |
| `deleteDomain(id)` | `/domains/{id}` | DELETE | Delete domain |
| `checkHealth()` | `/health` | GET | Health check |
| `getStats()` | `/stats` | GET | LLM monitoring stats |

---

## 🚀 How to Run

### 1. Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Access Application
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 🧪 Testing the Connection

### Test 1: Health Check
```javascript
import { checkHealth } from './services/api';

const health = await checkHealth();
console.log(health); // { status: 'healthy' }
```

### Test 2: Authentication
```javascript
import { register, login } from './services/api';

// Register
await register({ email: 'test@example.com', password: 'test123' });

// Login
const response = await login('test@example.com', 'test123');
console.log(response.access_token); // JWT token
```

### Test 3: Create Domain
```javascript
import { createDomain, getDomain } from './services/api';

const domain = await createDomain('Test Domain', 'Testing connection');
console.log(domain.id);

const retrieved = await getDomain(domain.id);
console.log(retrieved.config_json);
```

---

## 📝 Migration Notes

### Old API (Deprecated)
```javascript
// ❌ Old way (deprecated)
createSession(content, fileType, metadata)
getSession(sessionId)
deleteSession(sessionId)
```

### New API (Current)
```javascript
// ✅ New way
createDomain(name, description, version)
getDomain(domainId)
deleteDomain(domainId)
```

The old functions still work but will show deprecation warnings in the console.

---

## 🐛 Troubleshooting

### Issue: CORS Errors
**Solution**: Make sure backend CORS is configured for `http://localhost:5173`
```python
# backend/app/main.py
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Issue: 401 Unauthorized
**Solution**: Check if token is stored in localStorage
```javascript
const token = localStorage.getItem('token');
console.log(token); // Should show JWT token
```

### Issue: Network Error
**Solution**: Verify backend is running
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

## 🎯 Next Steps

1. ✅ Frontend-Backend connection complete
2. ✅ All CRUD operations working
3. ✅ Chatbot API commented out
4. ⏳ Implement chatbot UI (when OpenAI quota available)
5. ⏳ Add real-time updates
6. ⏳ Add export functionality

---

## 📚 Additional Resources

- Backend API Docs: `http://localhost:8000/docs`
- Test Scripts: `backend/test_all_operations.py`
- Patch Testing Guide: `backend/PATCH_TESTING_GUIDE.md`
