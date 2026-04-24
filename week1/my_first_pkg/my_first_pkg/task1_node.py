import rclpy
from rclpy.node import Node

class Task1Node(Node):
    def __init__(self):
        super().__init__('task1_node')
        self.get_logger().info('Welcome to Mobile Robotics Lab')

def main(args=None):
    rclpy.init(args=args)
    node = Task1Node()
    rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
