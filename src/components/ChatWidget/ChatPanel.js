/**
 * ChatPanel - Main chat panel UI
 *
 * Contains:
 * - Header with title and close button
 * - Messages container with scroll
 * - Chat input at bottom
 * - Error display
 * - Selected context preview
 */
import React, { useRef, useEffect, useCallback } from 'react';
import { useChatContext } from '@site/src/context/ChatContext';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import styles from './ChatPanel.module.css';

export default function ChatPanel() {
  const { state, actions } = useChatContext();
  const { messages, isLoading, error, selectedContext } = state;
  const messagesEndRef = useRef(null);
  const panelRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Focus trap for accessibility (T112)
  const handleTabKey = useCallback((e) => {
    if (e.key !== 'Tab' || !panelRef.current) return;

    const focusableElements = panelRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusableElements.length === 0) return;

    const first = focusableElements[0];
    const last = focusableElements[focusableElements.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', handleTabKey);
    return () => document.removeEventListener('keydown', handleTabKey);
  }, [handleTabKey]);

  return (
    <div
      ref={panelRef}
      className={styles.chatPanel}
      role="dialog"
      aria-label="Robot AI Assistant"
      aria-modal="true"
    >
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <h3 className={styles.title}>🤖 Robot AI Assistant</h3>
          {selectedContext && (
            <span className={styles.contextBadge}>
              Context active
            </span>
          )}
        </div>
        <div className={styles.headerActions}>
          {messages.length > 0 && (
            <button
              className={styles.newConvoButton}
              onClick={actions.clearConversation}
              aria-label="New conversation"
              title="New conversation"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 5v14M5 12h14"></path>
              </svg>
            </button>
          )}
          <button
            className={styles.closeButton}
            onClick={actions.closePanel}
            aria-label="Close chat"
          >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        </div>
      </div>

      {/* Selected Context Preview */}
      {selectedContext && (
        <div className={styles.contextPreview}>
          <span className={styles.contextLabel}>Asking about:</span>
          <span className={styles.contextText}>
            {selectedContext.text?.substring(0, 100)}
            {selectedContext.text?.length > 100 ? '...' : ''}
          </span>
          <button
            className={styles.clearContextButton}
            onClick={() => actions.setSelectedContext(null)}
            aria-label="Clear context"
          >
            Clear
          </button>
        </div>
      )}

      {/* Messages Container */}
      <div className={styles.messagesContainer} aria-live="polite">
        {messages.length === 0 && !isLoading && !error && (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>
              <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 64 64" fill="currentColor" opacity="0.5">
                <rect x="29" y="1" width="6" height="8" rx="3"/>
                <circle cx="32" cy="1.5" r="3" opacity="0.7"/>
                <rect x="14" y="9" width="36" height="22" rx="5"/>
                <rect x="18" y="15" width="11" height="8" rx="2.5" fill="var(--chat-bg, #fff)" opacity="0.7"/>
                <rect x="35" y="15" width="11" height="8" rx="2.5" fill="var(--chat-bg, #fff)" opacity="0.7"/>
                <rect x="19" y="25" width="26" height="3" rx="1.5" fill="var(--chat-bg, #fff)" opacity="0.5"/>
                <rect x="26" y="31" width="12" height="5" rx="2" opacity="0.8"/>
                <rect x="9" y="36" width="46" height="22" rx="6"/>
                <rect x="18" y="40" width="28" height="13" rx="3" fill="var(--chat-bg, #fff)" opacity="0.5"/>
                <circle cx="26" cy="47" r="3" fill="var(--chat-bg, #fff)" opacity="0.7"/>
                <circle cx="32" cy="47" r="3" fill="var(--chat-bg, #fff)"/>
                <circle cx="38" cy="47" r="3" fill="var(--chat-bg, #fff)" opacity="0.7"/>
                <rect x="1" y="37" width="8" height="16" rx="4" opacity="0.85"/>
                <rect x="55" y="37" width="8" height="16" rx="4" opacity="0.85"/>
              </svg>
            </div>
            <p className={styles.emptyText}>
              Ask me anything about the textbook!
            </p>
            <p className={styles.emptyHint}>
              Try: "What is embodied intelligence?"
            </p>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className={styles.loadingContainer}>
            <div className={styles.loadingDots}>
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className={styles.loadingText}>Thinking...</span>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className={styles.errorContainer}>
            <div className={styles.errorMessage}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <span>{error}</span>
            </div>
            <button
              className={styles.retryButton}
              onClick={actions.clearError}
            >
              Dismiss
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <ChatInput />
    </div>
  );
}
