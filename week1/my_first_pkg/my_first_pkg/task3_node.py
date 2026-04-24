import rclpy
from rclpy.node import Node

class Task3Node(Node):
    def __init__(self):
        super().__init__('task3_node')
        self.declare_parameter('student_name', None)
        student_name = self.get_parameter('student_name').get_parameter_value().string_value
        if student_name:
            self.get_logger().info(f'Student Name: {student_name}')
        else:
            self.get_logger().info('student_name not set')

def main(args=None):
    rclpy.init(args=args)
    node = Task3Node()
    rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
