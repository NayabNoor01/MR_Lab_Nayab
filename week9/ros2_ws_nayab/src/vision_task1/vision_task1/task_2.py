#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class GreenObjectSegmenter(Node):
    def __init__(self):
        super().__init__('green_object_segmenter')

        # Subscribe to the camera topic
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)

        self.bridge = CvBridge()
        self.get_logger().info("Task 2: Green Object Segmentation Node Started")

    def image_callback(self, msg):
        try:
            # 1. Convert ROS Image message to OpenCV format (BGR)
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # 2. Convert the image from BGR to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 3. Define the HSV range for the color GREEN
            # Hue for green is around 60. Range 35-85 captures it well in Gazebo.
            lower_green = np.array([35, 80, 80])
            upper_green = np.array([85, 255, 255])

            # 4. Create the binary mask
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # 5. Clean up the mask (Noise removal using morphological operations)
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

            # 6. Display the original frame and the isolated green mask
            cv2.imshow("Original Camera View", frame)
            cv2.imshow("HSV Mask (Green Detection)", mask)

            # Required to refresh the OpenCV windows
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Image processing failed: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = GreenObjectSegmenter()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Allows you to stop the node cleanly with Ctrl+C
        pass
    finally:
        # Ensure OpenCV windows close cleanly when the node stops
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
