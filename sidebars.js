module.exports = {
  docs: [
    {
      type: 'category',
      label: 'Physical AI & Humanoid Robotics',
      items: [
        'intro',
        {
          type: 'category',
          label: 'Module 1: Physical AI Fundamentals Book Structure',
          items: [
            'modules/module-1/chapter-1-introduction-to-physical-ai',
            'modules/module-1/chapter-2-embodied-intelligence-principles',
            'modules/module-1/chapter-3-digital-physical-bridge'
          ]
        },
        {
          type: 'category',
          label: 'Module 2: ROS 2 Robotic Nervous System Content',
          items: [
            'modules/module-2/chapter-1-ros2-architecture-fundamentals',
            'modules/module-2/chapter-2-communication-patterns',
            'modules/module-2/chapter-3-robot-modeling-urdf'
          ]
        },
        {
          type: 'category',
          label: 'Module 3: Simulation Environment Content',
          items: [
            'modules/module-3/chapter-1-gazebo-simulation-environments',
            'modules/module-3/chapter-2-unity-robotics-integration',
            'modules/module-3/chapter-3-sensor-simulation-integration'
          ]
        },
        {
          type: 'category',
          label: 'Module 4: NVIDIA Isaac AI Integration Content',
          items: [
            'modules/module-4/chapter-1-isaac-sim-synthetic-data',
            'modules/module-4/chapter-2-visual-slam-navigation',
            'modules/module-4/chapter-3-ai-perception-decision-making'
          ]
        },
        {
          type: 'category',
          label: 'Module 5: Vision-Language-Action Integration Content',
          items: [
            'modules/module-5/chapter-1-vision-language-action-fundamentals',
            'modules/module-5/chapter-2-multimodal-learning-for-robotics',
            'modules/module-5/chapter-3-human-robot-interaction-systems'
          ]
        }
      ]
    }
  ]
};
