# Gen72 双臂遥操 - 进度记录

---

## 2026-03-31

### 已完成

**Home 位置校正**
- 右臂 home：`[-88.85, 69.10, 0.40, 0.45, -0.68, 73.06, -0.67]`
- 左臂 home：`[87.79, 71.60, -1.73, -0.32, 1.02, 73.07, -0.63]`
- 配置文件：`xrobotoolkit_teleop/hardware/dual_gen72_teleop_controller.py` 顶部 `DEFAULT_HOME_JOINTS`

**左臂 URDF 基座朝向修正**
- 左臂安装方向与右臂镜像，joint1 符号相反
- `assets/gen72/dual_gen72.urdf` 中 `world_to_left_base` 的 `rpy` 改为 `"0 0 3.14159"`

**scale_factor 调整**
- `scripts/hardware/teleop_dual_gen72_hardware.py` 默认值从 1.5 改为 1.0

**奇异点处理增强**（参考 unitreerobotics/xr_teleoperate）
- 执行层速度限幅：每步最大 2°，防止关节突变（`gen72.py`）
- 加权移动平均滤波（WMA）：窗口4帧，权重 `[0.4, 0.3, 0.2, 0.1]`，替换原一阶低通（`gen72.py`）
- manipulability 权重：`1e-2` → `5e-2`（`base_teleop_controller.py`）
- 详细分析见 `docs/singularity_handling.md`

**手柄输入抖动抑制**
- 在 `base_teleop_controller.py` 的 `_process_xr_pose` 中加入一阶低通滤波
- 默认 `alpha=0.2`，可调范围 0.1~0.5

### 进行中

**IPOPT IK 集成**（参考 unitreerobotics/xr_teleoperate）
- 目标：复用 CasADi + IPOPT 方案，保留 Placo 作为备选，支持运行时切换
- 依赖：`casadi`（已安装）、`pinocchio.casadi`（阻塞中）
- 阻塞原因：`pip install pin` 不含 casadi 接口；conda-forge 版 pinocchio 与 placo 依赖的版本冲突
- 当前状态：pinocchio 3.8.0（pip）+ placo 正常运行，但 `pinocchio.casadi` 不可用
- 下一步：评估从源码构建 pinocchio with casadi 支持，或改用子进程方案

### 未解决

**左臂夹爪 Modbus 不通**
- 右臂夹爪正常，左臂所有地址/波特率/端口组合均无响应
- 工具电压、Modbus 初始化均返回成功，但写寄存器失败
- 怀疑左臂末端工具接口硬件问题，建议交叉测试夹爪

**黄灯保护问题**
- 待排查

---
