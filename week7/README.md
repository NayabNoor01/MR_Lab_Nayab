# Lab 7: Autonomous Navigation with Nav2

## Overview
This lab demonstrates autonomous navigation using ROS 2 Nav2 stack with a pre-built occupancy map. The TurtleBot3 robot is localized using AMCL and navigates inside a Gazebo simulation environment.

---

## Objectives
- Load a saved occupancy map (my_map.yaml)
- Perform localization using AMCL
- Send navigation goals via RViz and CLI
- Execute multi-waypoint missions
- Observe global and local costmaps
- Analyze Nav2 recovery behaviors

---

## Tools Used
- ROS 2 Humble
- Nav2 Navigation Stack
- TurtleBot3 Burger
- Gazebo Simulator
- RViz Visualization Tool

---

## How to Run

### 1. Launch Simulation
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

### 2. Launch Navigation Stack
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$HOME/maps/my_map.yaml

### 3. Teleoperation (Optional)
ros2 run turtlebot3_teleop teleop_keyboard

---

## Tasks Performed

### Task 1: Single Goal Navigation
- Sent navigation goals via RViz and CLI
- Observed start and end poses using /amcl_pose

### Task 2: Multi-Waypoint Navigation
- Executed predefined waypoint mission using Nav2 FollowWaypoints

### Task 3: Dynamic Waypoint Navigation
- Implemented runtime waypoint input using NavigateToPose

### Task 4: Costmap Observation
- Observed global and local costmaps during navigation

### Task 5: Recovery Behaviors
- Tested obstacle avoidance and recovery strategies (spin, back-up, replan, wait)

---

## Detailed Report
A complete explanation of all tasks, code, results, and observations is provided in:

Lab_7_Report.pdf

---

## Repository Structure
week7/
 ├── screenshots/
 ├── Lab_7_Report.pdf
 ├── README.md
 └── src/


