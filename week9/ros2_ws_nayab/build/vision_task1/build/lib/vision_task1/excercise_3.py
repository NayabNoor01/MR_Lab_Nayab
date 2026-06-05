#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge
import cv2
import numpy as np
import math


class CameraFollower(Node):
    def __init__(self):
        super().__init__('camera_follower')

        # IMAGE SUBSCRIPTION
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # ODOMETRY SUBSCRIPTION (FOR TRUE 360°)
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()

        # ---------------- CONTROL PARAMETERS ----------------
        self.kp = 0.001
        self.center_threshold = 40
        self.approach_speed = 0.15
        self.search_speed = 0.3

        self.stop_area = 550000
        self.min_area = 500

        # ---------------- BLUE HSV ----------------
        self.lower_color = np.array([100, 150, 50])
        self.upper_color = np.array([140, 255, 255])

        # ---------------- ODOM SCAN VARIABLES ----------------
        self.current_yaw = 0.0
        self.prev_yaw = None
        self.rotated_angle = 0.0
        self.searching = False

        self.get_logger().info("FINAL 360° Vision Tracking Node Started")

    # ---------------- ODOM CALLBACK ----------------
    def odom_callback(self, msg):
        q = msg.pose.pose.orientation

        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        self.current_yaw = yaw

    # ---------------- IMAGE CALLBACK ----------------
    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except:
            return

        h, w, _ = frame.shape
        center_x = w // 2

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, 1)
        mask = cv2.dilate(mask, kernel, 2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        valid = [c for c in contours if cv2.contourArea(c) >= self.min_area]

        twist = Twist()

        # ================= OBJECT FOUND =================
        if valid:

            self.searching = False
            self.prev_yaw = None
            self.rotated_angle = 0.0

            largest = max(valid, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            M = cv2.moments(largest)

            if M["m00"] > 0:
                obj_x = int(M["m10"] / M["m00"])
                error = center_x - obj_x

                cv2.circle(frame, (obj_x, 100), 10, (0, 0, 255), -1)
                cv2.line(frame, (center_x, 0), (center_x, h), (255, 0, 0), 2)

                if area >= self.stop_area:
                    twist.linear.x = 0.0
                    twist.angular.z = 0.0
                    self.get_logger().info("[STOPPED] Target reached")

                elif abs(error) > self.center_threshold:
                    twist.linear.x = 0.0
                    twist.angular.z = self.kp * error
                    self.get_logger().info(f"[ALIGNING] error={error}")

                else:
                    twist.linear.x = self.approach_speed
                    twist.angular.z = self.kp * error
                    self.get_logger().info("[APPROACHING] moving")

        # ================= NO OBJECT → TRUE 360 SCAN =================
        else:
            twist.linear.x = 0.0

            if not self.searching:
                self.searching = True
                self.prev_yaw = self.current_yaw
                self.rotated_angle = 0.0

            # compute delta yaw
            diff = self.current_yaw - self.prev_yaw

            # normalize wrap
            if diff > math.pi:
                diff -= 2 * math.pi
            elif diff < -math.pi:
                diff += 2 * math.pi

            self.rotated_angle += abs(diff)
            self.prev_yaw = self.current_yaw

            if self.rotated_angle < 6.2:
                twist.angular.z = self.search_speed
                self.get_logger().info("[SCANNING] 360° rotation...")
            else:
                twist.angular.z = 0.0
                self.get_logger().info("[SCAN COMPLETE] STOPPED")

        self.publisher.publish(twist)

        cv2.imshow("Camera View", frame)
        cv2.imshow("Mask", mask)
        cv2.waitKey(1)


def main():
    rclpy.init()
    node = CameraFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()