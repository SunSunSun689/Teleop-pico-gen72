# 松灵 Piper 机械臂集成指南

## 集成架构概述

基于 XRoboToolkit 的单臂控制集成模式，Piper 机械臂的集成需要以下组件：

```
xrobotoolkit_teleop/
├── hardware/
│   ├── interface/
│   │   └── piper.py              # Piper 硬件接口类
│   └── piper_teleop_controller.py # Piper 遥操作控制器
├── assets/
│   └── piper/
│       └── piper.urdf             # Piper URDF 模型
└── scripts/
    └── hardware/
        └── teleop_piper_hardware.py # Piper 启动脚本
```

---

## 第一步：创建 Piper 硬件接口

### 文件：`xrobotoolkit_teleop/hardware/interface/piper.py`

```python
import numpy as np
from typing import List, Optional, Union

# 导入松灵 Piper SDK
# import piper_sdk  # 根据实际 SDK 调整


class PiperInterface:
    """
    松灵 Piper 机械臂硬件接口类

    负责与 Piper 机械臂的底层通信，包括：
    - 关节位置控制
    - 关节状态读取
    - 夹爪控制
    - 安全保护
    """

    def __init__(
        self,
        robot_ip: str = "192.168.1.18",  # Piper 默认 IP
        port: int = 8080,
        dt: float = 0.02,  # 控制周期 50Hz
    ):
        """
        初始化 Piper 接口

        Args:
            robot_ip: Piper 机械臂的 IP 地址
            port: 通信端口
            dt: 控制周期（秒）
        """
        self.robot_ip = robot_ip
        self.port = port
        self.dt = dt
        self.num_joints = 6  # Piper 有 6 个关节

        # 初始化 Piper SDK 连接
        # self.robot = piper_sdk.PiperRobot(robot_ip, port)
        # self.robot.connect()

        print(f"Piper Interface initialized: {robot_ip}:{port}")

    def go_home(self) -> bool:
        """
        移动到预定义的 Home 位置

        Returns:
            bool: 成功返回 True
        """
        # Piper Home 位置（单位：弧度）
        home_position = [0.0, -0.5, 1.0, 0.0, 1.5, 0.0]

        # self.robot.move_to_joint_positions(home_position, speed=0.5)
        print("Moving Piper to home position...")
        return True

    def get_joint_positions(self) -> np.ndarray:
        """
        获取当前关节位置

        Returns:
            np.ndarray: 关节位置数组，shape: (6,)
        """
        # joint_positions = self.robot.get_joint_positions()
        # return np.array(joint_positions)

        # 临时返回零位置（实际使用时替换为真实读取）
        return np.zeros(self.num_joints)

    def get_joint_velocities(self) -> np.ndarray:
        """
        获取当前关节速度

        Returns:
            np.ndarray: 关节速度数组，shape: (6,)
        """
        # joint_velocities = self.robot.get_joint_velocities()
        # return np.array(joint_velocities)

        return np.zeros(self.num_joints)

    def set_joint_positions(
        self,
        positions: Union[List[float], np.ndarray],
        **kwargs
    ) -> bool:
        """
        设置目标关节位置

        Args:
            positions: 目标关节位置，shape: (6,)
            **kwargs: 额外参数（如速度、加速度限制）

        Returns:
            bool: 成功返回 True
        """
        if len(positions) != self.num_joints:
            print(f"Error: Expected {self.num_joints} joints, got {len(positions)}")
            return False

        # self.robot.set_joint_positions(positions)
        return True

    def set_gripper_position(self, position: float) -> bool:
        """
        设置夹爪位置

        Args:
            position: 夹爪开合度 (0.0=完全闭合, 1.0=完全打开)

        Returns:
            bool: 成功返回 True
        """
        # 将 0-1 映射到 Piper 夹爪的实际范围
        # gripper_pos = position * 0.85  # Piper 夹爪最大开合 0.85m
        # self.robot.set_gripper(gripper_pos)
        return True

    def enable_robot(self) -> bool:
        """使能机械臂"""
        # self.robot.enable()
        print("Piper robot enabled")
        return True

    def disable_robot(self) -> bool:
        """失能机械臂"""
        # self.robot.disable()
        print("Piper robot disabled")
        return True

    def emergency_stop(self) -> bool:
        """紧急停止"""
        # self.robot.emergency_stop()
        print("Piper emergency stop triggered!")
        return True

    def __del__(self):
        """析构函数，断开连接"""
        # if hasattr(self, 'robot'):
        #     self.robot.disconnect()
        pass
```

