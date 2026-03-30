"""
松灵 Piper 机械臂遥操作启动脚本

使用方法：
    # 基本运行
    python scripts/hardware/teleop_piper_hardware.py

    # 自定义 IP
    python scripts/hardware/teleop_piper_hardware.py --robot-ip 192.168.1.100

    # 启用可视化
    python scripts/hardware/teleop_piper_hardware.py --visualize-placo

    # 启用相机和数据记录
    python scripts/hardware/teleop_piper_hardware.py --enable-camera --enable-log-data
"""

import tyro
from xrobotoolkit_teleop.hardware.piper_teleop_controller import (
    DEFAULT_PIPER_MANIPULATOR_CONFIG,
    DEFAULT_PIPER_URDF_PATH,
    PiperTeleopController,
)


def main(
    robot_urdf_path: str = DEFAULT_PIPER_URDF_PATH,
    can_port: str = "can0",
    scale_factor: float = 1.5,
    enable_camera: bool = False,
    enable_log_data: bool = True,
    visualize_placo: bool = False,
    control_rate_hz: int = 50,
    log_dir: str = "logs/piper",
):
    """
    松灵 Piper 机械臂遥操作主程序

    Args:
        robot_urdf_path: URDF 文件路径
        can_port: CAN 端口名称（如 "can0", "can1"）
        scale_factor: VR 控制器移动缩放因子（建议 1.0-2.0）
        enable_camera: 是否启用 RealSense 相机
        enable_log_data: 是否记录遥操作数据
        visualize_placo: 是否可视化 IK 求解过程
        control_rate_hz: 控制频率（Hz），建议 50Hz
        log_dir: 日志保存目录
    """
    print("=" * 60)
    print("松灵 Piper 机械臂遥操作系统")
    print("=" * 60)
    print(f"CAN 端口: {can_port}")
    print(f"控制频率: {control_rate_hz} Hz")
    print(f"缩放因子: {scale_factor}")
    print(f"数据记录: {'启用' if enable_log_data else '禁用'}")
    print(f"IK 可视化: {'启用' if visualize_placo else '禁用'}")
    print("=" * 60)

    controller = PiperTeleopController(
        robot_urdf_path=robot_urdf_path,
        manipulator_config=DEFAULT_PIPER_MANIPULATOR_CONFIG,
        can_port=can_port,
        scale_factor=scale_factor,
        enable_camera=enable_camera,
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
