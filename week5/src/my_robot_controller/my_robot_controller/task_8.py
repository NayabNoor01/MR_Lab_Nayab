import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CmdVelToggle(Node):

    def __init__(self):
        super().__init__('cmd_vel_toggle')

        # Publisher to /cmd_vel
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        # Timer every 2 seconds
        self.timer = self.create_timer(2.0, self.timer_callback)

        # State (toggle between moving and stopping)
        self.move = True

        self.get_logger().info("CmdVel Toggle Node Started")

    def timer_callback(self):
        msg = Twist()

        if self.move:
            # Move forward
            msg.linear.x = 0.2
            msg.angular.z = 0.0
            self.get_logger().info("Moving Forward")
        else:
            # Stop robot
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info("Stopping")

        # Publish message
        self.publisher_.publish(msg)

        # Toggle state
        self.move = not self.move


def main(args=None):
    rclpy.init(args=args)

    node = CmdVelToggle()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
