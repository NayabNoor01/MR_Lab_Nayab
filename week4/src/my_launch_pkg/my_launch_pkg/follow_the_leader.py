import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math

class Follower(Node):

    def __init__(self):
        super().__init__('follower')

        self.leader_pose = None
        self.follower_pose = None

        # store path history
        self.path = []

        self.create_subscription(Pose, '/turtle1/pose', self.leader_callback, 10)
        self.create_subscription(Pose, '/turtle2/pose', self.follower_callback, 10)

        self.pub = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        self.timer = self.create_timer(0.1, self.control_loop)

    def leader_callback(self, msg):
        self.leader_pose = msg

        # store leader path
        self.path.append((msg.x, msg.y))

        # keep limited memory
        if len(self.path) > 50:
            self.path.pop(0)

    def follower_callback(self, msg):
        self.follower_pose = msg

    def control_loop(self):
        if self.leader_pose is None or self.follower_pose is None:
            return

        # follow OLD point instead of current (KEY FIX)
        if len(self.path) < 10:
            return

        target_x, target_y = self.path[0]

        dx = target_x - self.follower_pose.x
        dy = target_y - self.follower_pose.y

        distance = math.sqrt(dx**2 + dy**2)
        angle_to_target = math.atan2(dy, dx)

        angle_error = angle_to_target - self.follower_pose.theta

        # normalize angle
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

        cmd = Twist()

        # proportional control
        cmd.linear.x = 2.0 * distance
        cmd.angular.z = 6.0 * angle_error

        # remove point when reached
        if distance < 0.2:
            self.path.pop(0)

        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = Follower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
