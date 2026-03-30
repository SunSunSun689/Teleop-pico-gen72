# 松灵 Piper 机械臂集成完成

## 已创建的文件

### 1. 硬件接口
- `xrobotoolkit_teleop/hardware/interface/piper.py`
  - Piper 机械臂底层通信接口
  - 包含关节控制、状态读取、夹爪控制等功能

### 2. 遥操作控制器
- `xrobotoolkit_teleop/hardware/piper_teleop_controller.py`
  - 继承自 HardwareTeleopController
  - 实现 Piper 特定的控制逻辑
  - 集成 Placo IK 求解器

### 3. 启动脚本
- `scripts/hardware/teleop_piper_hardware.py`
  - 主启动脚本
  - 支持命令行参数配置

### 4. 测试脚本
- `scripts/hardware/test_piper_interface.py`
  - 硬件接口测试工具
  - 用于验证 Piper 连接和基本功能

### 5. 资源目录
- `assets/piper/`
  - URDF 文件存放位置
  - 包含 README 说明文档

---

## 下一步操作

### 1. 获取 Piper URDF 文件

**必需**：将 Piper 的 URDF 文件放置到 `assets/piper/piper.urdf`

获取方式：
- 联系松灵机器人技术支持
- 从 ROS 包中提取
- 从其他项目复制

详见：`assets/piper/README.md`

### 2. 安装 Piper SDK

```bash
conda activate pico

# 根据松灵提供的 SDK 安装方式
# 例如：
# pip install piper-sdk
# 或从源码安装
```

### 3. 更新硬件接口代码

在 `xrobotoolkit_teleop/hardware/interface/piper.py` 中：
- 取消注释 SDK 导入语句
- 替换所有 `# TODO` 标记的代码
- 使用实际的 Piper SDK API 调用

### 4. 测试硬件连接

```bash
conda activate pico
cd ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python

# 测试基本连接
python scripts/hardware/test_piper_interface.py --robot-ip 192.168.1.18

# 测试关节限位
python scripts/hardware/test_piper_interface.py --test-limits
```

### 5. 运行遥操作

```bash
# 确保 XRoboToolkit-PC-Service 正在运行
cd /opt/apps/roboticsservice
bash runService.sh

# 在另一个终端运行 Piper 遥操作
conda activate pico
cd ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python

# 基本运行
python scripts/hardware/teleop_piper_hardware.py

# 带可视化
python scripts/hardware/teleop_piper_hardware.py --visualize-placo

# 自定义参数
python scripts/hardware/teleop_piper_hardware.py \
    --robot-ip 192.168.1.100 \
    --scale-factor 1.5 \
    --control-rate-hz 50 \
    --enable-log-data \
    --log-dir logs/piper_demo
```

---

## 配置说明

### 关键参数

1. **robot_ip**: Piper 机械臂 IP 地址（默认：192.168.1.18）
2. **scale_factor**: VR 控制器移动缩放（建议：1.0-2.0）
3. **control_rate_hz**: 控制频率（建议：50Hz）
4. **visualize_placo**: 是否可视化 IK 求解

### 机械臂配置

在 `piper_teleop_controller.py` 中的 `DEFAULT_PIPER_MANIPULATOR_CONFIG`：

```python
{
    "right_arm": {
        "link_name": "link6",              # 末端执行器链接名
        "pose_source": "right_controller",  # VR 控制器映射
        "control_trigger": "right_grip",    # 激活控制的按键
        "gripper_config": {
            "gripper_trigger": "right_trigger",  # 夹爪控制按键
            "joint_names": ["gripper_joint"],
            "open_pos": [0.85],
            "close_pos": [0.0],
        },
    },
}
```

### 关节限位

在 `piper.py` 中的 `set_joint_positions` 方法：

```python
joint_limits = [
    (-3.14, 3.14),   # joint1
    (-2.0, 2.0),     # joint2
    (-2.5, 2.5),     # joint3
    (-3.14, 3.14),   # joint4
    (-2.0, 2.0),     # joint5
    (-3.14, 3.14),   # joint6
]
```

根据 Piper 实际限位调整这些值。

---

## 故障排查

### 1. 连接失败
```bash
# 检查网络连接
ping 192.168.1.18

# 检查防火墙
sudo ufw status

# 测试端口
telnet 192.168.1.18 8080
```

### 2. URDF 文件缺失
```
错误: FileNotFoundError: assets/piper/piper.urdf

解决: 按照 assets/piper/README.md 获取 URDF 文件
```

### 3. SDK 未安装
```
错误: ModuleNotFoundError: No module named 'piper_sdk'

解决: 安装松灵 Piper SDK
```

### 4. 控制不流畅
- 降低 control_rate_hz
- 检查网络延迟
- 调整 scale_factor

---

## 集成架构

```
XRoboToolkit-PC-Service (接收 Pico 数据)
         ↓
PiperTeleopController (遥操作控制器)
         ↓
    Placo IK Solver (逆运动学求解)
         ↓
PiperInterface (硬件接口)
         ↓
    Piper SDK (松灵 SDK)
         ↓
Piper Robot (实体机械臂)
```

---

## 参考文档

- XRoboToolkit 官方文档：https://xr-robotics.github.io/
- 松灵机器人官网：https://www.agilex.ai/
- Placo IK 求解器：https://github.com/Rhoban/placo
- 项目集成指南：`/home/dora/teleop_pico/piper_integration_guide.md`

---

## 状态

- ✅ 硬件接口类已创建
- ✅ 遥操作控制器已创建
- ✅ 启动脚本已创建
- ✅ 测试脚本已创建
- ⏳ 等待 URDF 文件
- ⏳ 等待 Piper SDK 安装
- ⏳ 等待实际硬件测试

---

创建时间：2026-03-11
