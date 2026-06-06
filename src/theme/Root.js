import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import { useLocation } from '@docusaurus/router';
import { ChatProvider } from '@site/src/context/ChatContext';
import { AuthProvider } from '@site/src/context/AuthContext';
import { AuthButton } from '@site/src/components/AuthModal/AuthModal';
import ChapterActions from '@site/src/components/ChapterActions/ChapterActions';
import ChatWidget from '@site/src/components/ChatWidget';

function ChapterActionsInjector() {
  const location = useLocation();
  const [container, setContainer] = useState(null);

  useEffect(() => {
    const MOUNT_ID = 'chapter-actions-mount';

    const inject = () => {
      // Remove stale mount from previous page
      const old = document.getElementById(MOUNT_ID);
      if (old) old.remove();

      const article = document.querySelector('article');
      if (!article) {
        setContainer(null);
        return;
      }

      const div = document.createElement('div');
      div.id = MOUNT_ID;
      article.insertBefore(div, article.firstChild);
      setContainer(div);
    };

    // Small delay lets Docusaurus finish rendering the new page
    const t = setTimeout(inject, 150);
    return () => clearTimeout(t);
  }, [location.pathname]);

  if (!container) return null;
  return ReactDOM.createPortal(<ChapterActions />, container);
}

export default function Root({ children }) {
  return (
    <AuthProvider>
      <ChatProvider>
        {children}
        <ChapterActionsInjector />
        <AuthButton />
        <ChatWidget />
      </ChatProvider>
    </AuthProvider>
  );
}
