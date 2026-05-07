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

        # -------------------------------------------------------
        # KEY FIX: Use NavigateToPose instead of FollowWaypoints
        # NavigateToPose:
        #   - Plans a fresh global path (red line) per waypoint
        #   - Robot follows red line exactly
        #   - Only confirms REACHED when action truly succeeds
        #   - No false "waypoint reached" messages
        # -------------------------------------------------------
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._waypoints = []
        self.declare_parameter('waypoints', rclpy.parameter.Parameter.Type.DOUBLE_ARRAY)

    def get_waypoints_from_parameter(self):
        param = self.get_parameter('waypoints')
        if param.value is None:
            return None
        values = list(param.value)
        return _build_waypoints_from_flat_list(values, self, source='ROS 2 parameter')

    def feedback_callback(self, feedback_msg):
        """
        Called during navigation to a single waypoint.
        Shows distance remaining to current waypoint.
        """
        distance = feedback_msg.feedback.distance_remaining
        self.get_logger().info(
            f'Distance remaining to waypoint: {distance:.2f} m'
        )

    def navigate_to_single_waypoint(self, waypoint, waypoint_number, total):
        """
        Navigates to ONE waypoint and waits until it is truly reached.
        Returns True if reached, False if missed/failed.
        """
        x = waypoint.pose.position.x
        y = waypoint.pose.position.y
        z = waypoint.pose.position.z

        self.get_logger().info('---------------------------------------')
        self.get_logger().info(
            f'Going to Waypoint {waypoint_number} of {total}'
        )
        self.get_logger().info(
            f'Target Position -> X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}'
        )
        self.get_logger().info('---------------------------------------')

        # Build goal — stamp with current time
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = waypoint
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.header.frame_id = 'map'

        # Send goal with feedback
        send_goal_future = self._client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error(
                f'Waypoint {waypoint_number} REJECTED by Nav2 server!'
            )
            return False

        # Wait for robot to fully complete navigation to this waypoint
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result()

        # -------------------------------------------------------
        # Status 4 = SUCCEEDED in ROS 2 action goal status
        # Only print REACHED when truly succeeded
        # -------------------------------------------------------
        if result.status == 4:
            self.get_logger().info('---------------------------------------')
            self.get_logger().info(
                f'Waypoint {waypoint_number} REACHED!'
            )
            self.get_logger().info(
                f'Goal Position -> X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}'
            )
            self.get_logger().info('---------------------------------------')
            return True
        else:
            self.get_logger().warn(
                f'Waypoint {waypoint_number} NOT reached! '
                f'Nav2 Status Code: {result.status}'
            )
            self.get_logger().warn(
                f'Failed Position -> X: {x:.2f}, Y: {y:.2f}'
            )
            return False

    def send_waypoints(self, waypoints):
        self._waypoints = waypoints

        self.get_logger().info('Waiting for NavigateToPose action server...')
        self._client.wait_for_server()

        self.get_logger().info(f'Total waypoints to navigate: {len(waypoints)}')
        self.get_logger().info('========================================')

        for i, pose in enumerate(waypoints):
            x = pose.pose.position.x
            y = pose.pose.position.y
            w = pose.pose.orientation.w
            self.get_logger().info(
                f'Waypoint {i + 1} -> X: {x:.2f}, Y: {y:.2f}, W: {w:.2f}'
            )

        self.get_logger().info('========================================')
        self.get_logger().info('Starting mission...')

        total         = len(waypoints)
        reached_count = 0
        missed_list   = []

        # Navigate to each waypoint ONE BY ONE
        # Each waypoint gets its own fresh red path in RViz
        for i, waypoint in enumerate(waypoints):
            success = self.navigate_to_single_waypoint(waypoint, i + 1, total)
            if success:
                reached_count += 1
            else:
                missed_list.append(i + 1)

        # -------------------------------------------------------
        # Final mission summary
        # -------------------------------------------------------
        self.get_logger().info('======================================')

        if len(missed_list) == 0:
            self.get_logger().info(
                f'Mission Complete! All {total} waypoints reached!'
            )
        else:
            self.get_logger().info(
                f'Mission finished. '
                f'Reached: {reached_count}/{total} waypoints.'
            )
            self.get_logger().warn(
                f'Missed waypoints: {missed_list}'
            )
            for idx in missed_list:
                mp = self._waypoints[idx - 1]
                mx = mp.pose.position.x
                my = mp.pose.position.y
                self.get_logger().warn(
                    f'  Missed Waypoint {idx} -> X: {mx:.2f}, Y: {my:.2f}'
                )
            self.get_logger().warn(
                'TIP: Move missed waypoints to more open space on the map.'
            )

        self.get_logger().info('======================================')


