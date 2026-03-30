"""
Gen72 遥操调试脚本
按住右手 grip，观察 grip 值、控制器位移、IK 求解结果
不发送任何运动指令
"""
import sys
import time
import numpy as np

sys.path.insert(0, ".")
from xrobotoolkit_teleop.common.xr_client import XrClient
from xrobotoolkit_teleop.hardware.interface.gen72 import Gen72Interface
from xrobotoolkit_teleop.utils.geometry import R_HEADSET_TO_WORLD

client = XrClient()
robot = Gen72Interface(ip="192.168.1.19", port=8080, has_gripper=False)

print("调试模式启动，按住右手 grip 键移动控制器，Ctrl+C 退出\n")

ref_xyz = None
try:
    while True:
        grip = client.get_key_value_by_name("right_grip")
        pose = client.get_pose_by_name("right_controller")
        ctrl_xyz = R_HEADSET_TO_WORLD @ np.array(pose[:3])
        q = robot.get_joint_positions()

        if grip > 0.9:
            if ref_xyz is None:
                ref_xyz = ctrl_xyz.copy()
                print(f"[ACTIVATED] grip={grip:.2f}  q={np.round(np.degrees(q),1)}")
            delta = (ctrl_xyz - ref_xyz) * 1.5
            print(f"grip={grip:.2f}  delta={np.round(delta,4)}  q={np.round(np.degrees(q),1)}")
        else:
            if ref_xyz is not None:
                print("[DEACTIVATED]")
                ref_xyz = None

        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    robot.disable_robot()
    client.close()
    print("退出")
