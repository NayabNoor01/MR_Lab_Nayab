import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Twist
from action_msgs.msg import GoalStatus

import sys
import math
import time


# ===================== PARAMETERS =====================
MAX_RECOVERY_ATTEMPTS = 5
WAIT_BETWEEN_RETRIES = 2.0
GOAL_TOLERANCE = 0.05   # realistic Nav2 tolerance
# ======================================================


class Task5RecoveryNavigator(Node):

    def __init__(self):
        super().__init__('task5_recovery_navigator')

        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.goal_handle = None

        self.declare_parameter('waypoints', [])

        self.get_logger().info("Task 5 Recovery Navigator Started")

    # ----------------------------------------------------
    def get_waypoints_from_parameter(self):
        values = list(self.get_parameter('waypoints').value)

        if len(values) == 0:
            return None

        return build_waypoints(values, self)

    # ----------------------------------------------------
    def feedback_callback(self, msg):

        d = msg.feedback.distance_remaining

        self.get_logger().info(
            f"Distance remaining: {d:.2f} m",
            throttle_duration_sec=2.0
        )

    # ----------------------------------------------------
    def navigate_to_waypoint(self, waypoint, idx, total):

        x = waypoint.pose.position.x
        y = waypoint.pose.position.y

        self.get_logger().info(f"\nWaypoint {idx}/{total} → X={x:.2f}, Y={y:.2f}")

        for attempt in range(1, MAX_RECOVERY_ATTEMPTS + 1):

            if attempt > 1:
                self.get_logger().info(f"Recovery attempt {attempt}")

            goal = NavigateToPose.Goal()
            goal.pose = waypoint

            goal.pose.header.stamp = self.get_clock().now().to_msg()
            goal.pose.header.frame_id = "map"

            send_future = self.client.send_goal_async(
                goal, feedback_callback=self.feedback_callback
            )
            rclpy.spin_until_future_complete(self, send_future)

            self.goal_handle = send_future.result()

            if not self.goal_handle.accepted:
                self.get_logger().warn("Goal rejected by Nav2")
                time.sleep(WAIT_BETWEEN_RETRIES)
                continue

            result_future = self.goal_handle.get_result_async()
            rclpy.spin_until_future_complete(self, result_future)

            result = result_future.result()
            status = result.status

            # SUCCESS
            if status == GoalStatus.STATUS_SUCCEEDED:
                self.get_logger().info(f"Waypoint {idx} reached ✅")
                return True

            # RETRY
            if attempt < MAX_RECOVERY_ATTEMPTS:
                self.get_logger().warn(
                    f"Failed (status={status}), retrying..."
                )
                time.sleep(WAIT_BETWEEN_RETRIES)
            else:
                self.get_logger().error(f"Waypoint {idx} failed ❌")

        return False

    # ----------------------------------------------------
    def stop_robot(self):

        self.get_logger().warn("Stopping robot safely...")

        # 1. Cancel Nav2 goal
        try:
            if self.goal_handle is not None:
                cancel_future = self.goal_handle.cancel_goal_async()
                rclpy.spin_until_future_complete(self, cancel_future)
               
        except Exception as e:
            self.get_logger().warn(f"Cancel error: {e}")

        # 2. Publish zero velocity
        pub = self.create_publisher(Twist, '/cmd_vel', 10)
        stop_msg = Twist()

        for _ in range(15):
            pub.publish(stop_msg)
            time.sleep(0.1)

    # ----------------------------------------------------
    def send_waypoints(self, waypoints):

        self.client.wait_for_server()

        success = 0
        total = len(waypoints)

        for i, wp in enumerate(waypoints):
            if self.navigate_to_waypoint(wp, i + 1, total):
                success += 1

        self.get_logger().info(f"\nMISSION COMPLETE: {success}/{total}")

        self.stop_robot()


# ======================================================
# Helpers
# ======================================================

def make_pose(x, y, w, node):

    pose = PoseStamped()
    pose.header.frame_id = "map"
    pose.header.stamp = node.get_clock().now().to_msg()

    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0

    w = max(-1.0, min(1.0, w))
    z = math.sqrt(1.0 - w**2)

    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = z
    pose.pose.orientation.w = w

    return pose


def build_waypoints(values, node):

    if len(values) % 3 != 0:
        print("ERROR: Waypoints must be multiple of 3 values")
        sys.exit(1)

    waypoints = []

    for i in range(0, len(values), 3):
        x = values[i]
        y = values[i + 1]
        w = values[i + 2]

        waypoints.append(make_pose(x, y, w, node))

    return waypoints


def parse_cli(node):

    args = sys.argv[1:]

    if '--ros-args' in args:
        args = args[:args.index('--ros-args')]

    if len(args) == 0:
        return None

    values = [float(v) for v in args]

    return build_waypoints(values, node)


# ======================================================
# MAIN
# ======================================================

def main(args=None):

    rclpy.init(args=args)

    node = Task5RecoveryNavigator()

    waypoints = node.get_waypoints_from_parameter()

    if waypoints is None:
        waypoints = parse_cli(node)

    if waypoints is None:
        print("Usage:")
        print("python3 task_5.py x y w x y w ...")
        sys.exit(1)

    node.send_waypoints(waypoints)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
