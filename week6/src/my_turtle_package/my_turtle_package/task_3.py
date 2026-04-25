import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np


class ObstacleAvoidance(Node):

    def __init__(self):
        super().__init__('obstacle_avoidance')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # thresholds
        self.front_threshold = 0.6

    def scan_callback(self, msg):

        ranges = np.array(msg.ranges)

        # clean data
        ranges = np.nan_to_num(ranges, nan=10.0, posinf=10.0, neginf=0.0)

        total = len(ranges)

        # -----------------------------
        # REGION SPLITTING
        # -----------------------------
        front = np.concatenate((ranges[:30], ranges[-30:]))
        left = ranges[int(total*0.25):int(total*0.45)]
        right = ranges[int(total*0.55):int(total*0.75)]

        # minimum distances
        front_dist = np.min(front)
        left_dist = np.min(left)
        right_dist = np.min(right)

        self.get_logger().info(
            f"F:{front_dist:.2f} L:{left_dist:.2f} R:{right_dist:.2f}"
        )

        twist = Twist()

        # -----------------------------
        # TASK 3 LOGIC
        # -----------------------------

        if front_dist < self.front_threshold:
            # OBSTACLE AHEAD → MUST TURN

            twist.linear.x = 0.0

            # choose direction with more space
            if left_dist > right_dist:
                twist.angular.z = 0.6   # turn left
            else:
                twist.angular.z = -0.6  # turn right

        else:
            # CLEAR PATH → MOVE FORWARD

            twist.linear.x = 0.15
            twist.angular.z = 0.0

        self.publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoidance()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
