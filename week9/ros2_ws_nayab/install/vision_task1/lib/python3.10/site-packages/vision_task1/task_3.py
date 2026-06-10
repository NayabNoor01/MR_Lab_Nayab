#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class GreenCentroidDetector(Node):
    def __init__(self):
        super().__init__('green_centroid_detector')

        # Subscribe to the TurtleBot3 Waffle onboard camera topic
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)

        self.bridge = CvBridge()
        self.get_logger().info("Task 3: Green Object Centroid Detector Node Started")

    def image_callback(self, msg):
        try:
            # 1. Convert ROS Image message to OpenCV BGR format
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            height, width, _ = frame.shape
            screen_center_x = width // 2

            # 2. Convert from BGR to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 3. Define the robust HSV range for the Gazebo Green Box
            lower_green = np.array([35, 80, 80])
            upper_green = np.array([85, 255, 255])

            # 4. Generate the binary mask
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # 5. Morphological noise removal (essential for smooth centroid calculation)
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

            # 6. Compute spatial moments of the mask
            M = cv2.moments(mask)

            # Check if any green pixels were detected (Area > 0)
            if M['m00'] > 0:
                # Calculate centroid coordinates
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])

                # Compute the error relative to the screen's horizontal center
                error_x = cx - screen_center_x

                # Log the data cleanly to the terminal
                self.get_logger().info(
                    f"Target Found -> Centroid: ({cx}, {cy}) | Screen Center X: {screen_center_x} | Error X: {error_x}"
                )

                # Draw tracking graphics on the original color camera view
                # Draw a prominent crosshair at the centroid
                cv2.drawMarker(frame, (cx, cy), (0, 0, 255), markerType=cv2.MARKER_CROSS, 
                               markerSize=25, thickness=3)
                
                # Overlay coordinate data on the display window
                cv2.putText(frame, f"Centroid: X={cx}, Y={cy}", (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"Error X: {error_x} px", (20, 70), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                self.get_logger().info("Searching for target... No green object detected in view.")
                cv2.putText(frame, "Target Lost", (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # 7. Render both display channels
            cv2.imshow("Original Camera View (Tracking)", frame)
            cv2.imshow("HSV Mask (Green Detection)", mask)

            # Refresh graphics windows
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Image frame processing encountered an error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = GreenCentroidDetector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
