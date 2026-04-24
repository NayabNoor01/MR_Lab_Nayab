**Week 1 Lab Answers**

**Definitions:**

**Node**  
A node is a small program in a robotic system that performs one specific task. For example, it might read sensor data or control a motor. Each node focuses on doing its job well.

**Topic**  
A topic is a communication channel between nodes. It allows them to send and receive messages. This helps different parts of the system share information smoothly.

**Package**  
A package is an organized folder that contains related code, libraries, and configuration files. It groups everything needed for a specific function in one place. This makes development and maintenance easier.

**Workspace**  
A workspace is the main directory where multiple packages are stored and built together. It acts like a project environment. All development and testing usually happen inside the workspace.

**Why Sourcing a Workspace Is Important**  
Sourcing is required because it tells your system where to find the files and tools in your workspace.  
When you run the “source” command, you update your environment. You’re basically saying, “Hey, use this workspace.”  
Without sourcing, your terminal has no idea your new packages even exist. It won’t recognize your nodes. It won’t find your custom messages. Things that should run smoothly will suddenly fail, and that can feel confusing. You might see errors like “command not found” or “package not found.” That doesn’t always mean your code is wrong. Often, it just means the workspace wasn’t sourced.  
Think of sourcing like activating your project. If you skip it, the system falls back to the default setup. And your work stays invisible.

**What Is the Purpose of colcon build?**  
colcon build is used to compile and build the packages inside your workspace.  
It takes your source code and turns it into something the system can actually run.  
When you write code, it just sits there as text files. Nothing happens yet.  
When you run colcon build, the system processes that code. It compiles C++ files. It prepares Python packages. It organizes dependencies. In short, it gets everything ready for execution.  
Without building, your nodes won’t run. Even if your code is perfect.

**What Folders Does It Generate?**  
After running colcon build, you’ll notice three new folders in your workspace:

build  
This folder contains temporary build files. It’s where the compilation process happens.

install  
This is the important one. It stores the final built packages that your system will use after sourcing.

log  
This folder keeps log files. If something goes wrong, you can check here to see what happened.

**What Does entry_points (console script) Do in setup.py?**  
The entry_points console script connects your Python file to a terminal command. Without it, you would have to run the Python file directly. That can be messy. You’d need the full file path. And it wouldn’t feel integrated with the system.  
When you define a console script in setup.py, you’re basically saying, “When someone types this command, run this function from this file.”  
For example, you might map:  
talker = my_package.my_node:main  
Now, when you type ros2 run my_package talker, the system knows exactly which function to execute. It jumps straight to main() in that file.  
So in simple terms, entry_points makes your node executable from the command line. It turns your Python script into a proper ROS2 command.

**ROS2 Publisher-Subscriber Connection (ASCII Diagram)**

```
+-----------------+                          +-----------+                         +------------------+
|   Publisher     |     publishes messages   |  Topic    |     receives messages   |   Subscriber     |
|    (Node A)     |  --------------------->  |  /chatter |  ---------------------> |    (Node B)      |
|                 |                          |           |                         |                  |
|  - generates    |                          |  - message|                         |  - processes     |
|    data         |                          |    queue  |                         |    data          |
+-----------------+                          +-----------+                         +------------------+
```
The Publisher (Node A) creates and sends data.  
The Topic (/chatter) acts as a communication channel and temporarily holds the messages.  
The Subscriber (Node B) listens to the topic and processes the received data.

