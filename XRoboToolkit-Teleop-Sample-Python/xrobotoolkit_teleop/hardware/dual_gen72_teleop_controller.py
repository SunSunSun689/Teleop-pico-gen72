"""
睿曼 Gen72 双臂遥操作控制器

继承自 HardwareTeleopController，同时控制左右两台 Gen72（7自由度）
"""

import os
import time
from typing import Dict

import numpy as np

from xrobotoolkit_teleop.common.base_hardware_teleop_controller import (
    HardwareTeleopController,
)
from xrobotoolkit_teleop.hardware.interface.gen72 import Gen72Interface
from xrobotoolkit_teleop.utils.geometry import R_HEADSET_TO_WORLD
from xrobotoolkit_teleop.utils.path_utils import ASSET_PATH

# 默认路径
DEFAULT_DUAL_GEN72_URDF_PATH = os.path.join(ASSET_PATH, "gen72/dual_gen72.urdf")
DEFAULT_SCALE_FACTOR = 1.0

# 默认 IP 配置：右臂 .19，左臂 .20
DEFAULT_ROBOT_IPS = {
    "right_arm": "192.168.1.19",
    "left_arm": "192.168.1.20",
}

DEFAULT_ROBOT_PORT = 8080

# Home 位置（单位：度）
# 两臂安装方向镜像，joint1 符号相反
DEFAULT_HOME_JOINTS = {
    "right_arm": [-88.95, 72.21, -0.86, -7.14, -21.47, 64.5, 0.06],
    "left_arm":  [  8.21, 78.27, -14.17, -2.45,   0.07, 71.53, 9.54],
}

# 双臂 manipulator 配置
DEFAULT_DUAL_GEN72_MANIPULATOR_CONFIG = {
    "right_arm": {
        "link_name": "right_Link7",       # 双臂 URDF 中右臂末端链接
        "pose_source": "right_controller",
        "control_trigger": "right_grip",
        "gripper_config": {
            "type": "parallel",
            "gripper_trigger": "right_trigger",
            "joint_names": ["right_gripper_joint"],
            "open_pos": [1.0],
            "close_pos": [0.0],
        },
    },
    "left_arm": {
        "link_name": "left_Link7",        # 双臂 URDF 中左臂末端链接
        "pose_source": "left_controller",
        "control_trigger": "left_grip",
        "gripper_config": {
            "type": "parallel",
            "gripper_trigger": "left_trigger",
            "joint_names": ["left_gripper_joint"],
            "open_pos": [1.0],
            "close_pos": [0.0],
        },
    },
}

# arm_name → URDF 关节名前缀
_ARM_PREFIX = {
    "right_arm": "right_",
    "left_arm": "left_",
}


