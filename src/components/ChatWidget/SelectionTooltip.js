/**
 * SelectionTooltip - Floating tooltip near text selection
 *
 * Shows "Ask about this" button when user selects text in book content.
 * Positions itself near the selection, handling viewport edge cases.
 */
import React, { useMemo } from 'react';
import { useChatContext } from '@site/src/context/ChatContext';
import styles from './SelectionTooltip.module.css';

const TOOLTIP_OFFSET = 8;

export default function SelectionTooltip({ selection, onDismiss }) {
  const { actions } = useChatContext();

  const tooltipStyle = useMemo(() => {
    if (!selection?.rect) return {};

    const { rect } = selection;
    const viewportWidth = window.innerWidth;
    const tooltipWidth = 160;

    // Position above the selection
    let top = rect.top + window.scrollY - 40 - TOOLTIP_OFFSET;
    let left = rect.left + rect.width / 2 - tooltipWidth / 2;

    // If above the viewport, position below
    if (rect.top < 50) {
      top = rect.bottom + window.scrollY + TOOLTIP_OFFSET;
    }

    // Clamp to viewport edges
    left = Math.max(8, Math.min(left, viewportWidth - tooltipWidth - 8));

    return {
      position: 'absolute',
      top: `${top}px`,
      left: `${left}px`,
      zIndex: 1001,
    };
  }, [selection]);

  if (!selection) return null;

  const handleAskAboutThis = () => {
    actions.setSelectedContext({
      text: selection.text,
      url: selection.url,
      section: selection.section,
      position: selection.position,
    });
    actions.openPanel();
    if (onDismiss) onDismiss();
  };

  return (
    <div className={styles.tooltip} style={tooltipStyle}>
      <button
        className={styles.askButton}
        onClick={handleAskAboutThis}
        aria-label="Ask AI about selected text"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        Ask about this
      </button>
    </div>
  );
}
