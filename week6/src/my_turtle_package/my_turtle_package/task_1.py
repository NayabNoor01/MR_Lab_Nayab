import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import numpy as np

class ScanProcessor(Node):

    def __init__(self):
        super().__init__('scan_processor')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

    def scan_callback(self, msg):

        ranges = np.array(msg.ranges)

        # Clean data
        ranges = np.nan_to_num(ranges, nan=0.0, posinf=10.0, neginf=0.0)

        # Regions
        front = np.concatenate((ranges[:30], ranges[-30:]))
        left = ranges[60:120]
        right = ranges[-120:-60]

        # Min distances
        front_dist = np.min(front)
        left_dist = np.min(left)
        right_dist = np.min(right)

        # Print results
        self.get_logger().info(
            f"Front: {front_dist:.2f}, Left: {left_dist:.2f}, Right: {right_dist:.2f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = ScanProcessor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
