/**
 * useChatApi - Hook for communicating with the RAG backend
 *
 * Handles:
 * - Sending questions to POST /api/v1/chat
 * - Request timeout (30 seconds)
 * - Response parsing to ChatMessage format
 * - Error handling with user-friendly messages
 * - Listening for chat:submit events from ChatInput
 */
import { useEffect, useRef, useCallback } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { useChatContext } from '@site/src/context/ChatContext';
import {
  createUserMessage,
  createAssistantMessage,
  getErrorMessage,
  formatConversationHistory,
} from '@site/src/utils/chatHelpers';

const REQUEST_TIMEOUT = 30000; // 30 seconds
const RETRY_DELAY = 5000; // 5 seconds for 503 auto-retry

export default function useChatApi() {
  const { siteConfig } = useDocusaurusContext();
  const { state, actions } = useChatContext();
  const abortControllerRef = useRef(null);

  const getApiUrl = useCallback(() => {
    return siteConfig?.customFields?.chatApiUrl || 'http://localhost:8000';
  }, [siteConfig]);

  const sendMessage = useCallback(
    async (question) => {
      // Add user message to conversation
      const userMessage = createUserMessage(question);
      actions.addUserMessage(userMessage);
      actions.setLoading(true);
      actions.clearError();

      // Abort any in-flight request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      const controller = new AbortController();
      abortControllerRef.current = controller;

      // Set timeout
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, REQUEST_TIMEOUT);

      try {
        const apiUrl = getApiUrl();
        const conversationHistory = formatConversationHistory(state.messages);

        const requestBody = {
          question,
          top_k: 5,
        };

        // Include conversation history if available
        if (conversationHistory.length > 0) {
          requestBody.conversation_history = conversationHistory;
        }

        // Include selected context if present
        if (state.selectedContext) {
          requestBody.selected_context = {
            url: state.selectedContext.url,
          };
          if (state.selectedContext.section) {
            requestBody.selected_context.section = state.selectedContext.section;
          }
        }

        const response = await fetch(`${apiUrl}/api/v1/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          // Handle 503 with auto-retry
          if (response.status === 503) {
            actions.setError('Service temporarily unavailable. Retrying...');
            setTimeout(() => {
              sendMessage(question);
            }, RETRY_DELAY);
            return;
          }

          const errorMessage = getErrorMessage(null, response.status);
          actions.setError(errorMessage);
          return;
        }

        const data = await response.json();

        // Map API response to ChatMessage format
        const assistantMessage = createAssistantMessage(data);
        actions.addAssistantMessage(assistantMessage);
      } catch (error) {
        clearTimeout(timeoutId);

        if (error.name === 'AbortError') {
          actions.setError(getErrorMessage(error));
          return;
        }

        actions.setError(getErrorMessage(error));
      } finally {
        abortControllerRef.current = null;
      }
    },
    [getApiUrl, state.messages, state.selectedContext, actions]
  );

  // Listen for chat:submit events from ChatInput
  useEffect(() => {
    const handleChatSubmit = (event) => {
      const { question } = event.detail;
      if (question) {
        sendMessage(question);
      }
    };

    window.addEventListener('chat:submit', handleChatSubmit);
    return () => {
      window.removeEventListener('chat:submit', handleChatSubmit);
    };
  }, [sendMessage]);

  // Cleanup abort controller on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return { sendMessage };
}
