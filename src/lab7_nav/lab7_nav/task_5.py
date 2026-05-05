import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import sys
import math


class WaypointNavigator(Node):

    def __init__(self):
        super().__init__('waypoint_navigator')

        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._waypoints = []
        self.declare_parameter('waypoints', rclpy.parameter.Parameter.Type.DOUBLE_ARRAY)

        # Task 5 monitoring
        self._start_time = None
        self._recovery_flag = False

    def get_waypoints_from_parameter(self):
        param = self.get_parameter('waypoints')
        if param.value is None:
            return None
        return _build_waypoints_from_flat_list(list(param.value), self)

    def feedback_callback(self, feedback_msg):
        distance = feedback_msg.feedback.distance_remaining

        # Detect recovery condition
        if self._start_time is not None:
            elapsed = (self.get_clock().now().nanoseconds / 1e9) - self._start_time

            if elapsed > 10.0 and distance > 0.3:
                if not self._recovery_flag:
                    self._recovery_flag = True
                    self.get_logger().warn(
                        "⚠ RECOVERY BEHAVIOR DETECTED (spin / backup / replan)"
                    )

        self.get_logger().info(f'Distance remaining: {distance:.2f} m')

    def navigate_to_single_waypoint(self, waypoint, waypoint_number, total):

        self._start_time = self.get_clock().now().nanoseconds / 1e9
        self._recovery_flag = False

        x = waypoint.pose.position.x
        y = waypoint.pose.position.y

        self.get_logger().info(f'--- Waypoint {waypoint_number}/{total} ---')
        self.get_logger().info(f'Target -> X: {x:.2f}, Y: {y:.2f}')

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = waypoint
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.header.frame_id = 'map'

        send_goal_future = self._client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected!")
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result()

        elapsed = (self.get_clock().now().nanoseconds / 1e9) - self._start_time

        self.get_logger().info(f'Time: {elapsed:.2f} sec')

        if self._recovery_flag:
            self.get_logger().warn("Recovery behavior occurred")

        if result.status == 4:
            self.get_logger().info("Waypoint reached")
            return True
        else:
            self.get_logger().warn(f"Failed with status: {result.status}")
            return False

    def send_waypoints(self, waypoints):

        self._client.wait_for_server()

        total = len(waypoints)
        reached = 0

        for i, wp in enumerate(waypoints):
            if self.navigate_to_single_waypoint(wp, i + 1, total):
                reached += 1

        self.get_logger().info(f"Mission: {reached}/{total} reached")


# ================= HELPERS =================

def make_pose(x, y, w, node):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = node.get_clock().now().to_msg()

    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0

    w = max(-1.0, min(1.0, w))
    z = math.sqrt(1 - w**2)

    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = z
    pose.pose.orientation.w = w

    return pose


def _build_waypoints_from_flat_list(values, node):
    if len(values) % 3 != 0:
        print("Waypoints must be in groups of 3")
        sys.exit(1)

    waypoints = []
    for i in range(0, len(values), 3):
        waypoints.append(make_pose(values[i], values[i+1], values[i+2], node))

    return waypoints


def _parse_argv_waypoints(node):
    raw = sys.argv[1:]

    if '--ros-args' in raw:
        raw = raw[:raw.index('--ros-args')]

    if not raw:
        return None

    return _build_waypoints_from_flat_list([float(v) for v in raw], node)


# ================= MAIN =================

def main(args=None):
    rclpy.init(args=args)

    node = WaypointNavigator()

    waypoints = node.get_waypoints_from_parameter()

    if waypoints is None:
        waypoints = _parse_argv_waypoints(node)

    if waypoints is None:
        print("No waypoints provided")
        return

    node.send_waypoints(waypoints)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
