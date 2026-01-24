import { useState, useRef, useEffect } from 'react';
import { useMCPServer } from './useMCPServer';

export const useChat = (sessionId, mcpSessionId, initialMessages = [], onMessagesUpdate, onMcpSessionIdUpdate) => {
    const [messages, setMessages] = useState(initialMessages);
    const [isTyping, setIsTyping] = useState(false);
    const [uploadingFiles, setUploadingFiles] = useState(false); // Changed from [] to false
    const messagesEndRef = useRef(null);
    const { sendToMCP } = useMCPServer();

    useEffect(() => {
        setMessages(initialMessages);
    }, [sessionId]); // Only update when session ID changes

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

    const sendMessage = async (content, files = []) => {
        if (!content.trim() && files.length === 0) return;

        // Simulate file upload if files are present
        if (files.length > 0) {
            setUploadingFiles(files);
            // Simulate upload delay
            await new Promise(resolve => setTimeout(resolve, 1500));
            setUploadingFiles([]);
        }

        const userMsg = {
            id: Date.now(),
            role: 'user',
            content: content,
            files: files.length > 0 ? files : undefined,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        try {
            // Build conversation history correctly including the new user message
            // We use functional update setMessages to get latest pre-update state, but here we just constructed userMsg
            // So history is [...messages, userMsg]
            const currentHistory = [...messages, userMsg].map(msg => ({
                role: msg.role,
                content: msg.content
            }));

            // Send to backend with MCP integration
            const mcpResponse = await sendToMCP(
                content,
                files,
                mcpSessionId,  // Use MCP session ID from backend
                currentHistory
            );

            // Update MCP session ID if backend returned one
            if (mcpResponse.sessionId && mcpResponse.sessionId !== mcpSessionId) {
                onMcpSessionIdUpdate(mcpResponse.sessionId);
            }

            // Create AI message with backend response
            const aiMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                content: mcpResponse.response || mcpResponse.error || 'No response from backend',
                toolCalls: mcpResponse.toolCalls || [],
                timestamp: new Date(),
                error: !mcpResponse.success
            };

            setMessages(prev => [...prev, aiMsg]);
            setIsTyping(false);

        } catch (error) {
            console.error('Error sending message:', error);
            
            // Add error message
            const errorMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                content: `Error: ${error.message}. Please make sure the backend is running.`,
                timestamp: new Date(),
                error: true
            };
            
            setMessages(prev => [...prev, errorMsg]);
            setIsTyping(false);
        }
    };

    return {
        messages,
        isTyping,
        uploadingFiles,
        sendMessage,
        messagesEndRef,
        sessionId
    };
};
