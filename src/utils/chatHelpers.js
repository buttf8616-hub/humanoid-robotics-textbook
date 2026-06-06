/**
 * Chat Helper Utilities
 *
 * Utility functions for chat widget operations
 */

/**
 * Generate a unique message ID using timestamp and random string
 * @returns {string} Unique message ID
 */
export function generateMessageId() {
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substring(2, 9);
  return `msg_${timestamp}_${randomPart}`;
}

/**
 * Create a user message object
 * @param {string} content - Message content
 * @returns {Object} ChatMessage object
 */
export function createUserMessage(content) {
  return {
    id: generateMessageId(),
    role: 'user',
    content: content.trim(),
    timestamp: new Date(),
  };
}

/**
 * Create an assistant message object from API response
 * @param {Object} response - API response object
 * @returns {Object} ChatMessage object
 */
export function createAssistantMessage(response) {
  return {
    id: generateMessageId(),
    role: 'assistant',
    content: response.answer,
    timestamp: new Date(),
    sources: response.sources || [],
    confidence: response.confidence || 'medium',
  };
}

/**
 * Format conversation history for API request
 * @param {Array} messages - Array of ChatMessage objects
 * @param {number} maxMessages - Maximum messages to include (default: 6)
 * @returns {Array} Formatted conversation history
 */
export function formatConversationHistory(messages, maxMessages = 6) {
  // Get the last N messages
  const recentMessages = messages.slice(-maxMessages);

  // Format for API
  return recentMessages.map((msg) => ({
    role: msg.role,
    content: msg.content,
  }));
}

/**
 * Get user-friendly error message from error type
 * @param {Error|string} error - Error object or string
 * @param {number} statusCode - HTTP status code if available
 * @returns {string} User-friendly error message
 */
export function getErrorMessage(error, statusCode = null) {
  // Network errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return 'Unable to connect. Check your internet connection.';
  }

  // HTTP status code errors
  if (statusCode) {
    switch (statusCode) {
      case 400:
        return 'Please enter a valid question.';
      case 503:
        return 'Service temporarily unavailable. Please try again.';
      case 504:
        return 'Request timed out. Please try again.';
      default:
        if (statusCode >= 500) {
          return 'Server error. Please try again later.';
        }
    }
  }

  // Timeout error
  if (error?.name === 'AbortError' || error?.message?.includes('timeout')) {
    return 'Taking too long. Please try again.';
  }

  // Default error
  return 'Something went wrong. Please try again.';
}

/**
 * Check if a question is valid (non-empty, non-whitespace)
 * @param {string} question - Question text
 * @returns {boolean} Whether question is valid
 */
export function isValidQuestion(question) {
  return question && question.trim().length > 0;
}

/**
 * Truncate text to a maximum length with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength = 100) {
  if (!text || text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + '...';
}
