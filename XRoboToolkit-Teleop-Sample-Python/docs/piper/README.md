# XRoboToolkit Pico 遥操 piper - 手动启动指令

## 系统要求

- PICO 4 Ultra 头显（已安装 XRoboToolkit 应用）
- 控制电脑：Ubuntu 22.04 x86_64
- 头显和电脑在同一网络环境

---

## 启动步骤

### 1. 启动 XRoboToolkit-PC-Service（终端1）

```bash
cd /opt/apps/roboticsservice
bash runService.sh
```

**说明：** 这个服务会持续运行，负责接收 Pico 头显的数据。保持此终端运行。

---
### 2.激活can0
```bash
cd SDK/piper_sdk/piper_sdk
bash can_config.sh
```
### 3. 启动仿真程序（终端3）

#### 激活 conda 环境并运行仿真

```bash
# 激活 pico 环境
conda activate pico

# 进入项目目录
cd ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python

# 运行vr遥操
python scripts/hardware/teleop_piper_hardware.py --can-port can0

```
#### pico打开toolkit，连接上IP，然后选择head,controller,hand,send,tracking,vision,

#### 其他可用的仿真示例

```bash
# 双臂 ARX A1X
python scripts/simulation/teleop_dual_a1x_mujoco.py

# Flexiv Rizon 4s
python scripts/simulation/teleop_flexiv_rizon4s_mujoco.py

# Flexiv Rizon 4s (Placo 可视化)
python scripts/simulation/teleop_flexiv_rizon4s_placo.py

# Shadow 灵巧手
python scripts/simulation/teleop_shadow_hand_mujoco.py

# Inspire 灵巧手
python scripts/simulation/teleop_inspire_hand_placo.py

# Unitree G1 人形机器人
python scripts/simulation/teleop_unitree_g1_placo.py

# X7s 单臂机械臂
python scripts/simulation/teleop_x7s_placo.py
```

---

### 3. 在 Pico 4 Ultra 头显上操作

1. 打开 **XRoboToolkit** 应用
2. 输入控制电脑的 IP 地址
3. 勾选：**head**, **hand**, **controller**
4. 点击连接
5. 开始遥操作

---

## 硬件机器人控制（需要实体机器人）

### 双臂 UR5e 硬件

```bash
conda activate pico
cd ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python

# 正常运行
python scripts/hardware/teleop_dual_ur5e_hardware.py

# 重置机械臂位置
python scripts/hardware/teleop_dual_ur5e_hardware.py --reset

# 可视化 IK 结果
python scripts/hardware/teleop_dual_ur5e_hardware.py --visualize_placo
```

### ARX R5 双臂硬件

```bash
python scripts/hardware/teleop_dual_arx_r5_hardware.py
```

### ARX 单臂硬件

```bash
python scripts/hardware/teleop_arx_hardware.py
```

### Galaxea R1 Lite 人形机器人

```bash
python scripts/hardware/teleop_r1lite_hardware.py
```

---

## 停止程序

### 方法1：在终端中停止
- 在各个终端按 `Ctrl+C` 停止对应的程序

### 方法2：使用命令停止

```bash
# 停止 PC Service
pkill -f RoboticsServiceProcess

# 停止仿真程序
pkill -f teleop_dual_ur5e_mujoco
# 或停止其他仿真
pkill -f python.*teleop
```

---

## 常见问题

### 1. 头显连接不上？
- 确认头显和电脑在同一网络
- 检查电脑 IP 地址：`ip addr show`
- 确认 PC Service 正在运行：`ps aux | grep RoboticsService`

### 2. 仿真窗口无法打开？
- 确认已激活 conda 环境：`conda activate pico`
- 检查 MuJoCo 是否安装：`python -c "import mujoco; print(mujoco.__version__)"`

### 3. 数据全是 0？
- 检查网络防火墙设置
- 重启 PC Service 和头显应用
- 确认头显应用中已勾选 head、hand、controller

### 4. 全身追踪不工作？
- 在头显中校准 Motion Tracker
- 在应用中选择 "Full Body Tracking"
- 确保至少连接两个 Pico Swift 设备

---

## 项目路径

- **PC Service**: `/opt/apps/roboticsservice/`
- **Python 示例**: `~/teleop_pico/XRoboToolkit-Teleop-Sample-Python/`
- **Conda 环境**: `pico`

---

## 相关文档

- 官网：https://xr-robotics.github.io/
- GitHub：https://github.com/XR-Robotics
- 详细教程：`~/teleop_pico/XRoboToolkit-Teleop-Sample-Python/README.md`

XRoboToolkit 支持以下硬件机械臂：

  支持的硬件机器人：

  1. 双臂 UR5e（Universal Robots）

  - 脚本：teleop_dual_ur5e_hardware.py
  - 配置：双臂 UR 机械臂 + Robotiq 夹爪 + Dynamixel 头部
  - 特点：工业级协作机器人，适合抓取和操作任务

  2. ARX R5 双臂机械臂

  - 脚本：teleop_dual_arx_r5_hardware.py
  - 配置：双臂 ARX R5 + 内置夹爪
  - 特点：国产机械臂，集成夹爪控制

  3. ARX 单臂机械臂

  - 脚本：teleop_arx_hardware.py
  - 配置：单臂 ARX 机械臂
  - 特点：灵活的单臂控制

  4. Galaxea R1 Lite 人形机器人

  - 脚本：teleop_r1lite_hardware.py
  - 配置：人形机器人全身控制
  - 特点：人形机器人，支持全身遥操作

  硬件要求：

  根据文档，硬件机器人需要：
  - 机器人本体及其控制接口（如 UR 的 RTDE 接口）
  - 夹爪（如 Robotiq 夹爪）
  - 可选：Dynamixel 舵机（用于头部跟踪）
  - 可选：RealSense 相机（用于视觉反馈）

  运行硬件示例：

  例如运行双臂 UR5e：
  conda activate pico

