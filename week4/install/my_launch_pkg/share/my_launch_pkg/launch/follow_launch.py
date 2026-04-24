import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math

class FollowLeader(Node):

    def __init__(self):
        super().__init__('follow_leader')

        # subscribe turtle1 pose
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.callback,
            10
        )

        # publish turtle2 velocity
        self.publisher = self.create_publisher(
            Twist,
            '/turtle2/cmd_vel',
            10
        )

    def callback(self, msg):

        cmd = Twist()

        # follower logic (simple proportional control)
        cmd.linear.x = 1.5 * msg.x
        cmd.angular.z = 4.0 * math.atan2(msg.y, msg.x)

        self.publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = FollowLeader()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
