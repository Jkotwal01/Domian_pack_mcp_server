/**
 * API service for Domain Pack Backend
 * Updated to match actual backend routes
 */

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

/**
 * Get the authentication token from localStorage
 */
function getToken() {
  return localStorage.getItem('token');
}

/**
 * Handle API responses
 * Automatically handles 401 Unauthorized by clearing local storage
 */
async function handleResponse(response) {
  if (response.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  if (response.status === 204) {
    return true;
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `HTTP error! status: ${response.status}`);
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return await response.json();
  }
  
  return await response.text();
}

/**
 * Internal fetch wrapper to include shared headers
 */
async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (headers['Content-Type'] === undefined) {
    delete headers['Content-Type'];
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Ensure endpoint starts with a slash and BACKEND_URL doesn't end with one
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const cleanBaseUrl = BACKEND_URL.endsWith('/') ? BACKEND_URL.slice(0, -1) : BACKEND_URL;

  const response = await fetch(`${cleanBaseUrl}${cleanEndpoint}`, {
    ...options,
    headers,
  });

  return handleResponse(response);
}

/**
 * AUTHENTICATION
 */
export async function login(email, password) {
  const response = await fetch(`${BACKEND_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await handleResponse(response);
  if (data.access_token) {
    localStorage.setItem('token', data.access_token);
  }
  return data;
}

export async function register(userData) {
  const response = await fetch(`${BACKEND_URL}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  return handleResponse(response);
}

export async function getCurrentUser() {
  return apiFetch('/auth/me');
}

export function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

/**
 * DOMAINS (Replaces Sessions)
 */
export async function createDomain(name, description, version = '1.0.0', pdfFile = null) {
  const formData = new FormData();
  formData.append('name', name);
  if (description) formData.append('description', description);
  formData.append('version', version);
  if (pdfFile) formData.append('pdf_file', pdfFile);

  return apiFetch('/domains', {
    method: 'POST',
    // When using FormData, let the browser set the Content-Type with boundary
    headers: { 'Content-Type': undefined },
    body: formData
  });
}

export async function getDomain(domainId) {
  return apiFetch(`/domains/${domainId}`);
}

export async function listDomains() {
  return apiFetch('/domains/');
}

export async function updateDomain(domainId, configJson) {
  return apiFetch(`/domains/${domainId}`, {
    method: 'PUT',
    body: JSON.stringify({ config_json: configJson })
  });
}

export async function deleteDomain(domainId) {
  const response = await apiFetch(`/domains/${domainId}`, {
    method: 'DELETE'
  });
  return response === true || response?.status === 204;
}

/**
 * DOMAIN OPERATIONS (Direct CRUD without chatbot)
 */

// Entity Operations
export async function addEntity(domainId, entity) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.entities.push(entity);
  return updateDomain(domainId, config);
}

export async function updateEntity(domainId, entityIndex, updatedEntity) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.entities[entityIndex] = updatedEntity;
  return updateDomain(domainId, config);
}

export async function deleteEntity(domainId, entityIndex) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.entities.splice(entityIndex, 1);
  return updateDomain(domainId, config);
}

// Relationship Operations
export async function addRelationship(domainId, relationship) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.relationships.push(relationship);
  return updateDomain(domainId, config);
}

export async function updateRelationship(domainId, relationshipIndex, updatedRelationship) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.relationships[relationshipIndex] = updatedRelationship;
  return updateDomain(domainId, config);
}

export async function deleteRelationship(domainId, relationshipIndex) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.relationships.splice(relationshipIndex, 1);
  return updateDomain(domainId, config);
}

// Extraction Pattern Operations
export async function addExtractionPattern(domainId, pattern) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.extraction_patterns.push(pattern);
  return updateDomain(domainId, config);
}

export async function updateExtractionPattern(domainId, patternIndex, updatedPattern) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.extraction_patterns[patternIndex] = updatedPattern;
  return updateDomain(domainId, config);
}

export async function deleteExtractionPattern(domainId, patternIndex) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.extraction_patterns.splice(patternIndex, 1);
  return updateDomain(domainId, config);
}

// Key Terms Operations
export async function addKeyTerm(domainId, term) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.key_terms.push(term);
  return updateDomain(domainId, config);
}

export async function deleteKeyTerm(domainId, termIndex) {
  const domain = await getDomain(domainId);
  const config = domain.config_json;
  config.key_terms.splice(termIndex, 1);
  return updateDomain(domainId, config);
}

/**
 * CHAT & CHATBOT
 */

export async function createChatSession(domainConfigId) {
  return apiFetch('/chat/sessions', {
    method: 'POST',
    body: JSON.stringify({ domain_config_id: domainConfigId })
  });
}

export async function listChatSessions() {
  return apiFetch('/chat/sessions');
}

export async function sendChatMessage(sessionId, message) {
  return apiFetch(`/chat/sessions/${sessionId}/message`, {
    method: 'POST',
    body: JSON.stringify({ message })
  });
}

export async function getChatHistory(sessionId) {
  return apiFetch(`/chat/sessions/${sessionId}/messages`);
}

export async function closeChatSession(sessionId) {
  return apiFetch(`/chat/sessions/${sessionId}/close`, {
    method: 'POST'
  });
}

