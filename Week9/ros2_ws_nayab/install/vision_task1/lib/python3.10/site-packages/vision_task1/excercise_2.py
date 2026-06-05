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

        # --- ONLY CHANGE FOR EXERCISE 2 ---
        # 🔧 Tuned kp value (experiment this for Exercise 2)
        self.kp = 0.0005

        self.center_threshold = 40
        self.approach_speed = 0.15
        self.search_speed = 0.20
        
        self.stop_area = 550000
        self.min_area = 500

        # 🔵 HSV (UNCHANGED from Exercise 1)
        self.lower_color = np.array([100, 150, 50])
        self.upper_color = np.array([140, 255, 255])

        self.get_logger().info("Exercise 2: kp tuning node started")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Image conversion failed: {e}")
            return

        img_h, img_w, _ = frame.shape
        img_cx = img_w // 2

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        valid_contours = [c for c in contours if cv2.contourArea(c) >= self.min_area]

        twist = Twist()

        if valid_contours:
            largest = max(valid_contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            M = cv2.moments(largest)

            if M["m00"] > 0:
                obj_cx = int(M["m10"] / M["m00"])
                obj_cy = int(M["m01"] / M["m00"])

                error = img_cx - obj_cx

                cv2.circle(frame, (obj_cx, obj_cy), 10, (0, 0, 255), -1)
                cv2.line(frame, (img_cx, 0), (img_cx, img_h), (255, 0, 0), 2)

                if area >= self.stop_area:
                    twist.linear.x = 0.0
                    twist.angular.z = 0.0
                    self.get_logger().info("[STOPPED] Object reached")

                elif abs(error) > self.center_threshold:
                    twist.linear.x = 0.0
                    twist.angular.z = self.kp * error
                    self.get_logger().info(f"[ALIGNING] Error: {error}")

                else:
                    twist.linear.x = self.approach_speed
                    twist.angular.z = self.kp * error
                    self.get_logger().info("[APPROACHING] Moving forward")

        else:
            twist.linear.x = 0.0
            twist.angular.z = self.search_speed
            self.get_logger().info("[SEARCHING] No object detected")

        self.publisher.publish(twist)

        cv2.imshow("Camera View", frame)
        cv2.imshow("Mask", mask)
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
        rclpy.shutdown()

if __name__ == '__main__':
    main()
