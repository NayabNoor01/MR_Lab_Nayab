import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class VelocityPublisher(Node):

    def __init__(self):
        super().__init__('velocity_publisher')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        msg = Twist()

        # Move forward
        msg.linear.x = 2.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)
        time.sleep(2)

        # Turn 90 degrees
        msg.linear.x = 0.0
        msg.angular.z = 1.57
        self.publisher_.publish(msg)
        time.sleep(1)


def main(args=None):
    rclpy.init(args=args)
    node = VelocityPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
