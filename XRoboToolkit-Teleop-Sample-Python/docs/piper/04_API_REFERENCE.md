# Piper API 参考文档

本文档提供 Piper 硬件接口和控制器的 API 参考。

---

## PiperInterface

**位置**: `xrobotoolkit_teleop/hardware/interface/piper.py`

### 初始化

```python
from xrobotoolkit_teleop.hardware.interface.piper import PiperInterface

piper = PiperInterface(
    can_port="can0",  # CAN 端口名称
    dt=0.02,          # 控制周期（秒），默认 50Hz
)
```

### 方法

#### `go_home() -> bool`
移动到预定义的 Home 位置（零位）

**返回**: 成功返回 True

**示例**:
```python
piper.go_home()
```

#### `get_joint_positions() -> np.ndarray`
获取当前关节位置

**返回**: 关节位置数组（弧度），shape: (6,)

**示例**:
```python
positions = piper.get_joint_positions()
# array([0.059, -0.048, 0.065, 0.113, 0.310, 0.128])
```

#### `get_joint_velocities() -> np.ndarray`
获取当前关节速度

**返回**: 关节速度数组（弧度/秒），shape: (6,)

**注意**: Piper SDK 不提供速度数据，返回零数组

**示例**:
```python
velocities = piper.get_joint_velocities()
# array([0., 0., 0., 0., 0., 0.])
```

#### `set_joint_positions(positions, speed_factor=100) -> bool`
设置目标关节位置

**参数**:
- `positions`: 目标关节位置（弧度），shape: (6,)
- `speed_factor`: 速度因子 (0-100)，默认 100

**返回**: 成功返回 True

**示例**:
```python
target = [0.0, -0.3, 0.8, 0.0, 1.2, 0.0]
piper.set_joint_positions(target, speed_factor=80)
```

#### `set_gripper_position(position, speed=1000) -> bool`
设置夹爪位置

**参数**:
- `position`: 夹爪开合度 (0.0=完全闭合, 1.0=完全打开)
- `speed`: 夹爪速度，默认 1000

**返回**: 成功返回 True

**示例**:
```python
piper.set_gripper_position(0.5)  # 半开
piper.set_gripper_position(1.0)  # 完全打开
piper.set_gripper_position(0.0)  # 完全闭合
```

#### `get_gripper_position() -> float`
获取当前夹爪位置

**返回**: 夹爪开合度 (0.0-1.0)

**示例**:
```python
gripper_pos = piper.get_gripper_position()
```

#### `enable_robot() -> bool`
使能机械臂

**返回**: 成功返回 True

#### `disable_robot() -> bool`
失能机械臂

**返回**: 成功返回 True

#### `emergency_stop() -> bool`
紧急停止

**返回**: 成功返回 True

#### `get_arm_status()`
获取机械臂状态信息

**返回**: 机械臂状态对象

---

## PiperTeleopController

**位置**: `xrobotoolkit_teleop/hardware/piper_teleop_controller.py`

### 初始化

```python
from xrobotoolkit_teleop.hardware.piper_teleop_controller import (
    PiperTeleopController,
    DEFAULT_PIPER_MANIPULATOR_CONFIG,
    DEFAULT_PIPER_URDF_PATH,
)

controller = PiperTeleopController(
    robot_urdf_path=DEFAULT_PIPER_URDF_PATH,
    manipulator_config=DEFAULT_PIPER_MANIPULATOR_CONFIG,
    can_port="can0",
    scale_factor=1.5,
    visualize_placo=False,
    control_rate_hz=50,
    enable_log_data=True,
    log_dir="logs/piper",
)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `robot_urdf_path` | str | `DEFAULT_PIPER_URDF_PATH` | URDF 文件路径 |
| `manipulator_config` | dict | `DEFAULT_PIPER_MANIPULATOR_CONFIG` | 机械臂配置 |
| `can_port` | str | `"can0"` | CAN 端口名称 |
| `scale_factor` | float | `1.0` | VR 移动缩放因子 |
| `visualize_placo` | bool | `False` | 是否可视化 IK 求解 |
| `control_rate_hz` | int | `50` | 控制频率 (Hz) |
| `enable_log_data` | bool | `True` | 是否记录数据 |
| `log_dir` | str | `"logs/piper"` | 日志保存目录 |

### 方法

#### `run()`
运行遥操作控制循环

**示例**:
```python
controller.run()
```

---

## 配置字典

### DEFAULT_PIPER_MANIPULATOR_CONFIG

```python
DEFAULT_PIPER_MANIPULATOR_CONFIG = {
    "right_arm": {
        "link_name": "link6",              # 末端执行器链接名
        "pose_source": "right_controller",  # VR 控制器映射
        "control_trigger": "right_grip",    # 激活控制的按键
        "gripper_config": {
            "type": "parallel",                    # 夹爪类型
            "gripper_trigger": "right_trigger",    # 夹爪控制按键
            "joint_names": ["gripper_joint"],      # 夹爪关节名
            "open_pos": [0.85],                    # 完全打开位置
            "close_pos": [0.0],                    # 完全闭合位置
        },
    },
}
```

---

## 数据结构

### 关节位置数组
```python
# shape: (6,)
# 单位: 弧度
positions = np.array([
    joint1,  # 关节 1 位置
    joint2,  # 关节 2 位置
    joint3,  # 关节 3 位置
    joint4,  # 关节 4 位置
    joint5,  # 关节 5 位置
    joint6,  # 关节 6 位置
])
```

### 关节限位
```python
joint_limits = [
    (-3.14, 3.14),   # joint1: ±180°
    (-2.0, 2.0),     # joint2: ±114.6°
    (-2.5, 2.5),     # joint3: ±143.2°
    (-3.14, 3.14),   # joint4: ±180°
    (-2.0, 2.0),     # joint5: ±114.6°
    (-3.14, 3.14),   # joint6: ±180°
]
```

---

## SDK 底层 API

### Piper SDK (C_PiperInterface_V2)

```python
from piper_sdk import C_PiperInterface_V2

