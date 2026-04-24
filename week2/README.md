# MCT-454L Mobile Robotics – Lab 2: ROS 2 & Turtlesim

Welcome to Lab 2 of MCT-454L! In this lab, we explore ROS 2 nodes, topics, and services using the Turtlesim simulator, and get hands-on experience with the rqt GUI.

This lab is designed to help you see how ROS 2 works in real-time. You’ll control turtles, send commands, call services, and visualize the system’s behavior—all in one interactive session.

## Objective

- Get comfortable with ROS 2 command-line tools.
- Understand how a simulated robot behaves.
- Control turtles using topics and services.
- Explore the ROS 2 ecosystem visually using rqt.
- Observe real-time effects of commands and service calls.

## Lab Highlights

- Launch Turtlesim and move the turtle with keyboard teleop.
- Explore ROS 2 topics to see position and velocity updates.
- Send velocity commands programmatically with `ros2 topic pub`.
- Call services to reset simulation, spawn new turtles, teleport them, and change the background color.
- Visualize nodes, topics, and services with the rqt GUI.
- Control multiple turtles independently, demonstrating ROS 2’s multi-node capabilities.

## Setup Instructions

1. Source ROS 2 environment:


source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

2. Install Turtlesim (if needed):

sudo apt install ros-humble-turtlesim

3. Launch Turtlesim:

ros2 run turtlesim turtlesim_node

4. Control the turtle with teleop:

ros2 run turtlesim turtle_teleop_key

5. Explore topics and services using the terminal or rqt.

## Deliverables

- Screenshots of rqt service calls (`/reset`, `/spawn`).
- Short report explaining steps followed and observations (included in this repo).
