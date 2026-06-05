#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry          # <-- ADDED
from cv_bridge import CvBridge
import cv2
import numpy as np
import math                                # <-- ADDED


class Exercise4MultiColorFollower(Node):

    def __init__(self):
        super().__init__('multi_color_follower')

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # --- ADDED: Odometry subscription for true 360° scan tracking ---
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()

        # --- Control & Motion Parameters ---
        self.kp = 0.001               # Proportional gain for centering tracking
        self.center_threshold = 40
        self.approach_speed = 0.15
        self.search_speed = 0.20
        self.stop_area = 550000       # Stopping threshold for the green target
        self.min_area = 800

        # --- HSV Color Spectrum Ranges ---
        # Green Target
        self.lower_green = np.array([35, 30, 30])
        self.upper_green = np.array([85, 255, 255])

        # Red Barrier (Dual bounds combined to handle wrap-around)
        self.lower_red1 = np.array([0, 50, 30])
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([170, 50, 30])
        self.upper_red2 = np.array([180, 255, 255])

        # Blue Spin Trigger
        self.lower_blue = np.array([100, 50, 30])
        self.upper_blue = np.array([130, 255, 255])

        # --- ADDED: Odometry scan state variables ---
        self.current_yaw = 0.0
        self.prev_yaw = None
        self.rotated_angle = 0.0
        self.searching = False

        self.get_logger().info('Exercise 4 Node Initialized — Blue Precision Centered Stop Active')

    # --- ADDED: Odometry callback to track yaw angle ---
    def odom_callback(self, msg):
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        self.current_yaw = yaw

    def analyze_mask(self, mask):
        """Applies morphological cleanup and finds the largest contour features."""
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        valid_contours = [c for c in contours if cv2.contourArea(c) >= self.min_area]
        if valid_contours:
            largest = max(valid_contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            M = cv2.moments(largest)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return True, area, (cx, cy), mask
        return False, 0, (0, 0), mask

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Failed to convert frame: {e}")
            return

        img_h, img_w, _ = frame.shape
        img_cx = img_w // 2

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Process masks for all three target colors
        green_valid, green_area, green_pt, green_mask = self.analyze_mask(
            cv2.inRange(hsv, self.lower_green, self.upper_green))
        blue_valid, blue_area, blue_pt, blue_mask = self.analyze_mask(
            cv2.inRange(hsv, self.lower_blue, self.upper_blue))

        # Merge lower and upper red wrappers
        r_mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        r_mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        red_valid, red_area, red_pt, red_mask = self.analyze_mask(cv2.bitwise_or(r_mask1, r_mask2))

        twist = Twist()

        # --- Behavior Priority Tree Rules ---

        if red_valid:
            # Reset scan state since an obstacle is found
            self.searching = False
            self.prev_yaw = None
            self.rotated_angle = 0.0

            obj_cx, obj_cy = red_pt
            error = img_cx - obj_cx

            # RULE 1: Red Detected -> Stay centered on the centroid and move BACKWARD
            twist.linear.x = -0.15
            twist.angular.z = self.kp * error
            self.get_logger().warn(
                f'[RED OBSTACLE] Centroid Found at X: {obj_cx} | Moving backward away from box.')

            # Draw targeting overlays
            cv2.circle(frame, red_pt, 15, (0, 0, 255), -1)
            cv2.line(frame, (img_cx, 0), (img_cx, img_h), (255, 0, 0), 2)
            cv2.putText(frame, "RED CENTROID FOUND: BACKING AWAY", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        elif blue_valid:
            # Reset scan state since an obstacle is found
            self.searching = False
            self.prev_yaw = None
            self.rotated_angle = 0.0

            obj_cx, obj_cy = blue_pt
            error = img_cx - obj_cx

            # RULE 2: Blue Detected -> Rotate until centered, then stop cleanly
            if abs(error) > self.center_threshold:
                # If not perfectly centered yet, turn in place to face it directly
                twist.linear.x = 0.0
                twist.angular.z = self.kp * error
                self.get_logger().info(
                    f'[BLUE TRACKING] Aligning to Centroid X: {obj_cx}. Error: {error}px')
                cv2.putText(frame, "BLUE: ALIGNING TO CENTROID", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
            else:
                # Perfectly facing the center of the blue box -> Absolute Stop
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.get_logger().info(
                    f'[BLUE OBSTACLE] Centroid Centered at X: {obj_cx} | Stopped cleanly.')
                cv2.putText(frame, "BLUE CENTROID MATCHED: STOPPED", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            # Draw targeting overlays
            cv2.circle(frame, blue_pt, 15, (255, 0, 0), -1)
            cv2.line(frame, (img_cx, 0), (img_cx, img_h), (255, 0, 0), 2)

        elif green_valid:
            # Reset scan state since an obstacle is found
            self.searching = False
            self.prev_yaw = None
            self.rotated_angle = 0.0

            # RULE 3: Green Detected -> Proportional Tracking, Forward Approach, and Range Stop
            obj_cx, obj_cy = green_pt
            error = img_cx - obj_cx

            cv2.circle(frame, green_pt, 15, (0, 255, 0), -1)
            cv2.line(frame, (img_cx, 0), (img_cx, img_h), (255, 0, 0), 2)
            cv2.putText(frame, "GREEN: TRACK & APPROACH", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            if green_area >= self.stop_area:
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.get_logger().info(f'[GREEN ACTION] Destination reached! Stopping.')
            elif abs(error) > self.center_threshold:
                twist.linear.x = 0.0
                twist.angular.z = self.kp * error
                self.get_logger().info(f'[GREEN ACTION] Aligning to target center.')
            else:
                twist.linear.x = self.approach_speed
                twist.angular.z = self.kp * error
                self.get_logger().info(f'[GREEN ACTION] Approaching target forward.')

        else:
            # --- MODIFIED: Odometry-tracked 360° scan. Stops after full rotation if nothing found ---
            twist.linear.x = 0.0

            # Initialize scan session on first entry
            if not self.searching:
                self.searching = True
                self.prev_yaw = self.current_yaw
                self.rotated_angle = 0.0

            # Accumulate delta yaw with wrap-around normalization
            if self.prev_yaw is not None:
                diff = self.current_yaw - self.prev_yaw
                if diff > math.pi:
                    diff -= 2 * math.pi
                elif diff < -math.pi:
                    diff += 2 * math.pi
                self.rotated_angle += abs(diff)
                self.prev_yaw = self.current_yaw

            if self.rotated_angle < 6.2:
                # Full 360° not yet complete — keep rotating
                twist.angular.z = self.search_speed
                self.get_logger().info(
                    f'[SEARCHING] 360 scan in progress... '
                    f'{math.degrees(self.rotated_angle):.1f} deg covered.')
                cv2.putText(frame, "SEARCHING WORLD...", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            else:
                # Full 360° complete and still no obstacle found — stop completely
                twist.angular.z = 0.0
                self.get_logger().info(
                    '[SCAN COMPLETE] Full 360 done. No obstacle found. Stopped.')
                cv2.putText(frame, "SCAN COMPLETE: NO TARGET FOUND", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

        # Publish velocity commands to the TurtleBot
        self.publisher.publish(twist)

        # Generate combined UI windows
        combined_mask = cv2.bitwise_or(red_mask, cv2.bitwise_or(green_mask, blue_mask))
        cv2.imshow("Multi-Color Tracking Feed", frame)
        cv2.imshow("Combined Segmented Mask", combined_mask)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = Exercise4MultiColorFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(Twist())
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

