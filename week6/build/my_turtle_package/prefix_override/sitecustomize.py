import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/nayab/Lab_6/ros2_ws_nayab/install/my_turtle_package'
