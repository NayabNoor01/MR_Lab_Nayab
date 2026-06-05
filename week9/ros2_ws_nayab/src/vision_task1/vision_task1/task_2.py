#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import numpy as np


class HSVSegmentation(Node):

    def __init__(self):

        super().__init__('task_2_hsv_segmentation')

        # Subscribe to camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)

        self.bridge = CvBridge()

        self.get_logger().info("Task 2 HSV Segmentation Node Started")

    def image_callback(self, msg):

        # Step 1: Convert ROS image → OpenCV image
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Step 2: Convert BGR → HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Step 3: Define color range (RED)
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])

        # Step 4: Create mask
        mask = cv2.inRange(hsv, lower_red, upper_red)

        # Step 5: Optional noise removal (IMPORTANT IMPROVEMENT)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

        # Step 6: Show images
        cv2.imshow("Original Camera", frame)
        cv2.imshow("HSV Mask (Red Detection)", mask)

        cv2.waitKey(1)


def main(args=None):

    rclpy.init(args=args)

    node = HSVSegmentation()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
