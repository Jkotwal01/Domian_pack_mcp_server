import { useState, useRef, useEffect } from 'react';
import { useBackend } from './useBackend';

export const useChat = (sessionId, mcpSessionId, initialMessages = [], onMessagesUpdate, onMcpSessionIdUpdate, onVersionCreated) => {
    const [messages, setMessages] = useState(initialMessages);
    const [isTyping, setIsTyping] = useState(false);
    const [uploadingFiles, setUploadingFiles] = useState(false);
    const messagesEndRef = useRef(null);
    const { getIntent, confirmIntent } = useBackend();

    // currentSessionId is either the passed sessionId or the one managed by the backend
    // We prefer the backend mcpSessionId if it exists (meaning session is real/initialized)
    const [activeId, setActiveId] = useState(mcpSessionId || sessionId);

    // Only reset messages when the user switches CHAT sessions (different bucket)
    useEffect(() => {
        setMessages(initialMessages);
    }, [sessionId]); // ONLY depends on sessionId

    // Update active working ID when either changes, but preserve messages if it's just a promotion
    useEffect(() => {
        setActiveId(mcpSessionId || sessionId);
    }, [sessionId, mcpSessionId]);

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

        // 1. Intercept first message if no session exists and no file is provided
        if ((!activeId || activeId.startsWith('temp_')) && files.length === 0) {
            const userMsg = {
                id: Date.now(),
                role: 'user',
                content: content,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, userMsg]);
            
            setIsTyping(true);
            await new Promise(resolve => setTimeout(resolve, 800)); // Simulate thinking
            
            const introMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                content: "I'm your **Domain Pack AI Assistant**. I specialize in generating and maintaining complex structures like entities, rules, and reasoning templates.\n\nTo get started, **I need you to upload your domain pack file (YAML or JSON)**. This allows me to understand your project context and provide high-quality suggestions.",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, introMsg]);
            setIsTyping(false);
            return;
        }

        // 2. Handle File Upload (Session Creation)
        if (files.length > 0 && (!activeId || activeId.startsWith('temp_'))) {
            setIsTyping(true);
            try {
                const file = files[0];
                // We use the raw File object directly (api.js now handles FormData)
                const result = await getIntent(content || `Initializing with ${file.name}`, null, file);
                
                if (!result.success) throw new Error(result.error);
                
                // Sync session ID
                if (result.sessionId) {
                    setActiveId(result.sessionId);
                    if (onMcpSessionIdUpdate) onMcpSessionIdUpdate(result.sessionId);
                    // Initial version created
                    if (onVersionCreated) onVersionCreated(result.sessionId);
                }

                const aiMsg = {
                    id: Date.now() + 1,
                    role: 'assistant',
                    content: `Success! I've initialized your session with \`${file.name}\`.

I am now ready to help you enhance this domain pack. Here are some things you can ask:
- *"Suggest new entities relevant to this domain"*
- *"Check if students should have extra attributes"*
- *"Generate extraction patterns for the Instructor entity"*`,
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, aiMsg]);
            } catch (error) {
                console.error('Initialization failed:', error);
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
            return;
        }

        const userMsg = {
            id: Date.now(),
            role: 'user',
            content: content,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        try {
            // Send to backend v1 intent flow
            const result = await getIntent(content, activeId);

            if (!result.success) {
                throw new Error(result.error);
            }

            // Sync session ID if a new one was created
            if (result.sessionId && result.sessionId !== activeId) {
                setActiveId(result.sessionId);
                if (onMcpSessionIdUpdate) onMcpSessionIdUpdate(result.sessionId);
            }

            // Create AI message
            const aiMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                content: result.message,
                type: result.type, // 'suggestion' or 'operation'
                operations: result.operations,
                intentId: result.intentId,
                sessionId: result.sessionId,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, aiMsg]);
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
        try {
            const result = await confirmIntent(activeId, intentId, approved);
            
            // Refresh versions if approved
            if (approved && onVersionCreated) {
                onVersionCreated(activeId);
            }
            
            const systemMsg = {
                id: Date.now() + 2,
                role: 'assistant',
                content: result.message,
                diff: result.diff,
                version: result.version,
                timestamp: new Date(),
                isSystemAction: true,
                error: !result.approved && approved // only error if they clicked approve but it failed
            };

            setMessages(prev => [...prev, systemMsg]);
        } catch (error) {
            const errorMsg = {
                id: Date.now() + 2,
                role: 'assistant',
                content: `Error confirming intent: ${error.message}`,
                timestamp: new Date(),
                error: true
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
        }
    };

    return {
        messages,
        isTyping,
        uploadingFiles,
        sendMessage,
        handleConfirmIntent,
        messagesEndRef
    };
};
