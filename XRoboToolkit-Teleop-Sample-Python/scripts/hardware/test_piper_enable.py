#!/usr/bin/env python3
"""测试Piper机械臂使能状态"""

import sys
sys.path.insert(0, '/home/dora/teleop_pico/XRoboToolkit-Teleop-Sample-Python')

from piper_sdk import C_PiperInterface
import time

def main():
    print("初始化Piper...")
    piper = C_PiperInterface()
    piper.ConnectPort("can0")
    print("CAN端口连接成功")

    # 检查当前使能状态
    print("\n检查当前使能状态...")
    status = piper.GetArmEnableStatus()
    print(f"使能状态: {status}")

    # 尝试使能所有关节
    print("\n尝试使能所有关节...")
    piper.EnableArm(7)
    time.sleep(1)

    # 再次检查状态
    status = piper.GetArmEnableStatus()
    print(f"使能后状态: {status}")

    # 如果第6个关节没有使能，单独尝试
    if not status[5]:
        print("\n第6个关节未使能，尝试单独使能...")
        piper.EnableArm(6, 1)  # 单独使能第6个关节
        time.sleep(1)
        status = piper.GetArmEnableStatus()
        print(f"单独使能后状态: {status}")

    # 读取关节位置
    print("\n读取关节位置...")
    positions = piper.GetArmJointMsgs()
    print(f"关节位置: {positions}")

    print("\n测试完成")

if __name__ == "__main__":
    main()
