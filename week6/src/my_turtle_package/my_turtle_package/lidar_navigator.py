import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np

class LidarNavigator(Node):

    def __init__(self):
        super().__init__('lidar_navigator')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # TODO: Define thresholds
        self.front_threshold = 0.5
        self.side_threshold = 0.5

    def scan_callback(self, msg):
        ranges = np.array(msg.ranges)

        # -----------------------------
        # TODO 1: Clean data (remove inf/nan)
        # -----------------------------
        ranges = np.nan_to_num(ranges, nan=0.0, posinf=10.0, neginf=0.0)

        # -----------------------------
        # TODO 2: Define regions
        # -----------------------------
        front = np.concatenate((ranges[:30], ranges[-30:]))
        left = ranges[60:120]
        right = ranges[-120:-60]

        # Compute minimum distance
        front_dist = np.min(front)
        left_dist = np.min(left)
        right_dist = np.min(right)

        twist = Twist()

        # -----------------------------
        # TODO 3: Obstacle logic
        # -----------------------------
        if front_dist < self.front_threshold:  # obstacle in front

            # -------------------------
            # TODO 4: Turn direction
            # -------------------------
            if left_dist > right_dist:  # left clearer
                twist.angular.z = 0.5
            else:
                twist.angular.z = -0.5

            twist.linear.x = 0.0

        else:
            # -------------------------
            # TODO 5: Forward motion
            # -------------------------
            twist.linear.x = 0.15
            twist.angular.z = 0.0

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = LidarNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
