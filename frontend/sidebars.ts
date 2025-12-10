import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Physical AI & Humanoid Robotics',
      items: [
        'intro',
        {
          type: 'category',
          label: 'Module 1: The Robotic Nervous System (ROS 2)',
          items: [
            'module1/ch1-intro-physical-ai',
            'module1/ch2-ros2-architecture',
            'module1/ch3-building-ros2-packages',
            'module1/ch4-urdf-robot-description',
            'module1/exercise-set1'
          ],
        },
        {
          type: 'category',
          label: 'Module 2: The Digital Twin (Gazebo & Unity)',
          items: [
            'module2/ch5-gazebo-simulation',
            'module2/ch6-physics-collision-simulation',
            'module2/ch7-sensor-simulation',
            'module2/ch8-unity-integration',
            'module2/exercise-set2'
          ],
        },
        {
          type: 'category',
          label: 'Module 3: The AI-Robot Brain (NVIDIA Isaac)',
          items: [
            'module3/ch9-isaac-sim-setup',
            'module3/ch10-perception-navigation',
            'module3/ch11-ai-manipulation-planning',
            'module3/exercise-set3'
          ],
        },
        {
          type: 'category',
          label: 'Module 4: Vision-Language-Action (VLA)',
          items: [
            'module4/ch12-voice-action-pipelines',
            'module4/ch13-cognitive-planning',
            'module4/ch14-capstone-autonomous-humanoid',
            'module4/exercise-set4'
          ],
        }
      ],
    },
  ],
};

export default sidebars;
