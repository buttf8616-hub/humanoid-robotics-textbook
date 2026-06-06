/**
 * ChatInput - Message input field with send button
 *
 * Features:
 * - Auto-resizing textarea
 * - Send on Enter (Shift+Enter for newline)
 * - Disabled state during loading
 * - Character limit display
 */
import React, { useRef, useEffect } from 'react';
import { useChatContext } from '@site/src/context/ChatContext';
import { isValidQuestion } from '@site/src/utils/chatHelpers';
import styles from './ChatInput.module.css';

const MAX_CHARS = 500;

export default function ChatInput() {
  const { state, actions } = useChatContext();
  const { inputValue, isLoading } = state;
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  }, [inputValue]);

  // Focus input when panel opens
  useEffect(() => {
    if (state.isOpen && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [state.isOpen]);

  const handleSubmit = () => {
    if (!isValidQuestion(inputValue) || isLoading) return;
    if (inputValue.length > MAX_CHARS) return;

    // The actual send is handled by the useChatApi hook
    // We dispatch the input value and let the hook take over
    const question = inputValue.trim();
    actions.setInput('');
    // Dispatch a custom event that useChatApi listens to
    window.dispatchEvent(
      new CustomEvent('chat:submit', { detail: { question } })
    );
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e) => {
    const value = e.target.value;
    if (value.length <= MAX_CHARS) {
      actions.setInput(value);
    }
  };

  const canSend = isValidQuestion(inputValue) && !isLoading && inputValue.length <= MAX_CHARS;

  return (
    <div className={styles.inputContainer}>
      <div className={styles.inputWrapper}>
        <textarea
          ref={textareaRef}
          className={styles.textarea}
          value={inputValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask about the textbook..."
          disabled={isLoading}
          rows={1}
          aria-label="Type your question"
          maxLength={MAX_CHARS}
        />
        <button
          className={styles.sendButton}
          onClick={handleSubmit}
          disabled={!canSend}
          aria-label="Send message"
          title="Send (Enter)"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
      {inputValue.length > MAX_CHARS * 0.8 && (
        <div className={styles.charCount}>
          {inputValue.length}/{MAX_CHARS}
        </div>
      )}
    </div>
  );
}
