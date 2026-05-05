from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():

    return LaunchDescription([

        # turtlesim
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        ),
       
        Node(
          package='turtlesim',
          executable='turtle_teleop_key',
          name='teleop'
        ),
        # spawn turtle2 using service call (CORRECT METHOD)
        ExecuteProcess(
            cmd=[
                'ros2', 'service', 'call',
                '/spawn', 'turtlesim/srv/Spawn',
                "{x: 5.0, y: 5.0, theta: 0.0, name: 'turtle2'}"
            ],
            output='screen'
        ),

        # follower node
        Node(
            package='my_launch_pkg',
            executable='follow_leader',
            name='follower'
        )
    ])
