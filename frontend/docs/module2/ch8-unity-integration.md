---
title: 'Chapter 8 - Unity Integration for Robot Simulation'
description: 'Integrating Unity for advanced robot simulation and visualization'
---

# Chapter 8: Unity Integration for Robot Simulation

## Learning Objectives

After reading this chapter, you will be able to:
- Integrate Unity with ROS 2 for robot simulation and visualization
- Design and implement realistic humanoid robot models in Unity
- Create sensor visualization systems for various sensor types
- Implement interactive interfaces for robot control and monitoring
- Develop VR/AR interfaces for robot operation and training
- Optimize Unity performance for real-time robot simulation
- Validate Unity simulation accuracy against real robot behavior
- Deploy Unity applications for different platforms and use cases

## Introduction

Unity provides a powerful platform for advanced visualization and simulation of humanoid robots. Its high-fidelity rendering capabilities, physics engine, and support for VR/AR make it ideal for creating immersive interfaces and realistic robot simulation environments. This chapter explores how to integrate Unity with ROS 2 and robotics systems to create advanced visualization and control interfaces for humanoid robots.

## Unity-ROS Integration Architecture

### Overview of Unity-ROS Connection

Unity can communicate with ROS 2 through several methods:

1. **TCP Socket Communication**: Using the ROS TCP Connector package
2. **HTTP-based Communication**: REST API interface (less common)
3. **DDS Native Integration**: Direct DDS communication (advanced)

For robotics applications, the TCP socket approach is most prevalent as it provides good performance while maintaining flexibility.

### Setting Up Unity-ROS Connection

