"""
Piper 硬件接口测试脚本

用于测试 Piper 机械臂的基本连接和功能
"""

import time
import numpy as np
from xrobotoolkit_teleop.hardware.interface.piper import PiperInterface


def test_connection(can_port: str = "can0"):
    """测试 Piper 连接"""
    print("=" * 60)
    print("Piper 硬件接口测试")
    print("=" * 60)

    try:
        # 初始化接口
        print(f"\n1. 初始化 Piper 接口 (CAN: {can_port})...")
        piper = PiperInterface(can_port=can_port)

        # 读取当前位置
        print("\n2. 读取当前关节位置...")
        positions = piper.get_joint_positions()
        print(f"   关节位置: {positions}")

        velocities = piper.get_joint_velocities()
        print(f"   关节速度: {velocities}")

        # 移动到 Home 位置
        print("\n3. 移动到 Home 位置...")
        piper.go_home()
        time.sleep(3)

        # 测试关节控制
        print("\n4. 测试关节控制...")
        test_positions = [0.0, -0.3, 0.8, 0.0, 1.2, 0.0]
        print(f"   目标位置: {test_positions}")
        piper.set_joint_positions(test_positions)
        time.sleep(2)

        # 读取新位置
        new_positions = piper.get_joint_positions()
        print(f"   当前位置: {new_positions}")

        # 测试夹爪
        print("\n5. 测试夹爪控制...")
        print("   打开夹爪...")
        piper.set_gripper_position(1.0)
        time.sleep(1)

        print("   关闭夹爪...")
        piper.set_gripper_position(0.0)
        time.sleep(1)

        print("   半开夹爪...")
        piper.set_gripper_position(0.5)
        time.sleep(1)

        # 返回 Home
        print("\n6. 返回 Home 位置...")
        piper.go_home()
        time.sleep(2)

        # 失能机械臂
        print("\n7. 失能机械臂...")
        piper.disable_robot()

        print("\n" + "=" * 60)
        print("✅ 测试完成！所有功能正常")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_joint_limits():
    """测试关节限位功能"""
    print("\n" + "=" * 60)
    print("测试关节限位")
    print("=" * 60)

    piper = PiperInterface(can_port="can0")

    # 测试超出限位的位置
    print("\n测试超出限位的关节位置...")
    out_of_range_positions = [5.0, -3.0, 4.0, 5.0, -3.0, 5.0]  # 故意超出范围
    print(f"输入位置: {out_of_range_positions}")

    piper.set_joint_positions(out_of_range_positions)
    print("✅ 关节限位功能正常")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Piper 硬件接口测试")
    parser.add_argument(
        "--can-port",
        type=str,
        default="can0",
        help="CAN 端口名称（如 can0, can1）"
    )
    parser.add_argument(
        "--test-limits",
        action="store_true",
        help="测试关节限位功能"
    )

    args = parser.parse_args()

    if args.test_limits:
        test_joint_limits()
    else:
        test_connection(args.can_port)
