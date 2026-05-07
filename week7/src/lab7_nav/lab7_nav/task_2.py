import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped


class WaypointNavigator(Node):

    def __init__(self):
        super().__init__('waypoint_navigator')
        self._client = ActionClient(self, FollowWaypoints, 'follow_waypoints')
        self._waypoints = []
        self._last_printed_waypoint = -1  # tracks last printed waypoint index

    def feedback_callback(self, feedback_msg):
        """
        Called continuously during navigation.
        Prints goal position each time a new waypoint is reached.
        """
        current_index = feedback_msg.feedback.current_waypoint

        # Only print when a NEW waypoint is reached (not repeatedly)
        if current_index != self._last_printed_waypoint:
            self._last_printed_waypoint = current_index

            # Get the position of the waypoint that was just reached
            if current_index > 0:
                reached_index = current_index - 1
                reached_pose = self._waypoints[reached_index]
                x = reached_pose.pose.position.x
                y = reached_pose.pose.position.y
                z = reached_pose.pose.position.z
                self.get_logger().info(
                    f'---------------------------------------'
                )
                self.get_logger().info(
                    f'Waypoint {reached_index + 1} REACHED!'
                )
                self.get_logger().info(
                    f'Goal Position → X: {x}, Y: {y}, Z: {z}'
                )
                self.get_logger().info(
                    f'---------------------------------------'
                )

            # Print the next upcoming waypoint
            if current_index < len(self._waypoints):
                next_pose = self._waypoints[current_index]
                x = next_pose.pose.position.x
                y = next_pose.pose.position.y
                z = next_pose.pose.position.z
                self.get_logger().info(
                    f'Navigating to Waypoint {current_index + 1} ...'
                )
                self.get_logger().info(
                    f'Target Position → X: {x}, Y: {y}, Z: {z}'
                )

    def send_waypoints(self, waypoints):
        self._waypoints = waypoints

        self.get_logger().info('Waiting for FollowWaypoints action server...')
        self._client.wait_for_server()

        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints

        self.get_logger().info(
            f'Total waypoints to navigate: {len(waypoints)}'
        )
        self.get_logger().info('========================================')

        # Print all waypoint positions before mission starts
        for i, pose in enumerate(waypoints):
            x = pose.pose.position.x
            y = pose.pose.position.y
            z = pose.pose.position.z
            self.get_logger().info(
                f'Waypoint {i + 1} → X: {x}, Y: {y}, Z: {z}'
            )

        self.get_logger().info('========================================')
        self.get_logger().info('Starting mission...')

        # Send goal with feedback callback attached
        send_goal_future = self._client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by server!')
            return

        self.get_logger().info('Goal accepted. Robot is now navigating...')

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        # Print final waypoint reached
        last_pose = self._waypoints[-1]
        x = last_pose.pose.position.x
        y = last_pose.pose.position.y
        z = last_pose.pose.position.z
        self.get_logger().info('---------------------------------------')
        self.get_logger().info(
            f'Waypoint {len(self._waypoints)} REACHED!'
        )
        self.get_logger().info(
            f'Goal Position → X: {x}, Y: {y}, Z: {z}'
        )
        self.get_logger().info('---------------------------------------')
        self.get_logger().info('======================================')
        self.get_logger().info('Mission Complete! All waypoints reached!')
        self.get_logger().info('======================================')


def make_pose(x, y, z_orient, w_orient):
    """
    Creates a PoseStamped message for Nav2 waypoint navigation.

    Arguments:
        x        : X position on the map (meters)
        y        : Y position on the map (meters)
        z_orient : Quaternion Z for heading direction
        w_orient : Quaternion W for heading direction

    NOTE:
        position.z is ALWAYS 0.0
        TurtleBot3 is a ground robot — it never moves vertically.

    Orientation Guide:
        Facing forward  (+X) : z_orient=0.0,  w_orient=1.0
        Facing left     (+Y) : z_orient=0.7,  w_orient=0.7
        Facing backward (-X) : z_orient=1.0,  w_orient=0.0
        Facing right    (-Y) : z_orient=-0.7, w_orient=0.7
    """
    pose = PoseStamped()
    pose.header.frame_id = 'map'

    # ----- POSITION -----
    pose.pose.position.x = x        # Changes for every waypoint
    pose.pose.position.y = y        # Changes for every waypoint
    pose.pose.position.z = 0.0      # ALWAYS 0.0 — never change this

    # ----- ORIENTATION (Quaternion) -----
    pose.pose.orientation.x = 0.0   # ALWAYS 0.0 for 2D ground robot
    pose.pose.orientation.y = 0.0   # ALWAYS 0.0 for 2D ground robot
    pose.pose.orientation.z = z_orient   # Controls heading direction
    pose.pose.orientation.w = w_orient   # Controls heading direction

    return pose


def main(args=None):
    rclpy.init(args=args)
    navigator = WaypointNavigator()

    # ============================================================
    # 5 WAYPOINTS FOR MULTI-WAYPOINT MISSION
    #
    # make_pose( X,    Y,    z_orient, w_orient )
    #
    # position.z is ALWAYS 0.0 inside make_pose() — never changes
    # Only X and Y positions change between waypoints
    # ============================================================

    waypoints = [

        make_pose(0.5,  0.0,  0.0,  1.0),
        # Waypoint 1: Move forward from origin
        # position  → x=0.5, y=0.0, z=0.0 (fixed)
        # heading   → facing forward (+X direction)

        make_pose(1.0,  0.5,  0.0,  0.7),
        # Waypoint 2: Top-right area of map
        # position  → x=1.0, y=0.5, z=0.0 (fixed)
        # heading   → facing left (+Y direction)

        make_pose(1.0, -0.5, 0.0,  0.7),
        # Waypoint 3: Bottom-right area of map
        # position  → x=1.0, y=-0.5, z=0.0 (fixed)
        # heading   → facing right (-Y direction)

        make_pose(0.0, -0.5,  0.0,  0.0),
        # Waypoint 4: Bottom-left area of map
        # position  → x=0.0, y=-0.5, z=0.0 (fixed)
        # heading   → facing backward (-X direction)

        make_pose(0.0,  0.0,  0.0,  1.0),
        # Waypoint 5: Return back to origin
        # position  → x=0.0, y=0.0, z=0.0 (fixed)
        # heading   → facing forward (+X direction)

    ]

    navigator.send_waypoints(waypoints)
    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
