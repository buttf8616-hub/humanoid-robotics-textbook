import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/blog',
    component: ComponentCreator('/blog', 'b2f'),
    exact: true
  },
  {
    path: '/blog/archive',
    component: ComponentCreator('/blog/archive', '182'),
    exact: true
  },
  {
    path: '/blog/authors',
    component: ComponentCreator('/blog/authors', '0b7'),
    exact: true
  },
  {
    path: '/blog/first-blog-post',
    component: ComponentCreator('/blog/first-blog-post', '89a'),
    exact: true
  },
  {
    path: '/blog/long-blog-post',
    component: ComponentCreator('/blog/long-blog-post', '9ad'),
    exact: true
  },
  {
    path: '/blog/mdx-blog-post',
    component: ComponentCreator('/blog/mdx-blog-post', 'e9f'),
    exact: true
  },
  {
    path: '/blog/tags',
    component: ComponentCreator('/blog/tags', '287'),
    exact: true
  },
  {
    path: '/blog/tags/docusaurus',
    component: ComponentCreator('/blog/tags/docusaurus', '704'),
    exact: true
  },
  {
    path: '/blog/tags/facebook',
    component: ComponentCreator('/blog/tags/facebook', '858'),
    exact: true
  },
  {
    path: '/blog/tags/hello',
    component: ComponentCreator('/blog/tags/hello', '299'),
    exact: true
  },
  {
    path: '/blog/tags/hola',
    component: ComponentCreator('/blog/tags/hola', '00d'),
    exact: true
  },
  {
    path: '/blog/welcome',
    component: ComponentCreator('/blog/welcome', 'd2b'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '/',
    component: ComponentCreator('/', '99b'),
    routes: [
      {
        path: '/',
        component: ComponentCreator('/', '9e3'),
        routes: [
          {
            path: '/',
            component: ComponentCreator('/', 'd42'),
            routes: [
              {
                path: '/intro',
                component: ComponentCreator('/intro', '32d'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-1/chapter-1-introduction-to-physical-ai',
                component: ComponentCreator('/modules/module-1/chapter-1-introduction-to-physical-ai', '984'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-1/chapter-2-embodied-intelligence-principles',
                component: ComponentCreator('/modules/module-1/chapter-2-embodied-intelligence-principles', '1ab'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-1/chapter-3-digital-physical-bridge',
                component: ComponentCreator('/modules/module-1/chapter-3-digital-physical-bridge', '115'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-2/chapter-1-ros2-architecture-fundamentals',
                component: ComponentCreator('/modules/module-2/chapter-1-ros2-architecture-fundamentals', '7c0'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-2/chapter-2-communication-patterns',
                component: ComponentCreator('/modules/module-2/chapter-2-communication-patterns', 'cb5'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-2/chapter-3-robot-modeling-urdf',
                component: ComponentCreator('/modules/module-2/chapter-3-robot-modeling-urdf', '76a'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-3/chapter-1-gazebo-simulation-environments',
                component: ComponentCreator('/modules/module-3/chapter-1-gazebo-simulation-environments', '27e'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-3/chapter-2-unity-robotics-integration',
                component: ComponentCreator('/modules/module-3/chapter-2-unity-robotics-integration', '8ee'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-3/chapter-3-sensor-simulation-integration',
                component: ComponentCreator('/modules/module-3/chapter-3-sensor-simulation-integration', 'b7c'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-4/chapter-1-isaac-sim-synthetic-data',
                component: ComponentCreator('/modules/module-4/chapter-1-isaac-sim-synthetic-data', '888'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-4/chapter-2-visual-slam-navigation',
                component: ComponentCreator('/modules/module-4/chapter-2-visual-slam-navigation', 'c86'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-4/chapter-3-ai-perception-decision-making',
                component: ComponentCreator('/modules/module-4/chapter-3-ai-perception-decision-making', 'bf4'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-5/chapter-1-vision-language-action-fundamentals',
                component: ComponentCreator('/modules/module-5/chapter-1-vision-language-action-fundamentals', 'cbc'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-5/chapter-2-multimodal-learning-for-robotics',
                component: ComponentCreator('/modules/module-5/chapter-2-multimodal-learning-for-robotics', '014'),
                exact: true,
                sidebar: "docs"
              },
              {
                path: '/modules/module-5/chapter-3-human-robot-interaction-systems',
                component: ComponentCreator('/modules/module-5/chapter-3-human-robot-interaction-systems', '556'),
                exact: true,
                sidebar: "docs"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
