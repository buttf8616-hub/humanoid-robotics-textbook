/**
 * ChatMessage - Renders a single chat message
 *
 * Supports:
 * - User and assistant message styles
 * - Markdown rendering for assistant messages
 * - Source citations display
 * - Confidence indicator
 */
import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SourceCitation from './SourceCitation';
import styles from './ChatMessage.module.css';

export default function ChatMessage({ message }) {
  const { role, content, sources, confidence } = message;
  const isUser = role === 'user';

  return (
    <div
      className={`${styles.message} ${isUser ? styles.userMessage : styles.assistantMessage}`}
      role="article"
      aria-label={`${isUser ? 'You' : 'Assistant'}: ${content.substring(0, 50)}`}
    >
      <div className={styles.bubble}>
        {isUser ? (
          <p className={styles.userText}>{content}</p>
        ) : (
          <div className={styles.markdownContent}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          </div>
        )}
      </div>

      {/* Confidence indicator for assistant messages */}
      {!isUser && confidence && (
        <div className={styles.meta}>
          <span className={`${styles.confidence} ${styles[confidence]}`}>
            {confidence === 'high' && 'High confidence'}
            {confidence === 'medium' && 'Medium confidence'}
            {confidence === 'low' && 'Low confidence'}
            {confidence === 'refused' && 'Out of scope'}
          </span>
        </div>
      )}

      {/* Source Citations */}
      {!isUser && sources && sources.length > 0 && (
        <div className={styles.sources}>
          <span className={styles.sourcesLabel}>Sources:</span>
          {sources.map((source, index) => (
            <SourceCitation key={index} source={source} />
          ))}
        </div>
      )}
    </div>
  );
}
