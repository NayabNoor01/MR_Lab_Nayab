import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np


class WallFollower(Node):

    def __init__(self):
        super().__init__('wall_follower')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # PARAMETERS (carefully tuned)
        self.desired_distance = 0.5
        self.Kp = 0.5
        self.front_threshold = 0.45

    def scan_callback(self, msg):

        ranges = np.array(msg.ranges)

        # clean data
        ranges = np.nan_to_num(ranges, nan=10.0, posinf=10.0, neginf=0.0)

        total = len(ranges)

        # -----------------------------
        # REGIONS
        # -----------------------------
        front = np.concatenate((ranges[:25], ranges[-25:]))
        right = ranges[int(total * 0.65):int(total * 0.85)]

        front_dist = np.min(front)
        right_dist = np.min(right)

        twist = Twist()

        # -----------------------------
        # 🚨 STRONG SAFETY (ONLY WHEN VERY CLOSE)
        # -----------------------------
        if front_dist < self.front_threshold:
            twist.linear.x = 0.0
            twist.angular.z = 0.6   # turn left
            self.publisher.publish(twist)
            return

        # -----------------------------
        # WALL FOLLOWING (RIGHT WALL ONLY)
        # -----------------------------
        error = self.desired_distance - right_dist

        twist.linear.x = 0.15

        # proportional control
        angular = self.Kp * error

        # limit oscillation
        angular = max(min(angular, 0.4), -0.4)

        twist.angular.z = angular

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = WallFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
