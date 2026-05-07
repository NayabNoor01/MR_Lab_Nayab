import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseWithCovarianceStamped
import time


class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')

        self._client = ActionClient(self, FollowWaypoints, 'follow_waypoints')

        # Live AMCL pose subscriber (robot position in real time)
        self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_callback,
            10
        )

        self.last_print_time = 0.0
        self.robot_pose = None

    def amcl_callback(self, msg):
        """Print robot position in real time (throttled)."""
        now = time.time()

        if now - self.last_print_time > 1.0:  # 1 sec update rate
            x = msg.pose.pose.position.x
            y = msg.pose.pose.position.y

            self.get_logger().info(
                f'📍 Robot Position -> x: {x:.2f}, y: {y:.2f}'
            )

            self.last_print_time = now
            self.robot_pose = msg.pose.pose

    def send_waypoints(self, waypoints):
        self.get_logger().info('Waiting for FollowWaypoints action server...')

        self._client.wait_for_server()

        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints

        self.get_logger().info(f'Sending {len(waypoints)} waypoints...')

        send_goal_future = self._client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by server!')
            return

        self.get_logger().info('Goal accepted. Navigating...')

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        self.get_logger().info('All waypoints reached!')


def make_pose(x, y, yaw_w):
    pose = PoseStamped()
    pose.header.frame_id = 'map'

    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0

    # (Kept exactly as manual style)
    pose.pose.orientation.z = yaw_w
    pose.pose.orientation.w = 1.0

    return pose


def main(args=None):
    rclpy.init(args=args)

    navigator = WaypointNavigator()

    # =========================
    # WAYPOINTS (FROM MANUAL)
    # =========================
    waypoints = [
        make_pose(0.5, 0.0, 1.0),   # Waypoint 1
        make_pose(1.0, 0.5, 1.0),   # Waypoint 2
        make_pose(1.0, -0.5, 1.0),  # Waypoint 3
        make_pose(0.0, -0.5, 0.0),  # Waypoint 4
        make_pose(0.0, 0.0, 1.0),   # Waypoint 5 (return)
    ]

    navigator.send_waypoints(waypoints)

    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
