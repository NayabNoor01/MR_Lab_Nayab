#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class GreenProportionalAligner(Node):
    def __init__(self):
        super().__init__('green_proportional_aligner')

        # 1. Image Subscriber
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)

        # 2. Velocity Publisher
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()
        
        # --- TUNED CONTROLLER PARAMETERS ---
        # Lowered Kp to prevent the robot from overshooting the stop zone due to inertia
        self.kp = 0.0015  
        
        # Stop zone set exactly to your 12-pixel requirement
        self.stop_threshold = 12 

        self.get_logger().info("Task 4: Stateless Proportional Alignment Node Active")
        self.get_logger().info(f"Target stop zone configured at: +/- {self.stop_threshold} pixels")

    def image_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV BGR format
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            h, w, _ = frame.shape
            center_x = w // 2

            # HSV Segmentation for Green Object
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_green = np.array([35, 80, 80])
            upper_green = np.array([85, 255, 255])
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # Clean mask noise using Morphological Operations
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

            # Initialize a fresh, clean velocity command
            cmd = Twist()
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

            # Calculate spatial moments
            M = cv2.moments(mask)

            # Lowered area check to 200 to catch the obstacle even if moved further away
            if M["m00"] > 200:
                cx = int(M["m10"] / M["m00"])
                
                # Proportional error calculation: (Screen Center - Object Center)
                error = center_x - cx  

                # Visual Feedback: Plot center line, target center, and target boundary zone
                cv2.circle(frame, (cx, h // 2), 8, (0, 0, 255), -1)
                cv2.line(frame, (center_x, 0), (center_x, h), (255, 0, 0), 2)
                
                # Draw the visual green bounds for your 12px stop zone
                cv2.rectangle(frame, (center_x - self.stop_threshold, 0), (center_x + self.stop_threshold, h), (0, 255, 0), 2)
                cv2.putText(frame, f"Current Error: {error} px", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # --- STATELESS PROPORTIONAL CONTROL CONTROLLER ---
                if abs(error) <= self.stop_threshold:
                    # Force a hard structural brake
                    cmd.angular.z = 0.0
                    cv2.putText(frame, "HOLDING POSITION (ALIGNED)", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    self.get_logger().info(f"Target Aligned (Error: {error} px). Holding position until obstacle moves.")
                else:
                    # Apply Proportional Control Equation: U = Kp * error
                    angular_velocity = self.kp * error
                    
                    # Safe ceiling limit to ensure controlled movement approach
                    max_speed = 0.3
                    cmd.angular.z = np.clip(angular_velocity, -max_speed, max_speed)
                    
                    direction = "LEFT" if error > 0 else "RIGHT"
                    cv2.putText(frame, f"ALIGNING: TURNING {direction}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    self.get_logger().info(f"Tracking active -> Error: {error} px | Speed Z: {cmd.angular.z:.4f}")
            else:
                # --- THIS IS THE ONLY CHANGE ---
                # No object tracked: Rotate continuously to search for the green object
                cmd.angular.z = 0.2  # Slow rotation to scan the room
                cv2.putText(frame, "SEARCHING: ROTATING TO FIND TARGET", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                self.get_logger().info("Searching... Rotating to find green object.")

            # Publish velocity command and refresh windows
            self.publisher.publish(cmd)
            cv2.imshow("Camera View (Task 4 Alignment)", frame)
            cv2.imshow("Mask Display", mask)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Image loop execution error: {e}")

    def destroy_node(self):
        # Publish absolute zero velocity upon exit to safely halt the robot base
        stop_msg = Twist()
        self.publisher.publish(stop_msg)
        cv2.destroyAllWindows()
        super().destroy_node()

def main():
    rclpy.init()
    node = GreenProportionalAligner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
