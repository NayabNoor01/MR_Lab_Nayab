import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np


class ScanProcessor(Node):

    def __init__(self):
        super().__init__('scan_processor')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.threshold = 0.5  # stop distance

    def scan_callback(self, msg):

        ranges = np.array(msg.ranges)

        # clean data
        ranges = np.nan_to_num(ranges, nan=0.0, posinf=10.0, neginf=0.0)

        # front region (same as your Task 1 style)
        front = np.concatenate((ranges[:30], ranges[-30:]))

        front_dist = np.min(front)

        self.get_logger().info(f"Front: {front_dist:.2f}")

        twist = Twist()

        # TASK 2 LOGIC
        if front_dist > self.threshold:
            twist.linear.x = 0.15   # move forward
            twist.angular.z = 0.0
        else:
            twist.linear.x = 0.0    # STOP
            twist.angular.z = 0.0

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = ScanProcessor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
