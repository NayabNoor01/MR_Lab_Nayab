import rclpy
from rclpy.node import Node
import os

class Task2Node(Node):
    def __init__(self):
        super().__init__('task2_node')
        self.counter_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "counter.txt"
        )
        self.counter = self.read_counter()
        self.counter += 1
        self.write_counter()
        self.get_logger().info(f'Run count: {self.counter}')

    def read_counter(self):
        if os.path.exists(self.counter_file):
            with open(self.counter_file, "r") as f:
                try:
                    return int(f.read())
                except ValueError:
                    return 0
        else:
            return 0

    def write_counter(self):
        with open(self.counter_file, "w") as f:
            f.write(str(self.counter))

def main(args=None):
    rclpy.init(args=args)
    node = Task2Node()
    rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
