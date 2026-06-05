#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import numpy as np


class HSVCentroidDetector(Node):

    def __init__(self):

        super().__init__('task_3_hsv_centroid')

        # Subscribe to camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)

        self.bridge = CvBridge()

        self.get_logger().info("Task 3 HSV Centroid Detection Node Started")

    def image_callback(self, msg):

        # Step 1: Convert ROS Image → OpenCV
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        height, width, _ = frame.shape

        # Step 2: Convert BGR → HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Step 3: RED color range (two ranges for robustness)
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        # Step 4: Mask creation
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask1 + mask2

        # Step 5: Noise removal
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

        # Step 6: Compute moments
        M = cv2.moments(mask)

        cx, cy = -1, -1

        if M["m00"] > 0:

            # ✔ CENTROID COMPUTATION (TASK 3 CORE)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Draw centroid
            cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)

            cv2.putText(frame,
                        f"Centroid: ({cx}, {cy})",
                        (cx + 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2)

            self.get_logger().info(f"Centroid: ({cx}, {cy})")

        else:
            self.get_logger().warn("No object detected")

        # Step 7: Show results
        cv2.imshow("Camera View", frame)
        cv2.imshow("Mask", mask)

        cv2.waitKey(1)


def main(args=None):

    rclpy.init(args=args)

    node = HSVCentroidDetector()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
