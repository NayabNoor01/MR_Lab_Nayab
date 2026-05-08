# Lab 7: Autonomous Navigation with Nav2

## Overview
This lab demonstrates autonomous navigation using the ROS 2 Nav2 stack with a pre-built map. The TurtleBot3 robot is localized using AMCL and navigates to goals and multiple waypoints inside a Gazebo simulation.

## Objectives
- Load saved map
- Perform localization using AMCL
- Send navigation goals
- Execute waypoint missions
- Observe costmaps
- Analyze recovery behaviors

## Tools Used
- ROS 2 Humble
- Nav2
- TurtleBot3
- Gazebo
- RViz

## How to Run

1. Launch simulation:
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

2. Launch Nav2:
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$HOME/maps/my_map.yaml

3. Teleop (optional):
ros2 run turtlebot3_teleop teleop_keyboard

## Tasks
- Single goal navigation
- Multi-waypoint navigation
- Dynamic waypoint navigation
- Costmap observation
- Recovery behavior testing

## Detailed Report
A complete and detailed explanation of all tasks, observations, code implementations, and results is provided in:

Lab_7_Report.pdf

## Repository Structure
week7/
 ├── screenshots/
 ├── Lab_7_Report.pdf
 └── src/