export async function deleteChatSession(sessionId) {
  return apiFetch(`/chat/sessions/${sessionId}`, {
    method: 'DELETE'
  });
}

/**
 * HEALTH
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    const data = await handleResponse(response);
    return { status: 'healthy', ...data };
  } catch (error) {
    return { status: 'unhealthy', error: error.message };
  }
}

/**
 * STATS (LLM Session Stats)
 */
export async function getNodeCallLogs(sessionId) {
  try {
    return await apiFetch(`/chat/sessions/${sessionId}/node-calls`);
  } catch (error) {
    return [];
  }
}

export function getBackendUrl() {
  return BACKEND_URL;
}

/**
 * LEGACY/DEPRECATED FUNCTIONS (Kept for compatibility, will be removed)
 */

// Old session-based functions - redirect to domain functions
export async function createSession(contentOrFile, fileType = null, metadata = {}) {
  console.warn('createSession is deprecated, use createDomain instead');
  return createDomain(metadata.name || 'New Domain', metadata.description || 'Created from session');
}

export async function getSession(sessionId) {
  console.warn('getSession is deprecated, use getDomain instead');
  return getDomain(sessionId);
}

export async function deleteSession(sessionId) {
  console.warn('deleteSession is deprecated, use deleteDomain instead');
  return deleteDomain(sessionId);
}

export async function getAllSessions() {
  console.warn('getAllSessions is deprecated, use listDomains instead');
  return listDomains();
}

// Domain pack functions (mapped to domain functions)
export async function listDomainPacks() {
  console.warn('listDomainPacks is deprecated, use listDomains instead');
  return listDomains();
}

export async function createDomainPack(name, description) {
  console.warn('createDomainPack is deprecated, use createDomain instead');
  return createDomain(name, description);
}

export async function getDomainPackExport(domainId) {
  console.warn('getDomainPackExport is deprecated, use getDomain instead');
  const domain = await getDomain(domainId);
  // Return structure expected by ConfigView.jsx
  return {
    json: domain.config_json,
    yaml: JSON.stringify(domain.config_json, null, 2),
    ...domain
  };
}

export async function syncDomainPack(domainId, data) {
  console.warn('syncDomainPack is deprecated, use updateDomain instead');
  // If data is a string (YAML/JSON), try to parse it
  let configJson = data;
  if (typeof data === 'string') {
    try {
      configJson = JSON.parse(data);
    } catch (e) {
      console.error('Failed to parse config string as JSON:', e);
      // If it's YAML, we'd need a parser, but for now we assume JSON or raw object
    }
  }
  return updateDomain(domainId, configJson);
}


// Version-related functions (not implemented in new backend, return mock data)
export async function getVersionYAML(sessionId, version) {
  console.warn('getVersionYAML is not implemented in the new backend');
  // Return mock YAML for now
  const domain = await getDomain(sessionId);
  return {
    yaml: `# Domain: ${domain.name}\n# Version: ${domain.version}\n\nentities: ${domain.config_json.entities.length}\nrelationships: ${domain.config_json.relationships.length}`
  };
}

export async function compareVersions(sessionId1, version1, sessionId2, version2) {
  console.warn('compareVersions is not implemented in the new backend');
  // Return mock comparison for now
  return {
    differences: [],
    message: 'Version comparison not available in current backend'
  };
}

export async function listVersions(sessionId, limit = 50) {
  console.warn('listVersions is not implemented in the new backend');
  // Return empty array for now
  return [];
}

export async function getVersion(sessionId, version) {
  console.warn('getVersion is not implemented in the new backend');
  return getDomain(sessionId);
}

export async function deleteVersion(sessionId, version) {
  console.warn('deleteVersion is not implemented in the new backend');
  return true;
}

export async function rollbackVersion(sessionId, targetVersion) {
  console.warn('rollbackVersion is not implemented in the new backend');
  return getDomain(sessionId);
}

export async function exportDomainPack(sessionId, format = 'yaml') {
  console.warn('exportDomainPack is not implemented in the new backend');
  const domain = await getDomain(sessionId);
  return {
    format,
    content: JSON.stringify(domain.config_json, null, 2)
  };
}

export function getDownloadUrl(sessionId, format = 'yaml') {
  console.warn('getDownloadUrl is not implemented in the new backend');
  return `${BACKEND_URL}/domains/${sessionId}`;
}

// Operations (not implemented in new backend)
export async function applyOperation(sessionId, operation, reason = "Direct operation") {
  console.warn('applyOperation is not implemented in the new backend');
  return { success: false, message: 'Use direct CRUD operations instead' };
}

export async function getAvailableTools() {
  console.warn('getAvailableTools is not implemented in the new backend');
  return [];
}

// Chat intent (pointing to new implementation)
export async function sendChatIntent(sessionId, message) {
  return sendChatMessage(sessionId, message);
}

export async function confirmChatIntent(sessionId, intentId, approved = true) {
  const message = approved ? "yes" : "no";
  return sendChatMessage(sessionId, message);
}

export async function getAllVersions() {
  console.warn('getAllVersions is not implemented in the new backend');
  return [];
}

