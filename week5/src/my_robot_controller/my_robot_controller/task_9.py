import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class OdomSubscriber(Node):

    def __init__(self):
        super().__init__('odom_subscriber')

        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.callback,
            10
        )

        self.get_logger().info("Odom Subscriber Node Started")

    def callback(self, msg):
        # Extract position
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        z = msg.pose.pose.position.z

        # Extract orientation
        ox = msg.pose.pose.orientation.x
        oy = msg.pose.pose.orientation.y
        oz = msg.pose.pose.orientation.z
        ow = msg.pose.pose.orientation.w

        self.get_logger().info(
            f"Position -> x: {x:.2f}, y: {y:.2f}, z: {z:.2f}"
        )
        self.get_logger().info(
            f"Orientation -> x: {ox:.2f}, y: {oy:.2f}, z: {oz:.2f}, w: {ow:.2f}"
        )


def main():
    rclpy.init()
    node = OdomSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
