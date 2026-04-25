import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np


class BehaviorSequencer(Node):

    def __init__(self):
        super().__init__('behavior_sequencer')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # PARAMETERS (tuned for stability)
        self.front_threshold = 0.5
        self.wall_detect_dist = 0.8
        self.desired_wall_dist = 0.5
        self.Kp = 0.5

    # -----------------------------
    # FILTERED MIN FUNCTION (IMPORTANT)
    # -----------------------------
    def get_filtered_min(self, data):
        data = data[data > 0.05]   # remove noise/zero readings
        if len(data) == 0:
            return 10.0
        return np.min(data)

    def scan_callback(self, msg):

        ranges = np.array(msg.ranges)

        # -----------------------------
        # CLEAN DATA
        # -----------------------------
        ranges = np.nan_to_num(ranges, nan=10.0, posinf=10.0, neginf=0.0)

        total = len(ranges)

        # -----------------------------
        # REGIONS
        # -----------------------------
        front = np.concatenate((ranges[:20], ranges[-20:]))
        left = ranges[int(total * 0.2):int(total * 0.4)]
        right = ranges[int(total * 0.6):int(total * 0.8)]

        # -----------------------------
        # FILTERED DISTANCES
        # -----------------------------
        front_dist = self.get_filtered_min(front)
        left_dist = self.get_filtered_min(left)
        right_dist = self.get_filtered_min(right)

        twist = Twist()

        # -----------------------------
        # 1. 🚨 OBSTACLE AVOIDANCE
        # -----------------------------
        if front_dist < self.front_threshold:

            twist.linear.x = 0.0

            if left_dist > right_dist:
                twist.angular.z = 0.6
            else:
                twist.angular.z = -0.6

            self.get_logger().info("Avoiding obstacle")

        # -----------------------------
        # 2. 🧱 WALL FOLLOWING (RIGHT)
        # -----------------------------
        elif right_dist < self.wall_detect_dist:

            error = self.desired_wall_dist - right_dist

            twist.linear.x = 0.15

            angular = self.Kp * error

            # limit angular speed (stability)
            angular = max(min(angular, 0.5), -0.5)

            twist.angular.z = angular

            self.get_logger().info("Following wall")

        # -----------------------------
        # 3. 🚗 MOVE STRAIGHT (DEFAULT)
        # -----------------------------
        else:

            twist.linear.x = 0.2
            twist.angular.z = 0.0

            self.get_logger().info("Moving straight")

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = BehaviorSequencer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
