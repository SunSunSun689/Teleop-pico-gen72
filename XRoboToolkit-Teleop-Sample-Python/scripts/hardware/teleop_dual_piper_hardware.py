"""
松灵 Piper 双臂遥操作启动脚本

使用方法：
    # 基本运行（默认 can0 右臂，can1 左臂）
    python scripts/hardware/teleop_dual_piper_hardware.py

    # 自定义 CAN 端口
    python scripts/hardware/teleop_dual_piper_hardware.py \
        --right-can-port can0 --left-can-port can1

    # 启用 IK 可视化
    python scripts/hardware/teleop_dual_piper_hardware.py --visualize-placo

    # 禁用数据记录
    python scripts/hardware/teleop_dual_piper_hardware.py --no-enable-log-data
"""

import tyro
from xrobotoolkit_teleop.hardware.dual_piper_teleop_controller import (
    DualPiperTeleopController,
    DEFAULT_RIGHT_CAN_PORT,
    DEFAULT_LEFT_CAN_PORT,
)
from xrobotoolkit_teleop.hardware.piper_teleop_controller import (
    DEFAULT_PIPER_URDF_PATH,
    DEFAULT_SCALE_FACTOR,
)


def main(
    robot_urdf_path: str = DEFAULT_PIPER_URDF_PATH,
    right_can_port: str = DEFAULT_RIGHT_CAN_PORT,
    left_can_port: str = DEFAULT_LEFT_CAN_PORT,
    scale_factor: float = DEFAULT_SCALE_FACTOR,
    visualize_placo: bool = False,
    control_rate_hz: int = 50,
    enable_log_data: bool = True,
    log_dir: str = "logs/piper_dual",
):
    """
    松灵 Piper 双臂遥操作主程序

    Args:
        robot_urdf_path: Piper URDF 文件路径
        right_can_port: 右臂 CAN 端口（默认 can0）
        left_can_port: 左臂 CAN 端口（默认 can1）
        scale_factor: VR 控制器移动缩放因子
        visualize_placo: 是否可视化 IK 求解过程
        control_rate_hz: 控制频率（Hz）
        enable_log_data: 是否记录遥操作数据
        log_dir: 日志保存目录
    """
    print("=" * 60)
    print("松灵 Piper 双臂遥操作系统")
    print("=" * 60)
    print(f"右臂 CAN: {right_can_port}")
    print(f"左臂 CAN: {left_can_port}")
    print(f"控制频率: {control_rate_hz} Hz")
    print(f"缩放因子: {scale_factor}")
    print(f"数据记录: {'启用' if enable_log_data else '禁用'}")
    print(f"IK 可视化: {'启用' if visualize_placo else '禁用'}")
    print("=" * 60)

    controller = DualPiperTeleopController(
        robot_urdf_path=robot_urdf_path,
        right_can_port=right_can_port,
        left_can_port=left_can_port,
        scale_factor=scale_factor,
        visualize_placo=visualize_placo,
        control_rate_hz=control_rate_hz,
        enable_log_data=enable_log_data,
        log_dir=log_dir,
    )

    try:
        controller.run()
    except Exception as e:
        print(f"\n错误: {e}")
        raise
    finally:
        print("程序结束")


if __name__ == "__main__":
    tyro.cli(main)
