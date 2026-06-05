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

        # PID Controller gains (reduced for less oscillation)
        self.kp = 0.003   # Reduced from 0.008
        self.ki = 0.00005 # Reduced integral
        self.kd = 0.01    # Increased damping
        
        # PID variables
        self.prev_error = 0
        self.integral = 0
        
        # CRITICAL: Stop zone (1-9 pixels)
        self.stop_zone_max = 9
        
        # Variables for immediate stop
        self.should_stop = False
        self.stop_counter = 0
        
        self.get_logger().info("Green Object Tracking - IMMEDIATE STOP on small error")
        self.get_logger().info(f"Robot will STOP IMMEDIATELY when error <= {self.stop_zone_max}")

    def image_callback(self, msg):

        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        h, w, _ = frame.shape
        center_x = w // 2

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # GREEN COLOR RANGE
        lower_green = np.array([40, 70, 70])
        upper_green = np.array([80, 255, 255])

        mask = cv2.inRange(hsv, lower_green, upper_green)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

        M = cv2.moments(mask)
        cmd = Twist()
        
        # Default to zero
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0

        # ---------------- OBJECT DETECTED ----------------
        if M["m00"] > 500:

            cx = int(M["m10"] / M["m00"])
            error = center_x - cx
            
            # Draw centroid and center line
            cv2.circle(frame, (cx, h//2), 8, (0, 0, 255), -1)
            cv2.line(frame, (center_x, 0), (center_x, h), (255, 0, 0), 2)
            
            # Draw stop zone (GREEN) - entire ±9 pixel zone
            cv2.rectangle(frame, 
                         (center_x - self.stop_zone_max, 0), 
                         (center_x + self.stop_zone_max, h), 
                         (0, 255, 0), 2)
            
            # Display error
            cv2.putText(frame, f"ERROR: {error} px", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # =====================================================
            # CRITICAL FIX: IMMEDIATE STOP WHEN ERROR <= 9
            # =====================================================
            
            # Check if error is in STOP ZONE (absolute value <= 9)
            if abs(error) <= self.stop_zone_max:
                # IMMEDIATE HARD STOP - publish zero velocity
                cmd.angular.z = 0.0
                
                # Publish stop command multiple times to ensure it's received
                for _ in range(3):
                    self.publisher.publish(cmd)
                
                # Reset PID to prevent windup
                self.integral = 0
                self.prev_error = 0
                
                # Log only once when entering stop zone
                if not self.should_stop:
                    self.get_logger().warn(
                        f"✅ IMMEDIATE STOP! | error={error} (<= {self.stop_zone_max})"
                    )
                    self.should_stop = True
                
                self.stop_counter += 1
                
                # Visual feedback
                cv2.putText(frame, ">>> IMMEDIATE STOP - TARGET ACQUIRED <<<", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)
                cv2.putText(frame, f"STOPPED at error={error}", (10, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Return early to skip any movement calculations
                self.publisher.publish(cmd)
                cv2.imshow("Camera - Green Object Tracking", frame)
                cv2.imshow("Mask", mask)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    rclpy.shutdown()
                return
            
            else:
                # Error is > 9 - need to rotate
                self.should_stop = False
                self.stop_counter = 0
                
                # Calculate PID only for large errors
                # Proportional term
                p_term = self.kp * error
                
                # Integral term (limited to prevent windup)
                self.integral += error
                self.integral = np.clip(self.integral, -50, 50)
                i_term = self.ki * self.integral
                
                # Derivative term (damping)
                derivative = error - self.prev_error
                d_term = self.kd * derivative
                
                # Calculate angular velocity
                angular_z = p_term + i_term + d_term
                
                # Limit maximum angular velocity
                max_angular = 0.3
                angular_z = np.clip(angular_z, -max_angular, max_angular)
                
                # Minimum threshold
                if abs(angular_z) < 0.01:
                    angular_z = 0.0
                
                cmd.angular.z = angular_z
                self.prev_error = error
                
                # Visual feedback
                direction = "LEFT" if error > 0 else "RIGHT"
                cv2.putText(frame, f"ROTATING {direction}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"Angular speed: {angular_z:.3f}", (10, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Log rotation
                if abs(angular_z) > 0.02:
                    self.get_logger().info(
                        f"🔄 ROTATING | error={error} | angular={angular_z:.3f}"
                    )

        # ---------------- NO OBJECT ----------------
        else:
            cmd.angular.z = 0.0
            self.integral = 0
            self.prev_error = 0
            self.should_stop = False
            self.stop_counter = 0
            cv2.putText(frame, "NO OBJECT DETECTED", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Publish command
        self.publisher.publish(cmd)

        # Display
        cv2.imshow("Camera - Green Object Tracking", frame)
        cv2.imshow("Mask", mask)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            rclpy.shutdown()

    def destroy_node(self):
        stop_msg = Twist()
        self.publisher.publish(stop_msg)
        cv2.destroyAllWindows()
        super().destroy_node()


def main():
    rclpy.init()
    node = CameraFollower()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
