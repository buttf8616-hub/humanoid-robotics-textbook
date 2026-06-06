/**
 * ChatContext - State management for the chat widget
 *
 * Provides centralized state for:
 * - Conversation messages
 * - Panel open/close state
 * - Loading and error states
 * - Selected text context
 */
import React, { createContext, useContext, useReducer } from 'react';

// Initial state for the chat context
const initialState = {
  messages: [],           // Array of ChatMessage objects
  inputValue: '',         // Current input field value
  isOpen: false,          // Whether chat panel is open
  isLoading: false,       // Whether awaiting API response
  error: null,            // Current error message or null
  selectedContext: null,  // SelectedContext object or null
};

// Action types
const ActionTypes = {
  OPEN_PANEL: 'OPEN_PANEL',
  CLOSE_PANEL: 'CLOSE_PANEL',
  TOGGLE_PANEL: 'TOGGLE_PANEL',
  SET_INPUT: 'SET_INPUT',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  ADD_USER_MESSAGE: 'ADD_USER_MESSAGE',
  ADD_ASSISTANT_MESSAGE: 'ADD_ASSISTANT_MESSAGE',
  SET_SELECTED_CONTEXT: 'SET_SELECTED_CONTEXT',
  CLEAR_CONVERSATION: 'CLEAR_CONVERSATION',
};

// Reducer function
function chatReducer(state, action) {
  switch (action.type) {
    case ActionTypes.OPEN_PANEL:
      return { ...state, isOpen: true };

    case ActionTypes.CLOSE_PANEL:
      return { ...state, isOpen: false };

    case ActionTypes.TOGGLE_PANEL:
      return { ...state, isOpen: !state.isOpen };

    case ActionTypes.SET_INPUT:
      return { ...state, inputValue: action.payload };

    case ActionTypes.SET_LOADING:
      return { ...state, isLoading: action.payload };

    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, isLoading: false };

    case ActionTypes.CLEAR_ERROR:
      return { ...state, error: null };

    case ActionTypes.ADD_USER_MESSAGE:
      return {
        ...state,
        messages: [...state.messages, action.payload],
        inputValue: '',
      };

    case ActionTypes.ADD_ASSISTANT_MESSAGE:
      return {
        ...state,
        messages: [...state.messages, action.payload],
        isLoading: false,
      };

    case ActionTypes.SET_SELECTED_CONTEXT:
      return { ...state, selectedContext: action.payload };

    case ActionTypes.CLEAR_CONVERSATION:
      return {
        ...state,
        messages: [],
        error: null,
        selectedContext: null,
      };

    default:
      return state;
  }
}

// Create the context
const ChatContext = createContext(null);

/**
 * ChatProvider component - wraps children with chat state
 */
export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Action creators for cleaner API
  const actions = {
    openPanel: () => dispatch({ type: ActionTypes.OPEN_PANEL }),
    closePanel: () => dispatch({ type: ActionTypes.CLOSE_PANEL }),
    togglePanel: () => dispatch({ type: ActionTypes.TOGGLE_PANEL }),
    setInput: (value) => dispatch({ type: ActionTypes.SET_INPUT, payload: value }),
    setLoading: (loading) => dispatch({ type: ActionTypes.SET_LOADING, payload: loading }),
    setError: (error) => dispatch({ type: ActionTypes.SET_ERROR, payload: error }),
    clearError: () => dispatch({ type: ActionTypes.CLEAR_ERROR }),
    addUserMessage: (message) => dispatch({ type: ActionTypes.ADD_USER_MESSAGE, payload: message }),
    addAssistantMessage: (message) => dispatch({ type: ActionTypes.ADD_ASSISTANT_MESSAGE, payload: message }),
    setSelectedContext: (context) => dispatch({ type: ActionTypes.SET_SELECTED_CONTEXT, payload: context }),
    clearConversation: () => dispatch({ type: ActionTypes.CLEAR_CONVERSATION }),
  };

  return (
    <ChatContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </ChatContext.Provider>
  );
}

/**
 * useChatContext hook - access chat state and actions
 */
export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
}

// Export action types for external use if needed
export { ActionTypes };
