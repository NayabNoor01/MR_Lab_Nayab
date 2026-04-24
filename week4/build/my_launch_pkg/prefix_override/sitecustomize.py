import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/nayab/Lab_4/ros2_ws_nayab/install/my_launch_pkg'
