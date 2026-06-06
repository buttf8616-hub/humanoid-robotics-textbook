/**
 * ChatWidget - Main chat widget container
 *
 * Renders the toggle button and chat panel.
 * Controls the open/close state via ChatContext.
 */
import React, { useEffect, useCallback } from 'react';
import { useChatContext } from '@site/src/context/ChatContext';
import useChatApi from '@site/src/hooks/useChatApi';
import useTextSelection from '@site/src/hooks/useTextSelection';
import ChatPanel from './ChatPanel';
import SelectionTooltip from './SelectionTooltip';
import styles from './ChatWidget.module.css';

export default function ChatWidget() {
  const { state, actions } = useChatContext();
  const { isOpen } = state;

  // Initialize the chat API hook (listens for chat:submit events)
  useChatApi();

  // Text selection detection for US2
  const { selection, clearSelection } = useTextSelection();

  // Handle Escape key to close panel
  const handleKeyDown = useCallback(
    (event) => {
      if (event.key === 'Escape' && isOpen) {
        actions.closePanel();
      }
      // Ctrl+/ or Cmd+/ to toggle panel
      if ((event.ctrlKey || event.metaKey) && event.key === '/') {
        event.preventDefault();
        actions.togglePanel();
      }
    },
    [isOpen, actions]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  return (
    <div className={styles.chatWidget}>
      {/* Toggle Button */}
      <button
        className={styles.toggleButton}
        onClick={actions.togglePanel}
        aria-label={isOpen ? 'Close Robot AI Assistant' : 'Open Robot AI Assistant'}
        aria-expanded={isOpen}
        title="Robot AI Assistant (Ctrl+/)"
      >
        {isOpen ? (
          // Close icon
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        ) : (
          // Robot icon
          <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 64 64" fill="currentColor">
            {/* Antenna */}
            <rect x="29" y="1" width="6" height="8" rx="3" fill="currentColor"/>
            <circle cx="32" cy="1.5" r="3" fill="currentColor" opacity="0.7"/>
            {/* Head */}
            <rect x="14" y="9" width="36" height="22" rx="5" fill="currentColor"/>
            {/* Eyes */}
            <rect x="18" y="15" width="11" height="8" rx="2.5" fill="var(--chat-header-bg, #18181b)" opacity="0.9"/>
            <rect x="35" y="15" width="11" height="8" rx="2.5" fill="var(--chat-header-bg, #18181b)" opacity="0.9"/>
            <rect x="21" y="17" width="5" height="4" rx="1.5" fill="var(--chat-toggle-bg, #18181b)" opacity="0.5"/>
            <rect x="38" y="17" width="5" height="4" rx="1.5" fill="var(--chat-toggle-bg, #18181b)" opacity="0.5"/>
            {/* Mouth */}
            <rect x="19" y="25" width="26" height="3" rx="1.5" fill="var(--chat-header-bg, #18181b)" opacity="0.7"/>
            {/* Neck */}
            <rect x="26" y="31" width="12" height="5" rx="2" fill="currentColor" opacity="0.8"/>
            {/* Body */}
            <rect x="9" y="36" width="46" height="22" rx="6" fill="currentColor"/>
            {/* Chest panel */}
            <rect x="18" y="40" width="28" height="13" rx="3" fill="var(--chat-header-bg, #18181b)" opacity="0.7"/>
            <circle cx="26" cy="47" r="3" fill="currentColor" opacity="0.8"/>
            <circle cx="32" cy="47" r="3" fill="currentColor"/>
            <circle cx="38" cy="47" r="3" fill="currentColor" opacity="0.8"/>
            {/* Arms */}
            <rect x="1" y="37" width="8" height="16" rx="4" fill="currentColor" opacity="0.85"/>
            <rect x="55" y="37" width="8" height="16" rx="4" fill="currentColor" opacity="0.85"/>
          </svg>
        )}
      </button>

      {/* Chat Panel */}
      {isOpen && <ChatPanel />}

      {/* Selection Tooltip (US2) */}
      {!isOpen && selection && (
        <SelectionTooltip selection={selection} onDismiss={clearSelection} />
      )}
    </div>
  );
}
