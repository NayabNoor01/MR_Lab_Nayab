import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
import math


class PosePrinter(Node):
    def __init__(self):
        super().__init__('pose_printer')

        self.sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.callback,
            10
        )

    def quat_to_yaw(self, x, y, z, w):
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        return math.atan2(siny_cosp, cosy_cosp)

    def callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        z = msg.pose.pose.position.z

        q = msg.pose.pose.orientation
        yaw = self.quat_to_yaw(q.x, q.y, q.z, q.w)

        # CLEAN OUTPUT ONLY
        print(f"X: {x:.3f} | Y: {y:.3f} | Z: {z:.3f} | Yaw: {yaw:.3f}")


def main():
    rclpy.init()
    node = PosePrinter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()