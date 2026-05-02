import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class MoveToLocation(Node):
    def __init__(self):
        super().__init__('move_to_location')

        # Target location
        self.target_x = 8.0
        self.target_y = 5.0

        # Publisher to control turtle velocity
        self.vel_pub = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)

        # Subscriber to get current turtle position
        self.pose_sub = self.create_subscription(Pose, 'turtle1/pose', self.pose_callback, 10)

        self.current_pose = None
        self.timer = self.create_timer(0.1, self.move_turtle)  # 10 Hz

    def pose_callback(self, msg):
        self.current_pose = msg

    def move_turtle(self):
        if self.current_pose is None:
            return

        # Compute distance and angle to target
        dx = self.target_x - self.current_pose.x
        dy = self.target_y - self.current_pose.y
        distance = math.sqrt(dx**2 + dy**2)
        angle_to_target = math.atan2(dy, dx)

        # Stop if close enough
        if distance < 0.1:
            msg = Twist()
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.vel_pub.publish(msg)
            self.get_logger().info(f'Turtle reached target: x={self.target_x}, y={self.target_y}')
            rclpy.shutdown()
            return

        # Create Twist message
        msg = Twist()
        msg.linear.x = 1.5 * distance          # Move faster if far
        msg.angular.z = 4.0 * (angle_to_target - self.current_pose.theta)  # Rotate toward target

        self.vel_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    move_node = MoveToLocation()
    rclpy.spin(move_node)
    move_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