---

## 第二步：创建 Piper 遥操作控制器

### 文件：`xrobotoolkit_teleop/hardware/piper_teleop_controller.py`

```python
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
        robot_ip: str = "192.168.1.18",
        robot_port: int = 8080,
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
            robot_ip: Piper 机械臂 IP 地址
            robot_port: 通信端口
            scale_factor: VR 控制器移动缩放因子
            visualize_placo: 是否可视化 IK 求解
            control_rate_hz: 控制频率
            enable_log_data: 是否记录数据
            log_dir: 日志保存目录
            enable_camera: 是否启用相机
            camera_serial: 相机序列号
        """
        self.robot_ip = robot_ip
        self.robot_port = robot_port
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
        print(f"Setting up Piper robot at {self.robot_ip}:{self.robot_port}")

        self.piper = PiperInterface(
            robot_ip=self.robot_ip,
            port=self.robot_port,
            dt=self.dt
        )

        # 使能机械臂
        self.piper.enable_robot()

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
```

---

## 第三步：创建启动脚本

### 文件：`scripts/hardware/teleop_piper_hardware.py`

```python
import tyro
from xrobotoolkit_teleop.hardware.piper_teleop_controller import (
    DEFAULT_PIPER_MANIPULATOR_CONFIG,
    DEFAULT_PIPER_URDF_PATH,
    PiperTeleopController,
)


def main(
    robot_urdf_path: str = DEFAULT_PIPER_URDF_PATH,
    robot_ip: str = "192.168.1.18",
    robot_port: int = 8080,
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
        robot_ip: Piper 机械臂 IP 地址
        robot_port: 通信端口
        scale_factor: VR 控制器移动缩放因子
        enable_camera: 是否启用相机
        enable_log_data: 是否记录数据
        visualize_placo: 是否可视化 IK 求解
        control_rate_hz: 控制频率（Hz）
        log_dir: 日志保存目录
    """
    controller = PiperTeleopController(
        robot_urdf_path=robot_urdf_path,
        manipulator_config=DEFAULT_PIPER_MANIPULATOR_CONFIG,
        robot_ip=robot_ip,
        robot_port=robot_port,
        scale_factor=scale_factor,
        enable_camera=enable_camera,
        enable_log_data=enable_log_data,
        visualize_placo=visualize_placo,
        control_rate_hz=control_rate_hz,
        log_dir=log_dir,
    )
    controller.run()


if __name__ == "__main__":
    tyro.cli(main)
```

---

## 第四步：准备 URDF 文件

### 获取 Piper URDF

1. **从松灵官方获取**：
   - 联系松灵技术支持获取 Piper 的 URDF 文件
   - 或从 ROS 包中提取：`piper_description` 包

2. **放置位置**：
   ```bash
   mkdir -p ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python/assets/piper
   cp /path/to/piper.urdf ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python/assets/piper/
   ```

3. **URDF 要求**：
   - 包含 6 个关节：`joint1` 到 `joint6`
   - 末端执行器链接名：`link6`
   - 夹爪关节：`gripper_joint`（如果有）
   - 包含所有必要的 mesh 文件

---

## 第五步：安装 Piper SDK

```bash
# 激活环境
conda activate pico

# 安装松灵 Piper SDK（根据实际情况调整）
# pip install piper-sdk
# 或从源码安装
# cd /path/to/piper-sdk
# pip install -e .
```

---

## 第六步：测试集成

### 1. 测试硬件连接

```python
# test_piper_connection.py
from xrobotoolkit_teleop.hardware.interface.piper import PiperInterface

piper = PiperInterface(robot_ip="192.168.1.18")
piper.enable_robot()
piper.go_home()

# 测试关节读取
positions = piper.get_joint_positions()
print(f"Current joint positions: {positions}")

piper.disable_robot()
```

