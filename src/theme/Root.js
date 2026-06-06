/**
 * Root.js - Docusaurus theme wrapper
 *
 * This component wraps the entire Docusaurus app to provide:
 * - ChatProvider for global chat state
 * - ChatWidget rendered on all pages
 *
 * @see https://docusaurus.io/docs/swizzling#wrapper-your-site-with-root
 */
import React from 'react';
import { ChatProvider } from '@site/src/context/ChatContext';
import ChatWidget from '@site/src/components/ChatWidget';

export default function Root({ children }) {
  return (
    <ChatProvider>
      {children}
      <ChatWidget />
    </ChatProvider>
  );
}
