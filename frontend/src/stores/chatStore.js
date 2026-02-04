/**
 * Chat Store
 * Manages chat sessions and messages
 */
import { create } from 'zustand';
import { chatAPI } from '../api/chat';

const useChatStore = create((set, get) => ({
  sessions: [],
  currentSession: null,
  messages: [],
  isLoading: false,
  isSending: false,
  error: null,

  loadSessions: async () => {
    set({ isLoading: true, error: null });
    try {
      const sessions = await chatAPI.getSessions();
      set({ sessions, isLoading: false });
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Failed to load sessions',
        isLoading: false,
      });
    }
  },

  createSession: async (domainPackId, metadata = {}) => {
    set({ isLoading: true, error: null });
    try {
      const session = await chatAPI.createSession(domainPackId, metadata);
      set((state) => ({
        sessions: [session, ...state.sessions],
        currentSession: session,
        messages: [],
        isLoading: false,
      }));
      return session;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Failed to create session',
        isLoading: false,
      });
      return null;
    }
  },

  setCurrentSession: (session) => {
    set({ currentSession: session, messages: [] });
  },

  sendMessage: async (message, domainPackId) => {
    const { currentSession } = get();
    if (!currentSession) return;

    // Add user message immediately
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    
    set((state) => ({
      messages: [...state.messages, userMessage],
      isSending: true,
      error: null,
    }));

    try {
      const response = await chatAPI.sendMessage(
        currentSession.id,
        message,
        domainPackId
      );

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        proposal: response.proposal,
        requires_confirmation: response.requires_confirmation,
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isSending: false,
      }));

      return response;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Failed to send message',
        isSending: false,
      });
      return null;
    }
  },

  clearError: () => set({ error: null }),
}));

export default useChatStore;
