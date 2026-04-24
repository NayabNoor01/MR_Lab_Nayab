# MCT-454L: Mobile Robotics Lab — ROS 2 & GitHub Basics

This lab is all about getting comfortable with the ROS 2 environment, from setting up a clean workspace and managing code on GitHub to actually moving things around in turtlesim. I’ve included a custom Python node here that sends velocity commands to a turtle to make it follow specific paths. The main goal was to bridge the gap between writing raw code and seeing physical (well, simulated) motion.

## How to get this running

- Prepare the workspace: Clone this into your ~/ros2_ws/src folder.

- Build it: Go back to the root ~/ros2_ws and run colcon build.

- Source it: Don't forget to run source install/setup.bash or you'll get "package not found" errors.

- Launch: Fire up the turtlesim_node in one tab and run ros2 run my_turtle_package my_node in another.

## What's inside?

- Version Control: My workflow for pushing changes to GitHub.

- Turtle Control: The Python logic used to translate geometry messages into movement.

- The Challenges: Code snippets and logic for drawing circles, triangles, and handling multiple turtles at once.
