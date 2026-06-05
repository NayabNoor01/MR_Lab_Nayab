#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class CameraFollower(Node):
    def __init__(self):
        super().__init__('camera_follower')
        
        self.subscription = self.create_subscription(
            Image, 
            '/camera/image_raw', 
            self.image_callback, 
            10
        )
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()

        # --- Tuned Control Parameters ---
        self.kp = 0.001                 # Lowered gain to prevent aggressive overshooting
        self.center_threshold = 40      # Slightly wider target window for high-res streams
        self.approach_speed = 0.15      # Linear forward speed
        self.search_speed = 0.20        # Slower search speed to prevent missing the target while spinning
        
        self.stop_area = 550000         # Large stop area for close-range termination
        self.min_area = 500             # Minimum contour area to ignore noise

        # --- HSV Thresholds (Green) ---
        self.lower_color = np.array([35, 40, 40])
        self.upper_color = np.array([90, 255, 255])
        
        self.get_logger().info('Vision-Based Target Tracking Node Started')

    def image_callback(self, msg):
        # Step 1: Convert ROS Image message to OpenCV image
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return

        img_h, img_w, _ = frame.shape
        img_cx = img_w // 2

        # Step 2: Convert to HSV and perform color segmentation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        
        # Clean up the mask using morphological operations
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        valid_contours = [c for c in contours if cv2.contourArea(c) >= self.min_area]

        twist = Twist()

        if valid_contours:
            # Step 3: Compute the centroid of the largest detected object
            largest_contour = max(valid_contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            M = cv2.moments(largest_contour)

            if M["m00"] > 0:
                obj_cx = int(M["m10"] / M["m00"])
                obj_cy = int(M["m01"] / M["m00"])
                
                # Error direction calculation
                error = img_cx - obj_cx  

                # Draw tracking lines and center dots for your Task 1 Deliverables
                cv2.circle(frame, (obj_cx, obj_cy), 10, (0, 0, 255), -1)
                cv2.line(frame, (img_cx, 0), (img_cx, img_h), (255, 0, 0), 2) 

                # Step 4 & 5: Proportional control and motion logic
                if area >= self.stop_area:
                    # Object is very close -> Stop
                    twist.linear.x = 0.0
                    twist.angular.z = 0.0
                    self.get_logger().info(f'[STOPPED] Target reached. Area: {area}')
                
                elif abs(error) > self.center_threshold:
                    # Object is off-center -> Rotate gently to align 
                    twist.linear.x = 0.0
                    twist.angular.z = self.kp * error
                    self.get_logger().info(f'[ALIGNING] Error: {error} px | Ang vel: {twist.angular.z:.3f}')
                
                else:
                    # Object is centered -> Move forward and maintain center tracking
                    twist.linear.x = self.approach_speed
                    twist.angular.z = self.kp * error
                    self.get_logger().info(f'[APPROACHING] Aligned (Error: {error} px) | Moving forward')

        else:
            # No object detected -> Spin slowly to search
            twist.linear.x = 0.0
            twist.angular.z = self.search_speed
            self.get_logger().info('[SEARCHING] Looking for target...')

        # Step 6: Publish the velocity command
        self.publisher.publish(twist)

        # Display the images (Task 1 Deliverable)
        cv2.imshow("Camera View", frame)
        cv2.imshow("Segmented Mask", mask)
        cv2.waitKey(1) 

def main(args=None):
    rclpy.init(args=args)
    node = CameraFollower()
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