/**
 * useTextSelection - Hook for detecting text selection in book content
 *
 * Features:
 * - Listens for mouseup/selectionchange events
 * - Extracts selected text, position, and bounding rect
 * - Detects current page URL
 * - Detects nearest section header from selection
 * - Filters out selections outside main content area
 */
import { useState, useEffect, useCallback } from 'react';

const MIN_SELECTION_LENGTH = 3;

function getNearestSectionHeader(node) {
  let current = node;
  while (current && current !== document.body) {
    // Check if current element is a heading
    if (/^H[1-6]$/.test(current.tagName)) {
      return current.textContent.trim();
    }
    // Check previous siblings for headings
    let sibling = current.previousElementSibling;
    while (sibling) {
      if (/^H[1-6]$/.test(sibling.tagName)) {
        return sibling.textContent.trim();
      }
      sibling = sibling.previousElementSibling;
    }
    current = current.parentElement;
  }
  return null;
}

function isInContentArea(node) {
  let current = node;
  while (current && current !== document.body) {
    // Docusaurus main content areas
    if (
      current.classList?.contains('markdown') ||
      current.tagName === 'ARTICLE' ||
      current.getAttribute?.('role') === 'main'
    ) {
      return true;
    }
    // Exclude chat widget selections
    if (current.classList?.contains('chatWidget') || current.classList?.contains('chatPanel')) {
      return false;
    }
    current = current.parentElement;
  }
  return false;
}

export default function useTextSelection() {
  const [selection, setSelection] = useState(null);

  const handleSelectionChange = useCallback(() => {
    const sel = window.getSelection();

    if (!sel || sel.isCollapsed || !sel.rangeCount) {
      setSelection(null);
      return;
    }

    const text = sel.toString().trim();

    if (text.length < MIN_SELECTION_LENGTH) {
      setSelection(null);
      return;
    }

    // Only detect selections in the main content area
    const anchorNode = sel.anchorNode;
    if (!anchorNode || !isInContentArea(anchorNode.parentElement || anchorNode)) {
      setSelection(null);
      return;
    }

    const range = sel.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    const section = getNearestSectionHeader(anchorNode.parentElement || anchorNode);

    setSelection({
      text,
      url: window.location.href,
      section,
      position: {
        top: rect.top + window.scrollY,
        left: rect.left + rect.width / 2,
      },
      rect: {
        top: rect.top,
        bottom: rect.bottom,
        left: rect.left,
        right: rect.right,
        width: rect.width,
        height: rect.height,
      },
    });
  }, []);

  const clearSelection = useCallback(() => {
    setSelection(null);
    window.getSelection()?.removeAllRanges();
  }, []);

  useEffect(() => {
    document.addEventListener('mouseup', handleSelectionChange);
    document.addEventListener('keyup', handleSelectionChange);

    return () => {
      document.removeEventListener('mouseup', handleSelectionChange);
      document.removeEventListener('keyup', handleSelectionChange);
    };
  }, [handleSelectionChange]);

  return { selection, clearSelection };
}
