import { useState, useRef, useEffect } from 'react';
import { useBackend } from './useBackend';

export const useChat = (sessionId, domainConfigId, mcpSessionId, initialMessages = [], onMessagesUpdate, onMcpSessionIdUpdate, onVersionCreated) => {
    const [messages, setMessages] = useState(initialMessages);
    const [isTyping, setIsTyping] = useState(false);
    const [uploadingFiles, setUploadingFiles] = useState(false);
    const messagesEndRef = useRef(null);
    const { getIntent, confirmIntent, deleteSession } = useBackend();

    // activeMcpId tracks the REAL ChatSession ID from the database
    const [activeMcpId, setActiveMcpId] = useState(mcpSessionId);

    // Only reset messages when the user switches CHAT sessions (different bucket)
    useEffect(() => {
        console.log('[useChat] Session ID changed, refreshing messages:', { sessionId, mcpSessionId });
        setMessages(initialMessages);
        setActiveMcpId(mcpSessionId);
    }, [sessionId]); // ONLY depend on sessionId to avoid resets during promotion

    // Sync activeMcpId if it's updated from props (without resetting messages)
    useEffect(() => {
        if (mcpSessionId && mcpSessionId !== activeMcpId) {
            console.log('[useChat] Syncing mcpSessionId:', mcpSessionId);
            setActiveMcpId(mcpSessionId);
        }
    }, [mcpSessionId]);

    // Notify parent of message updates
    useEffect(() => {
        if (onMessagesUpdate && messages.length > 0) {
            onMessagesUpdate(messages);
        }
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    /**
     * Send message and handle intent/suggestion response
     */
    const sendMessage = async (content, files = []) => {
        if (!content.trim() && files.length === 0) return;

        const userMsg = {
            id: Date.now(),
            role: 'user',
            content: content,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        try {
            // Use domainConfigId for intent flow (backend handles session creation/retrieval)
            const result = await getIntent(content, domainConfigId);

            if (!result.success && !result.message) {
                throw new Error(result.error || "Failed to get response");
            }

            // Sync session ID (the real database ChatSession ID)
            if (result.sessionId && onMcpSessionIdUpdate) {
                onMcpSessionIdUpdate(result.sessionId);
            }

            // Create AI message
            const aiMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                content: result.message,
                type: result.needs_confirmation ? 'operation' : 'suggestion',
                operations: result.proposed_changes, // Use proposed_changes for display
                intentId: result.intentId || 'pending', // Use 'pending' if not provided
                diff: result.diff_preview, // Pass diff preview for rendering
                timestamp: new Date()
            };

            setMessages(prev => [...prev, aiMsg]);
            console.log('[useChat] Assistant message added to state:', aiMsg.id);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                content: `Error: ${error.message}`,
                timestamp: new Date(),
                error: true
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
        }
    };

    /**
     * Handlers for intent confirmation
     */
    const handleConfirmIntent = async (intentId, approved) => {
        setIsTyping(true);
        // Add a small delay for better UX
        const userMsg = {
            id: Date.now() + 1,
            role: 'user',
            content: approved ? "Yes" : "No",
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMsg]);

        try {
            // Need a real database session ID to confirm
            if (!activeMcpId) throw new Error("Chat session not initialized");
            
            const result = await confirmIntent(activeMcpId, intentId, approved);
            
            // Refresh versions if approved
            if (approved && onVersionCreated) {
                onVersionCreated(domainConfigId);
            }
            
            const systemMsg = {
                id: Date.now() + 2,
                role: 'assistant',
                content: result.message,
                diff: result.diff_preview || result.diff,
                timestamp: new Date(),
                isSystemAction: true
            };

            setMessages(prev => [...prev, systemMsg]);
        } catch (error) {
            const errorMsg = {
                id: Date.now() + 2,
                role: 'assistant',
                content: `Error confirming change: ${error.message}`,
                timestamp: new Date(),
                error: true
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
        }
    };

    const deleteCurrentSession = async () => {
        if (!activeMcpId) {
            // If no backend session exists yet, just clear local messages
            setMessages([]);
            return true;
        }

        try {
            const success = await deleteSession(activeMcpId);
            if (success) {
                setMessages([]);
                if (onMcpSessionIdUpdate) {
                    onMcpSessionIdUpdate(null);
                }
                setActiveMcpId(null);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error deleting session:', error);
            // If it's a 404, it might already be gone (or wrong ID), so just clear local
            if (error.message?.includes('404')) {
                setMessages([]);
                if (onMcpSessionIdUpdate) onMcpSessionIdUpdate(null);
                setActiveMcpId(null);
                return true;
            }
            return false;
        }
    };

    return {
        messages,
        isTyping,
        uploadingFiles,
        sendMessage,
        handleConfirmIntent,
        deleteCurrentSession,
        messagesEndRef
    };
};
