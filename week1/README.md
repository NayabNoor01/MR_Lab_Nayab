# Week 1 – Linux Onboarding, ROS 2 Setup, and First Node

## Overview

This lab focused on setting up a ROS 2 development environment and creating my first working node.
I created a workspace (`~/ros2_ws`), built a Python package (`my_first_pkg`), and successfully executed a node using `ros2 run`.

The goal was simple: understand the workflow.
Create → Build → Source → Run.

---

## Commands Used

Below are the main commands I used during the lab:

\`\`\`bash
# Source ROS 2
source /opt/ros/humble/setup.bash

# Create workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build
source install/setup.bash

# Create package
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_first_pkg

# Build again
cd ~/ros2_ws
colcon build
source install/setup.bash

# Run node
ros2 run my_first_pkg simple_node
\`\`\`

---

## Problems Faced and Solutions

At first, `ros2` was not recognized.
The issue was that the environment was not sourced. I fixed it using:

\`\`\`bash
source /opt/ros/humble/setup.bash
\`\`\`

Later, my package did not appear in `ros2 pkg list`.
I had forgotten to rebuild and source after editing `setup.py`. Rebuilding solved the problem.

Small mistakes.
But useful lessons.

---

## Reflection

This lab helped me understand how ROS 2 is structured.

I learned the importance of sourcing the environment every time. That step is critical.
I also understood how `colcon build` prepares the workspace and how `entry_points` connects a Python file to a runnable command.

Creating and running my first node felt simple, but it clarified many concepts.
Now the workflow makes sense.

Overall, this lab gave me confidence in using the terminal and managing a ROS 2 workspace.

