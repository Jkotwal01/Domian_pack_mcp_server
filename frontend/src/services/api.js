/**
 * API service for Domain Pack Backend v1
 */

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const API_BASE = `${BACKEND_URL}/api/v1`;

/**
 * Handle API responses
 */
async function handleResponse(response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

export async function createSession(contentOrFile, fileType = null, metadata = {}) {
  const formData = new FormData();
  
  if (contentOrFile instanceof File) {
    formData.append('file', contentOrFile);
  } else if (typeof contentOrFile === 'object' && contentOrFile.content) {
    // Handle our "wrapped" file object from FileUploadButton
    formData.append('content', contentOrFile.content);
  } else {
    formData.append('content', contentOrFile);
  }
  
  if (fileType) {
    formData.append('file_type', fileType);
  }

  const response = await fetch(`${API_BASE}/sessions/`, {
    method: 'POST',
    body: formData
    // Note: No 'Content-Type' header needed for FormData; browser sets it automatically with boundary
  });
  return handleResponse(response);
}

export async function getSession(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}`);
  return handleResponse(response);
}

export async function deleteSession(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE'
  });
  if (response.status === 204) return true;
  return handleResponse(response);
}

/**
 * CHAT & INTENT
 */
export async function sendChatIntent(sessionId, message) {
  const response = await fetch(`${API_BASE}/chat/intent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message })
  });
  const data = await handleResponse(response);
  return {
    success: true,
    type: data.type,
    message: data.message,
    operations: data.operations,
    intentId: data.intent_id
  };
}

export async function confirmChatIntent(sessionId, intentId, approved = true) {
  const response = await fetch(`${API_BASE}/chat/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, intent_id: intentId, approved })
  });
  const data = await handleResponse(response);
  return {
    success: true,
    approved: data.approved,
    version: data.version,
    diff: data.diff,
    message: data.message
  };
}

/**
 * OPERATIONS
 */
export async function applyOperation(sessionId, operation, reason = "Direct operation") {
  const response = await fetch(`${API_BASE}/operations/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, operation, reason })
  });
  return handleResponse(response);
}

export async function getAvailableTools() {
  const response = await fetch(`${API_BASE}/operations/tools`);
  return handleResponse(response);
}

/**
 * VERSIONS
 */
export async function listVersions(sessionId, limit = 50) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/versions?limit=${limit}`);
  const data = await handleResponse(response);
  return data.versions;
}

export async function getVersion(sessionId, version) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/versions/${version}`);
  return handleResponse(response);
}

export async function deleteVersion(sessionId, version) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/versions/${version}`, {
    method: 'DELETE'
  });
  if (response.status === 204) return true;
  return handleResponse(response);
}

/**
 * ROLLBACK
 */
export async function rollbackVersion(sessionId, targetVersion) {
  const response = await fetch(`${API_BASE}/rollback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, target_version: targetVersion })
  });
  return handleResponse(response);
}

/**
 * EXPORT
 */
export async function exportDomainPack(sessionId, format = 'yaml') {
  const response = await fetch(`${API_BASE}/export/${sessionId}?format=${format}`);
  return handleResponse(response);
}

/**
 * GRANULAR DOMAIN PACKS (Phase 1)
 */
export async function listDomainPacks() {
  const response = await fetch(`${API_BASE}/domain-packs/`);
  return handleResponse(response);
}

export async function getDomainPackExport(domainId) {
  const response = await fetch(`${API_BASE}/domain-packs/${domainId}/export`);
  return handleResponse(response);
}

export async function syncDomainPack(domainId, data) {
  const response = await fetch(`${API_BASE}/domain-packs/${domainId}/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return handleResponse(response);
}

export async function createDomainPack(name, description) {
  const response = await fetch(`${API_BASE}/domain-packs/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description })
  });
  return handleResponse(response);
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

export function getBackendUrl() {
  return BACKEND_URL;
}

export function getDownloadUrl(sessionId, format = 'yaml') {
  return `${API_BASE}/export/${sessionId}/download?format=${format}`;
}

/**
 * DASHBOARD
 */
export async function getAllSessions() {
  const response = await fetch(`${API_BASE}/dashboard/sessions`);
  return handleResponse(response);
}

export async function getAllVersions() {
  const response = await fetch(`${API_BASE}/dashboard/versions/all`);
  return handleResponse(response);
}

export async function getVersionYAML(sessionId, version) {
  const response = await fetch(`${API_BASE}/dashboard/versions/${sessionId}/${version}/yaml`);
  return handleResponse(response);
}

export async function compareVersions(sessionId1, version1, sessionId2, version2) {
  const response = await fetch(`${API_BASE}/dashboard/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id_1: sessionId1,
      version_1: version1,
      session_id_2: sessionId2,
      version_2: version2
    })
  });
  return handleResponse(response);
}