### 2. 运行遥操作

```bash
conda activate pico
cd ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python

# 基本运行
python scripts/hardware/teleop_piper_hardware.py

# 带可视化
python scripts/hardware/teleop_piper_hardware.py --visualize_placo

# 自定义 IP
python scripts/hardware/teleop_piper_hardware.py --robot_ip 192.168.1.100

# 启用数据记录
python scripts/hardware/teleop_piper_hardware.py --enable_log_data --log_dir logs/piper_demo
```

---

## 关键配置参数

### 1. 网络配置
- **Piper IP**: 确保 Piper 和控制电脑在同一网络
- **测试连接**: `ping 192.168.1.18`

### 2. 控制参数调优
- **scale_factor**: 控制 VR 移动到机械臂移动的比例
  - 默认 1.5，可根据工作空间调整
  - 值越大，VR 移动相同距离，机械臂移动越远

- **control_rate_hz**: 控制频率
  - 推荐 50Hz（与 Piper 通信频率匹配）
  - 过高可能导致通信延迟

### 3. 安全限制
在 `PiperInterface` 中添加关节限位检查：

```python
def set_joint_positions(self, positions):
    # Piper 关节限位（弧度）
    joint_limits = [
        (-3.14, 3.14),   # joint1
        (-2.0, 2.0),     # joint2
        (-2.5, 2.5),     # joint3
        (-3.14, 3.14),   # joint4
        (-2.0, 2.0),     # joint5
        (-3.14, 3.14),   # joint6
    ]

    # 检查并限制关节位置
    for i, (pos, (min_val, max_val)) in enumerate(zip(positions, joint_limits)):
        if pos < min_val or pos > max_val:
            print(f"Warning: Joint {i+1} position {pos} out of range [{min_val}, {max_val}]")
            positions[i] = np.clip(pos, min_val, max_val)

    self.robot.set_joint_positions(positions)
```

---

## 常见问题

### 1. 连接失败
- 检查网络连接：`ping <piper_ip>`
- 确认 Piper SDK 正确安装
- 检查防火墙设置

### 2. 控制不流畅
- 降低 `control_rate_hz`
- 检查网络延迟
- 确认 Piper 固件版本

### 3. IK 求解失败
- 调整 `scale_factor`，避免超出工作空间
- 检查 URDF 文件的关节限位设置
- 启用 `visualize_placo` 查看 IK 求解过程

### 4. 夹爪控制异常
- 确认夹爪关节名称与 URDF 一致
- 检查 `open_pos` 和 `close_pos` 值
- 测试夹爪单独控制

---

## 下一步优化

1. **添加力控制**：
   - 在 `PiperInterface` 中实现力矩控制接口
   - 支持阻抗控制模式

2. **多相机支持**：
   - 添加多个 RealSense 相机
   - 实现立体视觉反馈

3. **双臂 Piper**：
   - 参考 `DEFAULT_DUAL_ARX_R5_MANIPULATOR_CONFIG`
   - 创建双臂 URDF 和配置

4. **数据采集优化**：
   - 添加更多传感器数据记录
   - 实现实时数据可视化

---

## 参考资料

- XRoboToolkit 官方文档：https://xr-robotics.github.io/
- ARX R5 集成示例：`xrobotoolkit_teleop/hardware/arx_r5_teleop_controller.py`
- 松灵 Piper 官方文档：[待补充]
- Placo IK 求解器：https://github.com/Rhoban/placo

---

## 总结

Piper 单臂集成的核心步骤：
1. ✅ 创建硬件接口类（`PiperInterface`）
2. ✅ 创建遥操作控制器（`PiperTeleopController`）
3. ✅ 创建启动脚本（`teleop_piper_hardware.py`）
4. ⏳ 准备 URDF 文件
5. ⏳ 安装 Piper SDK
6. ⏳ 测试和调优

按照这个指南，你可以将松灵 Piper 机械臂完整集成到 XRoboToolkit 系统中。
