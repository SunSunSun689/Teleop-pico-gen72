# 睿曼 Gen72 遥操作文档

## 硬件配置

| 项目 | 值 |
|------|-----|
| 右臂 IP | 192.168.1.19 |
| 左臂 IP | 192.168.1.20 |
| 端口 | 8080 |
| 自由度 | 7 DOF |
| 控制频率 | 50 Hz |

### Home 位置（单位：度）

| 关节 | 右臂 | 左臂 |
|------|------|------|
| joint1 | -88.95 | 8.21 |
| joint2 | 72.21 | 78.27 |
| joint3 | -0.86 | -14.17 |
| joint4 | -7.14 | -2.45 |
| joint5 | -21.47 | 0.07 |
| joint6 | 64.5 | 71.53 |
| joint7 | 0.06 | 9.54 |

修改位置：`xrobotoolkit_teleop/hardware/dual_gen72_teleop_controller.py` 顶部 `DEFAULT_HOME_JOINTS`

---

## 运行方式

```bash
#激活虚拟环境
conda activate pico
# 单臂遥操
python scripts/hardware/teleop_gen72_hardware.py

# 双臂遥操
python scripts/hardware/teleop_dual_gen72_hardware.py

# 自定义参数
python scripts/hardware/teleop_dual_gen72_hardware.py \
    --right-arm-ip 192.168.1.19 \
    --left-arm-ip 192.168.1.20 \
    --scale-factor 1.5
```

---

## 关键文件

```
xrobotoolkit_teleop/hardware/interface/gen72.py       # 硬件接口（单臂）
xrobotoolkit_teleop/hardware/gen72_teleop_controller.py       # 单臂控制器
xrobotoolkit_teleop/hardware/dual_gen72_teleop_controller.py  # 双臂控制器
scripts/hardware/teleop_gen72_hardware.py             # 单臂启动脚本
scripts/hardware/teleop_dual_gen72_hardware.py        # 双臂启动脚本
scripts/hardware/test_gen72_canfd.py                  # 通信测试脚本
scripts/hardware/debug_gen72.py                       # VR 输入调试脚本
assets/gen72/gen72.urdf                               # 单臂 URDF
assets/gen72/dual_gen72.urdf                          # 双臂 URDF
```

---

## 进度

- [x] 单臂硬件接口（`Gen72Interface`）
- [x] 单臂遥操验证（IK 正常，机械臂可运动）
- [x] 双臂连接（独立 SDK 实例，`skip_sdk_init` 方案）
- [x] 双臂 home 位置配置
- [ ] 双臂遥操验证
- [ ] IK 运动质量优化（全姿态 vs 纯位置控制）
- [ ] 黄灯保护问题根本解决

---

## 已知问题与解决方案

### 1. 机械臂不动（仿真模式）

**现象**：`rm_movej_canfd` 返回 0，但机械臂没有实际运动。

**原因**：`rm_set_arm_run_mode(0)` 是仿真模式，不会实际运动。

**解决**：连接后立刻调用 `arm.rm_set_arm_run_mode(1)` 切换到真实模式。

---

### 2. 双臂连接后第一台断开

**现象**：连接第二台机械臂后，第一台报 `[rm_movej] The robotic arm has been disconnected`。

**原因**：`RoboticArm` 的 `self.handle` 是单实例变量，每次 `rm_create_robot_arm` 都会覆盖，导致第一个连接丢失。

**解决**：每台机械臂使用独立的 `RoboticArm` 实例。`rm_init` 是全局 C 库初始化只需调用一次，第二个实例用 `RoboticArm(None)` 跳过初始化，再调 `rm_create_robot_arm` 建立独立连接。`Gen72Interface` 通过 `skip_sdk_init=True` 参数实现。

---

### 3. 连接失败（handle id: -1）

**现象**：`socket connect err! handle id: -1`

**原因**：上次脚本未正常断开，控制器端口被占用。

**解决**：等待约 15 秒让控制器超时释放，或重启机械臂控制器。

---

### 4. 运动后黄灯保护

**现象**：机械臂运动后进入保护状态（黄灯）。

**原因**：可能触发奇异点或关节限位。

**临时解决**：调用 `arm.rm_clear_system_err()` 清除错误，将 home 位置设为实际工作位置避免大幅运动。

---

## SDK 关键说明

```python
from Robotic_Arm.rm_robot_interface import RoboticArm, rm_thread_mode_e

# 初始化（全局只需一次）
arm = RoboticArm(rm_thread_mode_e.RM_TRIPLE_MODE_E)
handle = arm.rm_create_robot_arm("192.168.1.19", 8080)

# 必须切换到真实模式
arm.rm_set_arm_run_mode(1)   # 1=真实, 0=仿真

# 实时流式控制（单位：度）
arm.rm_movej_canfd(joint_deg_list, follow=True)   # follow=True 高跟随，要求周期 ≤10ms
arm.rm_movej_canfd(joint_deg_list, follow=False)  # follow=False 低跟随，50Hz 可用

# 规划运动
arm.rm_movej(joint_deg_list, speed=20, 0, 0, 1)
```

---

## 关节限位（弧度）

| 关节 | 最小 | 最大 |
|------|------|------|
| joint1 | -3.0014 (-172°) | 3.0014 (172°) |
| joint2 | -1.8323 (-105°) | 1.8323 (105°) |
| joint3 | -2.8448 | 2.8448 |
| joint4 | -2.8792 (-165°) | 0.9597 (55°) |
| joint5 | -2.8448 | 2.8448 |
| joint6 | -2.0944 (-120°) | 2.0944 (120°) |
| joint7 | -3.0014 (-172°) | 3.0014 (172°) |