# ======================================================================== #
#  Shared helpers
# ======================================================================== #

def make_pose(x, y, w_orient, node):
    """
    Creates a PoseStamped for Nav2 waypoint navigation.

    Arguments:
        x        : X position on the map (meters)
        y        : Y position on the map (meters)
        w_orient : Quaternion W for heading direction
        node     : ROS2 node — used to stamp the pose with current time

    Orientation quick-reference:
        Facing forward  (+X) : w_orient = 1.0  -> z_orient = 0.0
        Facing left     (+Y) : w_orient = 0.7  -> z_orient ~ 0.71
        Facing backward (-X) : w_orient = 0.0  -> z_orient = 1.0
        Facing right    (-Y) : w_orient = 0.7  -> z_orient ~ -0.71

    NOTE:
        position.z is ALWAYS 0.0 — TurtleBot3 is a flat ground robot
    """
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = node.get_clock().now().to_msg()

    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0

    w_clamped = max(-1.0, min(1.0, w_orient))
    z_orient  = math.sqrt(1.0 - w_clamped ** 2)

    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = z_orient
    pose.pose.orientation.w = w_clamped

    return pose


def _build_waypoints_from_flat_list(values, node, source='input'):
    if len(values) == 0:
        _print_usage_and_exit()

    if len(values) % 3 != 0:
        print(
            f'\n[ERROR] {source} must contain a multiple of 3 numbers, '
            f'but got {len(values)}.\n'
            f'Each waypoint needs exactly 3 values: x  y  orientation_w\n'
        )
        sys.exit(1)

    waypoints = []
    for i in range(0, len(values), 3):
        x, y, w = values[i], values[i + 1], values[i + 2]
        waypoints.append(make_pose(x, y, w, node))

    return waypoints


def _parse_argv_waypoints(node):
    raw = sys.argv[1:]

    if '--ros-args' in raw:
        raw = raw[:raw.index('--ros-args')]

    if len(raw) == 0:
        return None

    try:
        values = [float(v) for v in raw]
    except ValueError as exc:
        print(f'\n[ERROR] Non-numeric argument: {exc}\n')
        sys.exit(1)

    return _build_waypoints_from_flat_list(
        values, node, source='command-line arguments'
    )


def _print_usage_and_exit():
    print(
        '\n[ERROR] No waypoints provided.\n'
        '\n-- Option 1: python3 directly -----------------------------------\n'
        '  python3 waypoint_navigator.py  x1 y1 w1  x2 y2 w2  ...\n'
        '\n-- Option 2: ros2 run -------------------------------------------\n'
        '  ros2 run lab7_nav task_3 --ros-args \\\n'
        '      -p "waypoints:=[0.5, 0.0, 1.0, 1.0, 0.5, 0.7, 0.0, 0.0, 1.0]"\n'
        '\nEach group of THREE numbers defines one waypoint:\n'
        '  x   -> X position on the map  (meters)\n'
        '  y   -> Y position on the map  (meters)\n'
        '  w   -> Quaternion-W orientation\n'
        '         1.0=forward(+X)  0.7=left/right  0.0=backward(-X)\n'
        '\nExample (3 waypoints):\n'
        '  python3 waypoint_navigator.py 0.5 0.0 1.0  1.0 0.5 0.7  0.0 0.0 1.0\n'
    )
    sys.exit(1)


# ======================================================================== #
#  Entry point
# ======================================================================== #

def main(args=None):
    rclpy.init(args=args)
    navigator = WaypointNavigator()

    waypoints = navigator.get_waypoints_from_parameter()

    if waypoints is None:
        waypoints = _parse_argv_waypoints(navigator)

    if waypoints is None:
        navigator.destroy_node()
        rclpy.shutdown()
        _print_usage_and_exit()

    print('\n========================================')
    print('  DYNAMIC WAYPOINT MISSION')
    print(f'  Total waypoints parsed: {len(waypoints)}')
    print('========================================')
    for idx, wp in enumerate(waypoints):
        x  = wp.pose.position.x
        y  = wp.pose.position.y
        wq = wp.pose.orientation.w
        zq = wp.pose.orientation.z
        print(f'  Waypoint {idx + 1}: x={x:.2f}, y={y:.2f}, '
              f'orient_z={zq:.4f}, orient_w={wq:.4f}')
    print('========================================\n')

    navigator.send_waypoints(waypoints)
    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