```csharp
// ROSConnectionManager.cs
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Geometry;
using RosMessageTypes.Sensor;
using RosMessageTypes.Nav;
using System.Collections.Generic;
using System.Threading.Tasks;

public class ROSConnectionManager : MonoBehaviour
{
    [Header("ROS Connection Settings")]
    public string rosIPAddress = "127.0.0.1";
    public int rosPort = 10000;
    public bool useWebsocket = false;
    
    [Header("Topic Configuration")]
    public string jointStatesTopic = "/joint_states";
    public string cmdVelTopic = "/cmd_vel";
    public string laserScanTopic = "/scan";
    public string imuTopic = "/imu/data";
    
    private ROSConnection rosConnection;
    private Dictionary<string, float[]> jointPositions;
    private float[] currentJointPositions;
    private Transform robotRoot;
    
    [Header("Performance Settings")]
    public int updateFrequency = 30;  // Hz
    public bool enableSensorVisualization = true;
    
    void Start()
    {
        // Get the ROS connection singleton
        rosConnection = ROSConnection.instance;
        rosConnection.RosIPAddress = rosIPAddress;
        rosConnection.RosPort = rosPort;
        
        // Initialize dictionaries
        jointPositions = new Dictionary<string, float[]>();
        currentJointPositions = new float[0];
        
        // Find the robot root in the scene
        robotRoot = GameObject.FindGameObjectWithTag("Robot")?.transform;
        
        if(robotRoot == null)
        {
            Debug.LogError("Robot root not found in scene. Make sure there's a game object tagged as 'Robot'");
        }
        
        // Subscribe to ROS topics
        rosConnection.Subscribe<JointStateMsg>(jointStatesTopic, JointStateCallback);
        rosConnection.Subscribe<LaserScanMsg>(laserScanTopic, LaserScanCallback);
        rosConnection.Subscribe<ImuMsg>(imuTopic, ImuCallback);
        rosConnection.Subscribe<OdometryMsg>("/odom", OdomCallback);
        
        Debug.Log($"Connected to ROS at {rosIPAddress}:{rosPort}");
        Debug.Log($"Subscribed to topics: {jointStatesTopic}, {laserScanTopic}, {imuTopic}");
    }
    
    void JointStateCallback(JointStateMsg jointStateMsg)
    {
        // Update joint positions
        if(jointStateMsg.position.Length == jointStateMsg.name.Length)
        {
            for(int i = 0; i < jointStateMsg.name.Length; i++)
            {
                string jointName = jointStateMsg.name[i];
                float jointPosition = (float)jointStateMsg.position[i];
                
                // Update the corresponding joint in Unity
                UpdateJointInModel(jointName, jointPosition);
            }
        }
        
        // Store for reference
        currentJointPositions = new float[jointStateMsg.position.Length];
        for(int i = 0; i < jointStateMsg.position.Length; i++)
        {
            currentJointPositions[i] = (float)jointStateMsg.position[i];
        }
    }
    
    void LaserScanCallback(LaserScanMsg laserScanMsg)
    {
        if(enableSensorVisualization)
        {
            VisualizeLiDARData(laserScanMsg);
        }
    }
    
    void ImuCallback(ImuMsg imuMsg)
    {
        if(enableSensorVisualization)
        {
            VisualizeIMUData(imuMsg);
        }
    }
    
    void OdomCallback(OdometryMsg odomMsg)
    {
        // Update robot position and orientation
        var pose = odomMsg.pose.pose;
        
        if(robotRoot != null)
        {
            robotRoot.position = new Vector3((float)pose.position.x, (float)pose.position.y, (float)pose.position.z);
            robotRoot.rotation = new Quaternion((float)pose.orientation.x, (float)pose.orientation.y, 
                                               (float)pose.orientation.z, (float)pose.orientation.w);
        }
    }
    
    void UpdateJointInModel(string jointName, float position)
    {
        if(robotRoot == null) return;
        
        // Find the joint in the robot model
        Transform jointTransform = robotRoot.FindRecursive(jointName);  // Extension method to find by name recursively
        if(jointTransform != null)
        {
            // For revolute joints, apply rotation
            if(IsRevoluteJoint(jointName))
            {
                // Apply rotation around the joint's local Z axis (common configuration)
                jointTransform.localEulerAngles = new Vector3(0, 0, position * Mathf.Rad2Deg);
            }
            // For prismatic joints, apply translation
            else if(IsPrismaticJoint(jointName))
            {
                // Apply translation along the joint's local Z axis
                jointTransform.localPosition = new Vector3(0, 0, position);
            }
        }
    }
    
    bool IsRevoluteJoint(string jointName)
    {
        // In a real implementation, you'd have a proper joint type registry
        // For now, use naming convention
        return jointName.Contains("_joint") && !jointName.Contains("prismatic");
    }
    
    bool IsPrismaticJoint(string jointName)
    {
        return jointName.Contains("prismatic") || jointName.Contains("linear");
    }
    
    void VisualizeLiDARData(LaserScanMsg scan)
    {
        // In a real implementation, this would visualize the LiDAR scan
        // For now, we'll use this as a placeholder
        Debug.Log($"Received LiDAR data with {scan.ranges.Length} points");
    }
    
    void VisualizeIMUData(ImuMsg imu)
    {
        // Visualize IMU data - perhaps orient an arrow to show orientation
        Debug.Log($"IMU: Orientation ({imu.orientation.x}, {imu.orientation.y}, {imu.orientation.z}, {imu.orientation.w})");
    }
    
    public void SendVelocityCommand(double linearX, double angularZ)
    {
        // Create and send velocity command to ROS
        var twistMsg = new TwistMsg();
        twistMsg.linear = new Vector3Msg(linearX, 0, 0);
        twistMsg.angular = new Vector3Msg(0, 0, angularZ);
        
        rosConnection.Send<TwistMsg>(cmdVelTopic, twistMsg);
    }
    
    void Update()
    {
        // Handle keyboard input for manual control
        float linearVel = 0;
        float angularVel = 0;
        
        if(Input.GetKey(KeyCode.W)) linearVel = 0.5f;
        if(Input.GetKey(KeyCode.S)) linearVel = -0.5f;
        if(Input.GetKey(KeyCode.A)) angularVel = 0.5f;
        if(Input.GetKey(KeyCode.D)) angularVel = -0.5f;
        
        if(linearVel != 0 || angularVel != 0)
        {
            SendVelocityCommand(linearVel, angularVel);
        }
    }
}

// Extension method to find child by name recursively
public static class TransformExtensions 
{
    public static Transform FindRecursive(this Transform parent, string name) 
    {
        if(parent.name == name)
            return parent;
            
        foreach(Transform child in parent)
        {
            Transform found = child.FindRecursive(name);
            if(found != null)
                return found;
        }
        
        return null;
    }
}