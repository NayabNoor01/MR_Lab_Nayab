# 📘 MR Lab Report 8  
## Building and Visualizing a Custom Mobile Robot using URDF (ROS 2)
---

# 🎯 Objective

- Understand the Unified Robot Description Format (URDF) and its role in ROS 2 robot modeling.  
- Design a custom mobile robot using links and joints in URDF.  
- Build a robot structure including base chassis, wheels, and sensor links.  
- Learn how to define robot components such as links, joints, and materials.  
- Visualize the robot model in RViz using ROS 2 tools.  
- Inspect coordinate relationships using TF Tree via `tf2_tools`.  
- Gain hands-on experience in preparing robot descriptions for Gazebo simulation.  
- Develop foundational understanding for robot simulation and control systems.  

---

# 📌 Introduction

In robotics, a robot must be described mathematically and geometrically before simulation or hardware implementation. The **Unified Robot Description Format (URDF)** is the standard XML-based format used in ROS 2 for this purpose.

URDF represents a robot as a tree of:
- **Links** → rigid bodies (chassis, wheels, sensors)  
- **Joints** → define motion between links  

ROS 2 tools such as `robot_state_publisher`, `RViz`, and `tf2_tools` use URDF to:
- Publish coordinate transformations (TF)
- Visualize robot models in 3D
- Validate robot structure

---

# 🧪 Lab Summary

This lab focused on designing and visualizing a custom mobile robot using URDF in ROS 2. The robot was successfully built, launched, and visualized in RViz.

Key steps included:
- Creating a structured ROS 2 workspace  
- Writing a custom URDF robot model  
- Launching robot visualization in RViz  
- Using joint state publisher for interaction  
- Generating and analyzing TF Tree using `tf2_tools`  

The robot model was rendered successfully in RViz, confirming correct URDF configuration and frame broadcasting.

---

# 🤖 Custom Robot Design

A mobile robot was designed with the following components:

### 🧱 Base Chassis
- Rounded shape using two overlapping boxes and four corner cylinders  
- Dimensions: 0.34 × 0.30 × 0.10 m  
- Color: Yellow  

### 📷 Camera Link
- Cylinder-shaped sensor  
- Mounted on top of base using fixed joint  
- Height offset: 0.075 m  

### ⚙️ Left & Right Wheels
- Dark black cylindrical wheels  
- Attached using continuous joints  
- Positioned symmetrically on both sides  
- Enable rotation for differential drive  

### 🛞 Front Caster Wheel
- Sphere geometry  
- Passive support wheel for stability  
- Mounted under front of base  

---

# 🧾 URDF Concepts Used

## 🔹 Links
Each robot part is defined as a `<link>` (base, wheels, camera, caster).

## 🔹 Joints
Define relationship between links:
- **fixed** → no movement (camera, caster)  
- **continuous** → infinite rotation (wheels)  

## 🔹 Materials
Defined using RGBA colors:
- Yellow → robot body  
- Dark Black → wheels  

---

# 🌳 TF Tree

The TF Tree generated using `tf2_tools` confirms:
- Correct parent-child relationships  
- Proper frame transformations  
- Valid robot structure from `base_link` to all child links  

---

# ⚙️ Customizations Made

- Designed rounded chassis using combined primitives  
- Applied yellow and black color scheme  
- Added front caster wheel for balance  
- Positioned wheels for differential drive motion  
- Added camera link as sensor representation  
- Structured robot in realistic mobile robot layout  

---

# 🧠 Conclusion

- Successfully designed and implemented a custom URDF mobile robot  
- Understood link-joint structure in ROS 2  
- Visualized robot in RViz using ROS tools  
- Verified TF hierarchy using TF Tree  
- Learned differences between fixed and continuous joints  
- Gained hands-on experience in ROS 2 workspace setup  
- Prepared foundation for Gazebo simulation and sensor integration  

---

# 🚀 Additional Note

This repository contains the **complete implementation of Lab 8 URDF robot**, including all required files, launch setup, RViz configuration, screenshots, and a detailed summary of the robot design and visualization process.

---