# 初始化
piper = C_PiperInterface_V2("can0")
piper.ConnectPort()

# 使能
piper.EnablePiper()

# 关节控制
piper.JointCtrl(j0, j1, j2, j3, j4, j5)

# 夹爪控制
piper.GripperCtrl(position_um, speed, enable, force)

# 读取状态
joint_msgs = piper.GetArmJointMsgs()
gripper_msgs = piper.GetArmGripperMsgs()
```

### 单位转换

| 数据 | SDK 单位 | 转换因子 | 目标单位 |
|------|----------|----------|----------|
| 关节位置 | SDK 内部 | 57295.7795 | 弧度 |
| 夹爪角度 | 0.001 度 | 1000 | 度 |
| 夹爪位置 | μm | 1000000 | 米 |

**转换公式**:
```python
# 关节位置：SDK → 弧度
angle_rad = sdk_value / 57295.7795

# 关节位置：弧度 → SDK
sdk_value = round(angle_rad * 57295.7795)

# 夹爪：归一化 → μm
gripper_um = normalized_pos * 80000
```

---

## 使用示例

### 基本控制

```python
from xrobotoolkit_teleop.hardware.interface.piper import PiperInterface
import time

# 初始化
piper = PiperInterface(can_port="can0")

# 移动到 Home
piper.go_home()
time.sleep(2)

# 读取当前位置
positions = piper.get_joint_positions()
print(f"Current positions: {positions}")

# 设置新位置
target = [0.0, -0.3, 0.8, 0.0, 1.2, 0.0]
piper.set_joint_positions(target)
time.sleep(2)

# 控制夹爪
piper.set_gripper_position(1.0)  # 打开
time.sleep(1)
piper.set_gripper_position(0.0)  # 关闭

# 失能
piper.disable_robot()
```

### 遥操作控制

```python
from xrobotoolkit_teleop.hardware.piper_teleop_controller import (
    PiperTeleopController,
    DEFAULT_PIPER_MANIPULATOR_CONFIG,
    DEFAULT_PIPER_URDF_PATH,
)

# 创建控制器
controller = PiperTeleopController(
    robot_urdf_path=DEFAULT_PIPER_URDF_PATH,
    manipulator_config=DEFAULT_PIPER_MANIPULATOR_CONFIG,
    can_port="can0",
    scale_factor=1.5,
    control_rate_hz=50,
)

# 运行遥操作
try:
    controller.run()
except KeyboardInterrupt:
    print("Stopped by user")
```

---

## 错误处理

### 常见异常

```python
try:
    piper = PiperInterface(can_port="can0")
except TimeoutError:
    print("Failed to enable Piper robot")
except Exception as e:
    print(f"Error: {e}")
```

### 安全检查

```python
# 检查关节限位
def check_joint_limits(positions):
    limits = [(-3.14, 3.14), (-2.0, 2.0), (-2.5, 2.5),
              (-3.14, 3.14), (-2.0, 2.0), (-3.14, 3.14)]

    for i, (pos, (min_val, max_val)) in enumerate(zip(positions, limits)):
        if pos < min_val or pos > max_val:
            print(f"Warning: Joint {i+1} out of range")
            return False
    return True
```

---

## 参考资料

- **Piper SDK 文档**: `/home/dora/SDK/piper_sdk/README(ZH).MD`
- **XRoboToolkit 文档**: https://xr-robotics.github.io/
- **项目源码**: `xrobotoolkit_teleop/hardware/`

---

**最后更新**: 2026-03-11
