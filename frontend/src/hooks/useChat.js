import { useState, useRef, useEffect } from 'react';
import { useMCPServer } from './useMCPServer';

export const useChat = (sessionId, initialMessages = [], onMessagesUpdate) => {
    const [messages, setMessages] = useState(initialMessages);
    const [isTyping, setIsTyping] = useState(false);
    const [uploadingFiles, setUploadingFiles] = useState([]);
    const messagesEndRef = useRef(null);
    const { sendToMCP } = useMCPServer();

    // Update messages when session changes
    useEffect(() => {
        setMessages(initialMessages);
    }, [sessionId]);

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

        // Send to MCP server for tool calling
        const mcpResponse = await sendToMCP(content, files);

        // Mock AI response delay
        setTimeout(() => {
            const aiMsg = {
                id: Date.now() + 1,
                role: 'assistant',
                content: generateMockResponse(content, files),
                toolCalls: mcpResponse.toolCalls || [],
                timestamp: new Date()
            };
            setMessages(prev => [...prev, aiMsg]);
            setIsTyping(false);
        }, 1500 + Math.random() * 1000);
    };

    return {
        messages,
        isTyping,
        uploadingFiles,
        sendMessage,
        messagesEndRef
    };
};

const generateMockResponse = (input, files = []) => {
    const responses = [
        "That's an interesting perspective. Could you elaborate more?",
        "I can help with that. Here's a breakdown of what you might need...",
        "Based on what you've said, I'd recommend looking into React hooks more deeply.",
        "Sure! Here is a list of items:\n\n1. First item\n2. Second item\n3. Third item\n\nHope this helps!",
        "I understand. Let's proceed with the next step."
    ];
    
    let response = responses[Math.floor(Math.random() * responses.length)];
    
    if (files.length > 0) {
        response = `I received ${files.length} file(s). ${response}`;
    }
    
    if (input) {
        response += `\n\n(Context: "${input.substring(0, 20)}...")`;
    }
    
    return response;
};