class DualGen72TeleopController(HardwareTeleopController):
    """
    睿曼 Gen72 双臂遥操作控制器

    同时管理左右两台 Gen72，使用一个 Placo IK 求解器（14 DOF）
    """

    def __init__(
        self,
        robot_urdf_path: str = DEFAULT_DUAL_GEN72_URDF_PATH,
        manipulator_config: dict = DEFAULT_DUAL_GEN72_MANIPULATOR_CONFIG,
        robot_ips: Dict[str, str] = DEFAULT_ROBOT_IPS,
        robot_port: int = DEFAULT_ROBOT_PORT,
        R_headset_world: np.ndarray = R_HEADSET_TO_WORLD,
        scale_factor: float = DEFAULT_SCALE_FACTOR,
        visualize_placo: bool = False,
        control_rate_hz: int = 50,
        enable_log_data: bool = True,
        log_dir: str = "logs/gen72_dual",
        log_freq: float = 50,
        enable_camera: bool = False,
        camera_fps: int = 30,
    ):
        """
        初始化双臂 Gen72 遥操作控制器

        Args:
            robot_urdf_path: 双臂 URDF 文件路径
            manipulator_config: 机械臂配置字典（包含 right_arm 和 left_arm）
            robot_ips: 左右臂 IP 地址字典，例如 {"right_arm": "192.168.1.19", "left_arm": "192.168.1.18"}
            robot_port: 机械臂 TCP 端口（默认 8080）
            scale_factor: VR 控制器移动缩放因子
            visualize_placo: 是否可视化 IK 求解
            control_rate_hz: 控制频率
            enable_log_data: 是否记录数据
            log_dir: 日志保存目录
            enable_camera: 是否启用相机
        """
        self.robot_ips = robot_ips
        self.robot_port = robot_port

        super().__init__(
            robot_urdf_path=robot_urdf_path,
            manipulator_config=manipulator_config,
            R_headset_world=R_headset_world,
            floating_base=False,
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
        """设置 Placo IK 求解器，为每条臂建立独立的关节索引切片"""
        super()._placo_setup()

        self.placo_arm_joint_slice: Dict[str, slice] = {}
        for arm_name in self.manipulator_config:
            prefix = _ARM_PREFIX[arm_name]
            joint_names = [f"{prefix}joint{i}" for i in range(1, 8)]
            self.placo_arm_joint_slice[arm_name] = slice(
                self.placo_robot.get_joint_offset(joint_names[0]),
                self.placo_robot.get_joint_offset(joint_names[-1]) + 1,
            )

    def _robot_setup(self):
        """初始化左右两台 Gen72 的硬件接口"""
        self.arm_controllers: Dict[str, Gen72Interface] = {}

        for i, (arm_name, ip) in enumerate(self.robot_ips.items()):
            print(f"Connecting to Gen72 {arm_name} at {ip}:{self.robot_port}")
            self.arm_controllers[arm_name] = Gen72Interface(
                ip=ip,
                port=self.robot_port,
                dt=self.dt,
                home_joints=DEFAULT_HOME_JOINTS[arm_name],
                skip_sdk_init=(i > 0),  # 第一个实例初始化 SDK，后续跳过
            )

        print("Moving both arms to home position...")
        for arm_name, ctrl in self.arm_controllers.items():
            ctrl.go_home()

        time.sleep(2)
        print("Both Gen72 arms are ready for teleoperation.")

    def _initialize_camera(self):
        """初始化相机（双臂 Gen72 默认不使用相机）"""
        pass

    def _update_robot_state(self):
        """从左右两臂读取关节状态并更新 Placo"""
        for arm_name, ctrl in self.arm_controllers.items():
            q = ctrl.get_joint_positions()
            self.placo_robot.state.q[self.placo_arm_joint_slice[arm_name]] = q

    def _send_command(self):
        """将 IK 求解结果发送到左右两臂，并控制夹爪"""
        for arm_name, ctrl in self.arm_controllers.items():
            # 发送关节角度
            if self.active.get(arm_name, False):
                q_des = self.placo_robot.state.q[
                    self.placo_arm_joint_slice[arm_name]
                ].copy()
                ctrl.set_joint_positions(q_des)

            # 控制夹爪
            if "gripper_config" in self.manipulator_config[arm_name]:
                gripper_config = self.manipulator_config[arm_name]["gripper_config"]
                joint_name = gripper_config["joint_names"][0]
                gripper_target = self.gripper_pos_target[arm_name][joint_name]

                open_pos = gripper_config["open_pos"][0]
                close_pos = gripper_config["close_pos"][0]
                normalized_pos = (gripper_target - close_pos) / (open_pos - close_pos)

                ctrl.set_gripper_position(normalized_pos)

    def _get_robot_state_for_logging(self) -> Dict:
        """返回用于日志记录的机器人状态"""
        return {
            "qpos": {
                arm: ctrl.get_joint_positions()
                for arm, ctrl in self.arm_controllers.items()
            },
            "qvel": {
                arm: ctrl.get_joint_velocities()
                for arm, ctrl in self.arm_controllers.items()
            },
            "qpos_des": {
                arm: self.placo_robot.state.q[self.placo_arm_joint_slice[arm]].copy()
                for arm in self.arm_controllers
            },
            "gripper_target": {
                arm: (
                    self.gripper_pos_target[arm].copy()
                    if "gripper_config" in self.manipulator_config[arm]
                    else None
                )
                for arm in self.arm_controllers
            },
        }

    def _get_camera_frame_for_logging(self) -> Dict:
        """返回用于日志记录的相机帧（双臂 Gen72 默认无相机）"""
        return {}

    def _shutdown_robot(self):
        """优雅关闭左右两臂"""
        print("Shutting down both Gen72 arms...")
        for arm_name, ctrl in self.arm_controllers.items():
            print(f"  Homing {arm_name}...")
            ctrl.go_home()
        time.sleep(2)
        for arm_name, ctrl in self.arm_controllers.items():
            ctrl.disable_robot()
        print("Both Gen72 arms shut down.")
