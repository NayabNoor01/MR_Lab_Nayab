import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('velocity_publisher')
        # Publisher for turtle1/cmd_vel
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.timer_period = 0.5  # seconds
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        # Control variables
        self.pattern_stage = 'circle'  # Start with circle pattern
        self.step_count = 0

    def timer_callback(self):
        msg = Twist()

        # --- Circular pattern ---
        if self.pattern_stage == 'circle':
            msg.linear.x = 2.0       # Move forward
            msg.angular.z = 1.0      # Rotate while moving forward
            self.publisher_.publish(msg)
            self.step_count += 1
            if self.step_count >= 20:  # ~10 seconds of circular motion
                # Stop the turtle briefly before switching pattern
                msg.linear.x = 0.0
                msg.angular.z = 0.0
                self.publisher_.publish(msg)
                time.sleep(1)
                # Switch to triangular pattern
                self.pattern_stage = 'triangle'
                self.step_count = 0

        # --- Triangular pattern ---
        elif self.pattern_stage == 'triangle':
            # Move straight and turn in alternating steps
            if self.step_count % 2 == 0:
                # Move forward
                msg.linear.x = 2.0
                msg.angular.z = 0.0
                self.publisher_.publish(msg)
                time.sleep(2)  # move straight
            else:
                # Turn 120 degrees
                msg.linear.x = 0.0
                msg.angular.z = 2.094  # radians ≈ 120°
                self.publisher_.publish(msg)
                time.sleep(1)

            self.step_count += 1
            if self.step_count > 5:  # Complete 3 sides of triangle
                # Stop the turtle
                msg.linear.x = 0.0
                msg.angular.z = 0.0
                self.publisher_.publish(msg)
                rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    velocity_publisher = VelocityPublisher()
    rclpy.spin(velocity_publisher)
    velocity_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()