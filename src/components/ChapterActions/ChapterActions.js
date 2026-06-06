import React, { useState, useCallback } from 'react';
import { useAuth } from '@site/src/context/AuthContext';
import { AuthModal } from '@site/src/components/AuthModal/AuthModal';
import styles from './ChapterActions.module.css';

function ResultModal({ title, icon, content, loading, onClose }) {
  const [copied, setCopied] = useState(false);

  const copyText = () => {
    navigator.clipboard.writeText(content || '').then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={styles.resultModal}>
        <div className={styles.resultHeader}>
          <h3 className={styles.resultTitle}>
            <span>{icon}</span> {title}
          </h3>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        {loading ? (
          <div className={styles.loading}>
            <span className={styles.dot} />
            <span className={styles.dot} />
            <span className={styles.dot} />
            <span>Processing with AI... this may take 10–20 seconds</span>
          </div>
        ) : (
          <>
            <div
              className={styles.resultBody}
              dangerouslySetInnerHTML={{ __html: markdownToHtml(content || '') }}
            />
            <div className={styles.resultFooter}>
              <button className={styles.copyBtn} onClick={copyText}>
                {copied ? '✓ Copied' : 'Copy Text'}
              </button>
              <span className={styles.resultNote}>
                AI-generated — verify against original chapter
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function markdownToHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    .replace(/\n\n+/g, '</p><p>')
    .replace(/^(?!<[hul]|<block)(.+)$/gm, (m) => (m.trim() ? m : ''))
    .replace(/\n/g, '<br>');
}

function getPageContent() {
  const article = document.querySelector('article');
  if (!article) return document.title;
  const clone = article.cloneNode(true);
  clone.querySelectorAll('.chapterActionsBar, nav, .pagination-nav').forEach((el) => el.remove());
  return clone.innerText || clone.textContent || '';
}

export default function ChapterActions() {
  const { user, getToken, getApiUrl } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [modal, setModal] = useState(null); // { type, title, icon, content, loading }

  const openModal = (type, title, icon) =>
    setModal({ type, title, icon, content: '', loading: true });

  const closeModal = () => setModal(null);

  const callApi = useCallback(
    async (endpoint, body) => {
      const token = getToken();
      const r = await fetch(`${getApiUrl()}/api/v1/content/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || `${endpoint} failed`);
      return data.result;
    },
    [getToken, getApiUrl]
  );

  const handlePersonalize = useCallback(async () => {
    if (!user) { setShowAuthModal(true); return; }
    const content = getPageContent();
    const title = document.title || 'Chapter';
    openModal('personalize', 'Personalized for You', '🎯');
    try {
      const result = await callApi('personalize', { content, chapter_title: title });
      setModal((m) => ({ ...m, content: result, loading: false }));
    } catch (err) {
      setModal((m) => ({
        ...m,
        content: `**Error:** ${err.message}\n\nPlease make sure the backend is running.`,
        loading: false,
      }));
    }
  }, [user, callApi]);

  const handleTranslate = useCallback(async () => {
    if (!user) { setShowAuthModal(true); return; }
    const content = getPageContent();
    const title = document.title || 'Chapter';
    openModal('translate', 'اردو ترجمہ — Urdu Translation', '🌐');
    try {
      const result = await callApi('translate', { content, chapter_title: title });
      setModal((m) => ({ ...m, content: result, loading: false }));
    } catch (err) {
      setModal((m) => ({
        ...m,
        content: `**Error:** ${err.message}\n\nPlease make sure the backend is running.`,
        loading: false,
      }));
    }
  }, [user, callApi]);

  return (
    <>
      <div className={`${styles.bar} chapterActionsBar`}>
        <span className={styles.label}>AI Tools:</span>

        <button
          className={`${styles.btn} ${styles.btnPersonalize}`}
          onClick={handlePersonalize}
          title={user ? `Personalise for ${user.name}` : 'Sign in to personalise content'}
        >
          🎯 Personalize Content
        </button>

        <button
          className={`${styles.btn} ${styles.btnTranslate}`}
          onClick={handleTranslate}
          title={user ? 'Translate chapter to Urdu' : 'Sign in to translate'}
        >
          🌐 Translate to Urdu
        </button>

        {!user && (
          <span className={styles.loginHint}>
            <button
              className={styles.loginHintBtn}
              onClick={() => setShowAuthModal(true)}
            >
              Sign in
            </button>{' '}
            to use AI features
          </span>
        )}
      </div>

      {modal && (
        <ResultModal
          title={modal.title}
          icon={modal.icon}
          content={modal.content}
          loading={modal.loading}
          onClose={closeModal}
        />
      )}

      {showAuthModal && (
        <AuthModal
          onClose={() => setShowAuthModal(false)}
          defaultMode="signin"
        />
      )}
    </>
  );
}
