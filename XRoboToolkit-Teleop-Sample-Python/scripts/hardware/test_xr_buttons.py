#!/usr/bin/env python3
"""测试XR按钮数据获取"""

import time
import sys
sys.path.insert(0, '/home/dora/teleop_pico/XRoboToolkit-Teleop-Sample-Python')

from xrobotoolkit_teleop.common.xr_client import XrClient

def main():
    print("初始化XR客户端...")
    xr_client = XrClient()

    print("\n开始读取XR数据（按Ctrl+C退出）...")
    print("请按下手柄上的grip和trigger按钮进行测试\n")

    try:
        while True:
            # 获取位置数据
            right_pose = xr_client.get_pose_by_name("right_controller")

            # 获取按钮数据
            right_grip = xr_client.get_key_value_by_name("right_grip")
            right_trigger = xr_client.get_key_value_by_name("right_trigger")

            print(f"\r位置: [{right_pose[0]:.3f}, {right_pose[1]:.3f}, {right_pose[2]:.3f}] | "
                  f"Grip: {right_grip:.3f} | Trigger: {right_trigger:.3f}", end="")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n测试结束")
        xr_client.close()

if __name__ == "__main__":
    main()
