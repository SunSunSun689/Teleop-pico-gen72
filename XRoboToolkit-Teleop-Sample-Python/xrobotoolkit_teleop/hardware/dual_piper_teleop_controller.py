"""
松灵 Piper 双臂遥操作控制器

两个独立的 PiperTeleopController 实例（右臂 can0 + 左臂 can1），
在同一控制循环中驱动双臂。
"""

import time
import threading

from xrobotoolkit_teleop.hardware.piper_teleop_controller import (
    PiperTeleopController,
    DEFAULT_PIPER_MANIPULATOR_CONFIG,
    DEFAULT_PIPER_LEFT_MANIPULATOR_CONFIG,
    DEFAULT_PIPER_URDF_PATH,
    DEFAULT_SCALE_FACTOR,
)
from xrobotoolkit_teleop.utils.geometry import R_HEADSET_TO_WORLD

DEFAULT_RIGHT_CAN_PORT = "can0"
DEFAULT_LEFT_CAN_PORT = "can1"


class DualPiperTeleopController:
    """
    松灵 Piper 双臂遥操作控制器

    持有两个独立的 PiperTeleopController 实例，在同一控制循环中驱动双臂。
    右臂使用 can0，左臂使用 can1。
    """

    def __init__(
        self,
        robot_urdf_path: str = DEFAULT_PIPER_URDF_PATH,
        right_can_port: str = DEFAULT_RIGHT_CAN_PORT,
        left_can_port: str = DEFAULT_LEFT_CAN_PORT,
        scale_factor: float = DEFAULT_SCALE_FACTOR,
        visualize_placo: bool = False,
        control_rate_hz: int = 50,
        enable_log_data: bool = True,
        log_dir: str = "logs/piper_dual",
    ):
        self.control_rate_hz = control_rate_hz
        self._stop_event = threading.Event()

        print(f"初始化右臂 ({right_can_port})...")
        self.right_ctrl = PiperTeleopController(
            robot_urdf_path=robot_urdf_path,
            manipulator_config=DEFAULT_PIPER_MANIPULATOR_CONFIG,
            can_port=right_can_port,
            R_headset_world=R_HEADSET_TO_WORLD,
            scale_factor=scale_factor,
            visualize_placo=visualize_placo,
            control_rate_hz=control_rate_hz,
            enable_log_data=enable_log_data,
            log_dir=f"{log_dir}/right",
            enable_camera=False,
        )

        print(f"初始化左臂 ({left_can_port})...")
        self.left_ctrl = PiperTeleopController(
            robot_urdf_path=robot_urdf_path,
            manipulator_config=DEFAULT_PIPER_LEFT_MANIPULATOR_CONFIG,
            can_port=left_can_port,
            R_headset_world=R_HEADSET_TO_WORLD,
            scale_factor=scale_factor,
            visualize_placo=False,  # 只在右臂开可视化，避免重复窗口
            control_rate_hz=control_rate_hz,
            enable_log_data=enable_log_data,
            log_dir=f"{log_dir}/left",
            enable_camera=False,
        )

    def _setup(self):
        """初始化双臂硬件"""
        print("初始化右臂硬件...")
        self.right_ctrl._robot_setup()
        print("初始化左臂硬件...")
        self.left_ctrl._robot_setup()
        print("双臂初始化完成")

    def _control_loop(self, stop_event: threading.Event):
        """双臂控制主循环"""
        dt = 1.0 / self.control_rate_hz
        while not stop_event.is_set():
            t0 = time.time()

            # 右臂
            try:
                self.right_ctrl._update_robot_state()
                self.right_ctrl._update_gripper_target()
                self.right_ctrl._update_ik()
                self.right_ctrl._send_command()
            except Exception as e:
                print(f"[ERROR] 右臂控制异常: {e}")

            # 左臂
            try:
                self.left_ctrl._update_robot_state()
                self.left_ctrl._update_gripper_target()
                self.left_ctrl._update_ik()
                self.left_ctrl._send_command()
            except Exception as e:
                print(f"[ERROR] 左臂控制异常: {e}")

            elapsed = time.time() - t0
            sleep_time = dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        # 关闭双臂
        self.right_ctrl._shutdown_robot()
        self.left_ctrl._shutdown_robot()
        print("双臂控制循环已停止")

    def run(self):
        """启动双臂遥操作"""
        self._setup()

        thread = threading.Thread(target=self._control_loop, args=(self._stop_event,), daemon=True)
        thread.start()

        print("双臂遥操作运行中，按 Ctrl+C 退出")
        try:
            while thread.is_alive():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n用户中断，正在安全关闭...")
        finally:
            self._stop_event.set()
            thread.join(timeout=5.0)
            self.right_ctrl.xr_client.close()
            print("程序结束")
