# MR Lab 6 – Reactive Navigation using LiDAR (ROS 2)

## Overview
This lab implements a reactive navigation system for TurtleBot3 in Gazebo using LiDAR data. The robot performs obstacle detection, avoidance, wall following, and behavior sequencing.

## Features
- Obstacle detection using LiDAR
- Stop-on-obstacle safety
- Obstacle avoidance (left/right decision)
- Wall following using P-controller
- Behavior sequencing

## ROS 2 Topics
- /scan (LaserScan)
- /cmd_vel (Twist)

## How to Run
colcon build
source install/setup.bash
ros2 run <your_package_name> lidar_navigator

## Simulation
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

## Files
- src/
- screenshots/
- Lab_6_Report.pdf

## Report
See Lab_6_Report.pdf for full details.
