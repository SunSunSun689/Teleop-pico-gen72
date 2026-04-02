"""
睿曼 Gen72 双臂遥操作启动脚本

使用方法：
    # 基本运行（使用默认 IP）
    python scripts/hardware/teleop_dual_gen72_hardware.py

    # 自定义 IP
    python scripts/hardware/teleop_dual_gen72_hardware.py \
        --right-arm-ip 192.168.1.19 --left-arm-ip 192.168.1.18

    # 启用可视化
    python scripts/hardware/teleop_dual_gen72_hardware.py --visualize-placo

    # 仅连接右臂（左臂 IP 置空则跳过）
    python scripts/hardware/teleop_dual_gen72_hardware.py --left-arm-ip ""
"""

import tyro
from xrobotoolkit_teleop.hardware.dual_gen72_teleop_controller import (
    DEFAULT_DUAL_GEN72_MANIPULATOR_CONFIG,
    DEFAULT_DUAL_GEN72_URDF_PATH,
    DEFAULT_ROBOT_PORT,
    DualGen72TeleopController,
)


def main(
    robot_urdf_path: str = DEFAULT_DUAL_GEN72_URDF_PATH,
    right_arm_ip: str = "192.168.1.19",
    left_arm_ip: str = "192.168.1.20",
    robot_port: int = DEFAULT_ROBOT_PORT,
    scale_factor: float = 1.0,
    enable_log_data: bool = True,
    visualize_placo: bool = False,
    control_rate_hz: int = 50,
    log_dir: str = "logs/gen72_dual",
):
    """
    睿曼 Gen72 双臂遥操作主程序

    Args:
        robot_urdf_path: 双臂 URDF 文件路径
        right_arm_ip: 右臂 IP 地址（默认 192.168.1.19）
        left_arm_ip: 左臂 IP 地址（默认 192.168.1.18）
        robot_port: 机械臂 TCP 端口（默认 8080）
        scale_factor: VR 控制器移动缩放因子（建议 1.0-2.0）
        enable_log_data: 是否记录遥操作数据
        visualize_placo: 是否可视化 IK 求解过程
        control_rate_hz: 控制频率（Hz），建议 50Hz
        log_dir: 日志保存目录
    """
    robot_ips = {
        "right_arm": right_arm_ip,
        "left_arm": left_arm_ip,
    }

    print("=" * 60)
    print("睿曼 Gen72 双臂遥操作系统")
    print("=" * 60)
    print(f"右臂 IP: {right_arm_ip}:{robot_port}")
    print(f"左臂 IP: {left_arm_ip}:{robot_port}")
    print(f"控制频率: {control_rate_hz} Hz")
    print(f"缩放因子: {scale_factor}")
    print(f"数据记录: {'启用' if enable_log_data else '禁用'}")
    print(f"IK 可视化: {'启用' if visualize_placo else '禁用'}")
    print("=" * 60)

    controller = DualGen72TeleopController(
        robot_urdf_path=robot_urdf_path,
        manipulator_config=DEFAULT_DUAL_GEN72_MANIPULATOR_CONFIG,
        robot_ips=robot_ips,
        robot_port=robot_port,
        scale_factor=scale_factor,
        enable_log_data=enable_log_data,
        visualize_placo=visualize_placo,
        control_rate_hz=control_rate_hz,
        log_dir=log_dir,
    )

    try:
        controller.run()
    except KeyboardInterrupt:
        print("\n用户中断，正在安全关闭...")
    except Exception as e:
        print(f"\n错误: {e}")
        raise
    finally:
        print("程序结束")


if __name__ == "__main__":
    tyro.cli(main)
