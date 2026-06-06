import React, { useEffect } from 'react';
import Layout from '@theme/Layout';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { Redirect } from '@docusaurus/router';
import Link from '@docusaurus/Link';

// This is the main entry page for the Physical AI & Humanoid Robotics textbook
export default function Home() {
  const {siteConfig} = useDocusaurusContext();

  // Option 1: Redirect to the documentation intro page immediately
  // return <Redirect to="/docs/intro" />;

  /* Option 2: Alternative - Keep the home page with direct access to the book content */
  return (
    <Layout
      title={`Physical AI & Humanoid Robotics`}
      description="A comprehensive guide to Physical AI and Humanoid Robotics">
      <header className="hero hero--primary">
        <div className="container">
          <h1 className="hero__title">Physical AI & Humanoid Robotics</h1>
          <p className="hero__subtitle">A Comprehensive Technical Guide to Humanoid Robotics</p>

          <div style={{marginTop: '2rem'}}>
            <Link
              className="button button--secondary button--lg"
              to="/intro">
              Start Reading the Book
            </Link>
          </div>
        </div>
      </header>

      <main style={{padding: '2rem 0'}}>
        <div className="container">
          <div className="row">
            <div className="col col--4">
              <h2>Module 1: Physical AI Fundamentals</h2>
              <p>Foundational concepts of embodied intelligence and Physical AI for humanoid robotics.</p>
            </div>
            <div className="col col--4">
              <h2>Module 2: ROS 2 Robotic Nervous System</h2>
              <p>Architecture and communication patterns for humanoid robot control systems.</p>
            </div>
            <div className="col col--4">
              <h2>Module 3: Simulation Environment</h2>
              <p>Gazebo, Unity, and Isaac Sim for realistic humanoid robot simulation.</p>
            </div>
          </div>

          <div className="row" style={{marginTop: '2rem'}}>
            <div className="col col--4">
              <h2>Module 4: AI Perception & Decision Making</h2>
              <p>Vision-language-action systems and cognitive planning for humanoid robots.</p>
            </div>
            <div className="col col--8">
              <h2>About This Book</h2>
              <p>This comprehensive guide covers the complete development stack for creating AI-powered humanoid robots. Each module builds upon the previous ones to provide a complete understanding of humanoid robotics, from foundational concepts to advanced AI integration.</p>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}
