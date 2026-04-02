"""
睿曼 Gen72 机械臂硬件接口

基于官方 Realman Python SDK（RoboticArm）实现，使用 rm_movej_canfd 进行实时关节流式控制。
"""

import time
from collections import deque
from typing import List, Union

import numpy as np


class WeightedMovingFilter:
    """加权移动平均滤波器，平滑 IK 输出，抑制奇异点附近抖动"""

    def __init__(self, weights: np.ndarray, dim: int):
        self.weights = weights / weights.sum()
        self.buffer = deque(maxlen=len(weights))
        self.dim = dim

    def update(self, new_data: np.ndarray) -> np.ndarray:
        self.buffer.append(new_data.copy())
        data = np.array(self.buffer)
        w = self.weights[-len(data):]
        w = w / w.sum()
        return (data * w[:, None]).sum(axis=0)
from Robotic_Arm.rm_robot_interface import (
    RoboticArm,
    rm_peripheral_read_write_params_t,
    rm_thread_mode_e,
)


class Gen72Interface:
    """
    睿曼 Gen72 机械臂硬件接口类

    使用官方 Python SDK 与 Gen72 通信，rm_movej_canfd 实现实时流式关节控制
    """

    def __init__(
        self,
        ip: str = "192.168.1.19",
        port: int = 8080,
        dt: float = 0.02,
        filter_alpha: float = 0.6,
        has_gripper: bool = True,
        gripper_modbus_port: int = 1,
        gripper_baudrate: int = 115200,
        gripper_address: int = 40000,
        gripper_device: int = 1,
        home_joints: List[float] = None,
        arm: RoboticArm = None,
        skip_sdk_init: bool = False,
    ):
        self.ip = ip
        self.port = port
        self.dt = dt
        self.num_joints = 7
        self.has_gripper = has_gripper
        self.home_joints = home_joints if home_joints is not None else [-88.95, 72.21, -0.86, -7.14, -21.47, 64.5, 0.06]
        self.gripper_modbus_port = gripper_modbus_port
        self.gripper_baudrate = gripper_baudrate
        self.gripper_address = gripper_address
        self.gripper_device = gripper_device
        self._last_gripper_val = None

        # 一阶低通滤波器
        self.filter_alpha = filter_alpha
        self.filtered_positions = None

        # 加权移动平均滤波器（平滑 IK 输出）
        self.wma_filter = WeightedMovingFilter(np.array([0.4, 0.3, 0.2, 0.1]), self.num_joints)
        # 上一帧关节角（用于速度限幅，单位：弧度）
        self._last_positions = None

        # 初始化 SDK
        # skip_sdk_init=True 时跳过 rm_init（全局只需调用一次），每个实例仍有独立 handle
        print(f"Connecting to Gen72 at {ip}:{port}...")
        if arm is not None:
            self.arm = arm
            self._owns_arm = False
        else:
            self.arm = RoboticArm(None if skip_sdk_init else rm_thread_mode_e.RM_TRIPLE_MODE_E)
            self._owns_arm = True
        handle = self.arm.rm_create_robot_arm(ip, port)
        print(f"Gen72 connected, handle id: {handle.id}")

        # 设置末端工具电压 24V
        self.arm.rm_set_tool_voltage(3)

        # 切换到真实模式（mode 1），仿真模式(0)下机械臂不会实际运动
        self.arm.rm_set_arm_run_mode(1)

        # 初始化夹爪 Modbus
        if self.has_gripper:
            self._init_gripper()

    def _init_gripper(self):
        """初始化夹爪 Modbus 模式"""
        print("Initializing gripper Modbus mode...")
        ret = self.arm.rm_set_modbus_mode(self.gripper_modbus_port, self.gripper_baudrate, 2)
        if ret == 0:
            print("Gripper Modbus initialized")
        else:
            print(f"Warning: Gripper Modbus init returned {ret}")

        # 夹爪参数结构体
        self.gripper_params = rm_peripheral_read_write_params_t(
            self.gripper_modbus_port, self.gripper_address, self.gripper_device
        )

        # 初始化夹爪为打开状态
        self.arm.rm_write_single_register(self.gripper_params, 100)

    def go_home(self) -> bool:
        """移动到 Home 位置"""
        print("Moving Gen72 to home position...")
        ret = self.arm.rm_movej(self.home_joints, 20, 0, 0, 1)
        time.sleep(2.0)
        # rm_movej 会切换运动模式，结束后切回真实模式
        self.arm.rm_set_arm_run_mode(1)
        return ret == 0

    def get_joint_positions(self) -> np.ndarray:
        """
        获取当前关节位置（弧度）

        Returns:
            np.ndarray: shape (7,)，单位弧度
        """
        ret, joint_deg = self.arm.rm_get_joint_degree()
        if ret != 0 or joint_deg is None:
            if self._last_positions is not None:
                return self._last_positions.copy()
            return np.zeros(self.num_joints)

        positions = np.deg2rad(np.array(joint_deg[:self.num_joints], dtype=float))
        return positions

    def get_joint_velocities(self) -> np.ndarray:
        """返回零速度（SDK 不直接提供速度）"""
        return np.zeros(self.num_joints)

    def set_joint_positions(
        self,
        positions: Union[List[float], np.ndarray],
        **kwargs,
    ) -> bool:
        """
        实时流式关节位置控制（rm_movej_canfd）

        Args:
            positions: 目标关节位置（弧度），shape: (7,)

        Returns:
            bool: 成功返回 True
        """
        if len(positions) != self.num_joints:
            print(f"Error: Expected {self.num_joints} joints, got {len(positions)}")
            return False

        # 关节限位检查（弧度）
        joint_limits = [
            (-3.0014, 3.0014),   # joint1 ±172°
            (-1.8323, 1.8323),   # joint2 ±105°
            (-2.8448, 2.8448),   # joint3
            (-2.8792, 0.9597),   # joint4 -165°~+55°
            (-2.8448, 2.8448),   # joint5
            (-2.0944, 2.0944),   # joint6 ±120°
            (-3.0014, 3.0014),   # joint7 ±172°
        ]
        clipped = np.array([
            np.clip(pos, lo, hi)
            for pos, (lo, hi) in zip(positions, joint_limits)
        ])

        # 速度限幅：每步最大 2°，防止奇异点附近关节突变
        max_delta = np.deg2rad(2.0)
        if self._last_positions is not None:
            delta = clipped - self._last_positions
            scale = np.max(np.abs(delta)) / max_delta
            if scale > 1.0:
                clipped = self._last_positions + delta / scale
        self._last_positions = clipped.copy()

        # 加权移动平均滤波（替换一阶低通）
        smoothed = self.wma_filter.update(clipped)

        # 转换为角度列表（SDK 单位：度）
        joint_deg = np.rad2deg(smoothed).tolist()

        # rm_movej_canfd: 实时流式控制，follow=True 高跟随模式
        ret = self.arm.rm_movej_canfd(joint_deg, True)
        if ret != 0:
            print(f"[CANFD] ret={ret}  target={[round(j,1) for j in joint_deg]}")
        return ret == 0

    def set_gripper_position(self, position: float) -> bool:
        """
        设置夹爪位置（Modbus RTU，0-100 整数）

        Args:
            position: 夹爪开合度 (0.0=完全闭合, 1.0=完全打开)

        Returns:
            bool: 成功返回 True
        """
        if not self.has_gripper:
            return False

        position = float(np.clip(position, 0.0, 1.0))

        # 只在变化超过 1% 时才发送
        if self._last_gripper_val is not None and abs(position - self._last_gripper_val) < 0.01:
            return True

        self._last_gripper_val = position
        register_value = round(position * 100)
        ret = self.arm.rm_write_single_register(self.gripper_params, register_value)
        return ret == 0

    def get_gripper_position(self) -> float:
        """
        获取夹爪位置（0.0-1.0）

        Returns:
            float: 夹爪开合度，读取失败返回 -1.0
        """
        if not self.has_gripper:
            return 0.0

        read_params = rm_peripheral_read_write_params_t(
            self.gripper_modbus_port, self.gripper_address, self.gripper_device
        )
        ret, value = self.arm.rm_read_holding_registers(read_params)
        if ret != 0:
            return -1.0
        return float(np.clip(value / 100.0, 0.0, 1.0))

    def enable_robot(self) -> bool:
        print("Gen72 ready")
        return True

    def disable_robot(self) -> bool:
        print("Disconnecting Gen72...")
        if self._owns_arm:
            self.arm.rm_close_robot_arm()
        print("Gen72 disconnected")
        return True

    def emergency_stop(self) -> bool:
        print("Gen72 emergency stop!")
        self.arm.rm_set_arm_stop()
        return True

    def __del__(self):
        if hasattr(self, "arm") and self._owns_arm:
            try:
                self.arm.rm_close_robot_arm()
            except Exception:
                pass
