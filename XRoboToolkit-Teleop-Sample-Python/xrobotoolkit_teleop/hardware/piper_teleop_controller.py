"""
松灵 Piper 机械臂遥操作控制器

继承自 HardwareTeleopController，实现 Piper 特定的硬件接口
"""

import os
import time
from typing import Dict

import numpy as np

from xrobotoolkit_teleop.common.base_hardware_teleop_controller import (
    HardwareTeleopController,
)
from xrobotoolkit_teleop.hardware.interface.piper import PiperInterface
from xrobotoolkit_teleop.hardware.interface.realsense import RealSenseCameraInterface
from xrobotoolkit_teleop.utils.geometry import R_HEADSET_TO_WORLD
from xrobotoolkit_teleop.utils.path_utils import ASSET_PATH

# 默认路径和配置
DEFAULT_PIPER_URDF_PATH = os.path.join(ASSET_PATH, "piper/piper.urdf")
DEFAULT_SCALE_FACTOR = 1.0

# 默认相机配置（如果使用 RealSense）
DEFAULT_WRIST_CAM_SERIAL = "123456789"  # 替换为实际序列号

# Piper 单臂配置
DEFAULT_PIPER_MANIPULATOR_CONFIG = {
    "right_arm": {
        "link_name": "link6",  # Piper 末端执行器链接名
        "pose_source": "right_controller",  # 使用右手 VR 控制器
        "control_trigger": "right_grip",  # 右手握持键激活控制
        "gripper_config": {
            "type": "parallel",  # 平行夹爪
            "gripper_trigger": "right_trigger",  # 右手扳机键控制夹爪
            "joint_names": ["gripper_joint"],  # 夹爪关节名
            "open_pos": [0.85],  # 完全打开位置
            "close_pos": [0.0],  # 完全闭合位置
        },
    },
}


class PiperTeleopController(HardwareTeleopController):
    """
    松灵 Piper 机械臂遥操作控制器

    继承自 HardwareTeleopController，实现 Piper 特定的硬件接口
    """

    def __init__(
        self,
        robot_urdf_path: str = DEFAULT_PIPER_URDF_PATH,
        manipulator_config: dict = DEFAULT_PIPER_MANIPULATOR_CONFIG,
        can_port: str = "can0",
        R_headset_world: np.ndarray = R_HEADSET_TO_WORLD,
        scale_factor: float = DEFAULT_SCALE_FACTOR,
        visualize_placo: bool = False,
        control_rate_hz: int = 50,
        enable_log_data: bool = True,
        log_dir: str = "logs/piper",
        log_freq: float = 50,
        enable_camera: bool = False,
        camera_serial: str = DEFAULT_WRIST_CAM_SERIAL,
        camera_width: int = 640,
        camera_height: int = 480,
        camera_fps: int = 30,
    ):
        """
        初始化 Piper 遥操作控制器

        Args:
            robot_urdf_path: Piper URDF 文件路径
            manipulator_config: 机械臂配置字典
            can_port: CAN 端口名称（如 "can0", "can1"）
            scale_factor: VR 控制器移动缩放因子
            visualize_placo: 是否可视化 IK 求解
            control_rate_hz: 控制频率
            enable_log_data: 是否记录数据
            log_dir: 日志保存目录
            enable_camera: 是否启用相机
            camera_serial: 相机序列号
        """
        self.can_port = can_port
        self.camera_serial = camera_serial
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera_fps = camera_fps

        super().__init__(
            robot_urdf_path=robot_urdf_path,
            manipulator_config=manipulator_config,
            R_headset_world=R_headset_world,
            floating_base=False,  # Piper 是固定基座
            scale_factor=scale_factor,
            visualize_placo=visualize_placo,
            control_rate_hz=control_rate_hz,
            enable_log_data=enable_log_data,
            log_dir=log_dir,
            log_freq=log_freq,
            enable_camera=enable_camera,
            camera_fps=camera_fps,
        )

    def _placo_setup(self):
        """设置 Placo IK 求解器"""
        super()._placo_setup()

        # 获取 Piper 关节在 Placo 中的索引范围
        arm_joint_names = [f"joint{i}" for i in range(1, 7)]
        self.placo_arm_joint_slice = slice(
            self.placo_robot.get_joint_offset(arm_joint_names[0]),
            self.placo_robot.get_joint_offset(arm_joint_names[-1]) + 1,
        )

    def _robot_setup(self):
        """初始化 Piper 硬件接口"""
        print(f"Setting up Piper robot on CAN port: {self.can_port}")

        self.piper = PiperInterface(
            can_port=self.can_port,
            dt=self.dt
        )

        # 移动到 Home 位置
        print("Moving Piper to home position...")
        self.piper.go_home()
        time.sleep(2)  # 等待到达 Home 位置

        print("Piper is ready for teleoperation.")

    def _initialize_camera(self):
        """初始化相机（可选）"""
        if self.enable_camera:
            print("Initializing RealSense camera...")
            try:
                self.camera_interface = RealSenseCameraInterface(
                    width=self.camera_width,
                    height=self.camera_height,
                    fps=self.camera_fps,
                    serial_numbers=[self.camera_serial],
                    enable_depth=False,
                )
                self.camera_interface.start()
                print("Camera initialized successfully.")
            except Exception as e:
                print(f"Error initializing camera: {e}")
                self.camera_interface = None

    def _update_robot_state(self):
        """从硬件读取当前关节状态并更新 Placo"""
        current_q = self.piper.get_joint_positions()
        self.placo_robot.state.q[self.placo_arm_joint_slice] = current_q

    def _send_command(self):
        """将 IK 求解的关节目标发送到硬件"""
        # 只有在激活状态下才发送控制命令
        if self.active.get("right_arm", False):
            q_des = self.placo_robot.state.q[self.placo_arm_joint_slice].copy()
            self.piper.set_joint_positions(q_des)

        # 控制夹爪
        if "gripper_config" in self.manipulator_config["right_arm"]:
            gripper_config = self.manipulator_config["right_arm"]["gripper_config"]
            joint_name = gripper_config["joint_names"][0]
            gripper_target = self.gripper_pos_target["right_arm"][joint_name]

            # 将夹爪位置归一化到 0-1
            open_pos = gripper_config["open_pos"][0]
            close_pos = gripper_config["close_pos"][0]
            normalized_pos = (gripper_target - close_pos) / (open_pos - close_pos)

            self.piper.set_gripper_position(normalized_pos)

    def _get_robot_state_for_logging(self) -> Dict:
        """返回用于日志记录的机器人状态"""
        return {
            "qpos": self.piper.get_joint_positions(),
            "qvel": self.piper.get_joint_velocities(),
            "qpos_des": self.placo_robot.state.q[self.placo_arm_joint_slice].copy(),
            "gripper_target": self.gripper_pos_target["right_arm"].copy()
            if "gripper_config" in self.manipulator_config["right_arm"]
            else None,
        }

    def _get_camera_frame_for_logging(self) -> Dict:
        """返回用于日志记录的相机帧"""
        if not self.camera_interface:
            return {}

        frames = self.camera_interface.get_frames()
        return {"wrist_cam": frames.get(self.camera_serial, None)} if frames else {}

    def _shutdown_robot(self):
        """优雅关闭机器人"""
        print("Shutting down Piper...")
        self.piper.go_home()
        time.sleep(1)
        self.piper.disable_robot()
        print("Piper shutdown complete.")
