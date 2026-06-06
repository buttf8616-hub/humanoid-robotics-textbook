/**
 * SourceCitation - Renders a clickable source citation link
 *
 * Displays:
 * - Title and section as clickable link
 * - Relevance score badge with color coding
 * - Navigates to book section on click (FR-006)
 */
import React from 'react';
import styles from './SourceCitation.module.css';

function getScoreClass(score) {
  if (score >= 0.8) return styles.scoreHigh;
  if (score >= 0.5) return styles.scoreMedium;
  return styles.scoreLow;
}

function getScoreLabel(score) {
  return Math.round(score * 100) + '%';
}

export default function SourceCitation({ source }) {
  const { url, title, section, score } = source;

  const handleClick = (e) => {
    e.preventDefault();
    // Navigate to the book section
    if (url) {
      window.location.href = url;
    }
  };

  return (
    <a
      className={styles.citation}
      href={url || '#'}
      onClick={handleClick}
      title={`${title} - ${section}`}
      aria-label={`Source: ${title}, section ${section}, relevance ${getScoreLabel(score)}`}
    >
      <div className={styles.citationContent}>
        <div className={styles.citationTitle}>{title}</div>
        {section && (
          <div className={styles.citationSection}>{section}</div>
        )}
      </div>
      <span className={`${styles.scoreBadge} ${getScoreClass(score)}`}>
        {getScoreLabel(score)}
      </span>
    </a>
  );
}
