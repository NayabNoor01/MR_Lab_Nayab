import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn
import time

class MultiTurtle(Node):
    def __init__(self):
        super().__init__('multi_turtle')

        # Publishers
        self.pub1 = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.pub2 = self.create_publisher(Twist, 'turtle2/cmd_vel', 10)
        self.pub3 = self.create_publisher(Twist, 'turtle3/cmd_vel', 10)

        # Spawn turtle2 and turtle3
        self.spawn_turtle(2, 5.0, 5.0, 0.0)
        self.spawn_turtle(3, 8.0, 8.0, 0.0)

        # Counters to control steps
        self.turtle2_step = 0
        self.turtle3_step = 0

        # Timer to update turtles every 0.5 seconds
        self.timer = self.create_timer(0.5, self.move_turtles)

    def spawn_turtle(self, number, x, y, theta):
        client = self.create_client(Spawn, 'spawn')
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for spawn service...')
        request = Spawn.Request()
        request.x = x
        request.y = y
        request.theta = theta
        request.name = f'turtle{number}'
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info(f'Spawned turtle: {future.result().name}')

    def move_turtles(self):
        
        msg1 = Twist()
        msg1.linear.x = 2.0
        msg1.angular.z = 1.0
        self.pub1.publish(msg1)

        
        msg2 = Twist()
        if self.turtle2_step % 2 == 0:
            msg2.linear.x = 2.0
            msg2.angular.z = 0.0
        else:
            msg2.linear.x = 0.0
            msg2.angular.z = 2.094  # 120 degrees
        self.pub2.publish(msg2)
        self.turtle2_step += 1

        
        msg3 = Twist()
        if self.turtle3_step % 2 == 0:
            msg3.linear.x = 2.0
            msg3.angular.z = 0.0
        else:
            msg3.linear.x = 0.0
            msg3.angular.z = 1.57  # 90 degrees
        self.pub3.publish(msg3)
        self.turtle3_step += 1

        # Optional: stop after some steps
        if self.turtle2_step > 6 and self.turtle3_step > 8:
            stop_msg = Twist()
            self.pub1.publish(stop_msg)
            self.pub2.publish(stop_msg)
            self.pub3.publish(stop_msg)
            self.get_logger().info('All turtles finished patterns.')
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    multi_turtle = MultiTurtle()
    rclpy.spin(multi_turtle)
    multi_turtle.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
