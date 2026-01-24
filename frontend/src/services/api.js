/**
 * API service for backend communication
 */

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

/**
 * Send a chat message to the backend
 * @param {string} message - User message
 * @param {string|null} sessionId - Optional session ID
 * @param {Array} conversationHistory - Optional conversation history
 * @returns {Promise<Object>} Chat response
 */
export async function sendChatMessage(message, files = [], sessionId = null, conversationHistory = []) {
  try {
    console.log('Sending message to backend:', { message, filesCount: files.length, sessionId });
    if (files.length > 0) {
        console.log('First file content preview:', files[0].name, files[0].content ? files[0].content.substring(0, 50) : 'NO CONTENT');
    }

    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        files,
        session_id: sessionId,
        conversation_history: conversationHistory
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      response: data.response,
      sessionId: data.session_id,
      toolCalls: data.tool_calls || []
    };
  } catch (error) {
    console.error('Error sending chat message:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Call MCP tool directly (for testing)
 * @param {string} toolName - Name of the tool
 * @param {Object} args - Tool arguments
 * @returns {Promise<Object>} Tool result
 */
export async function callMCPTool(toolName, args) {
  try {
    const response = await fetch(`${BACKEND_URL}/mcp/call?tool_name=${toolName}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(args),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling MCP tool:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Check backend health
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking backend health:', error);
    return {
      status: 'unhealthy',
      error: error.message
    };
  }
}

/**
 * Get backend URL
 * @returns {string} Backend URL
 */
export function getBackendUrl() {
  return BACKEND_URL;
}
