import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/nayab/Lab_9/ros2_ws_nayab/install/vision_task1'
