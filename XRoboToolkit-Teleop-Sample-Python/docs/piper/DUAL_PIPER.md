# Piper 双臂遥操作

## 改动说明

新增两个文件，未修改任何现有代码：

- `xrobotoolkit_teleop/hardware/dual_piper_teleop_controller.py`
- `scripts/hardware/teleop_dual_piper_hardware.py`

---

## 使用说明

```bash
conda activate pico
cd /home/dora/teleop_pico/XRoboToolkit-Teleop-Sample-Python

# 默认运行（右臂 can0，左臂 can1）
python scripts/hardware/teleop_dual_piper_hardware.py

# 自定义 CAN 端口
python scripts/hardware/teleop_dual_piper_hardware.py --right-can-port can0 --left-can-port can1

# 开启 IK 可视化
python scripts/hardware/teleop_dual_piper_hardware.py --visualize-placo

# 关闭数据记录
python scripts/hardware/teleop_dual_piper_hardware.py --no-enable-log-data
```

控制方式与单臂一致：右手 grip 键激活右臂，左手 grip 键激活左臂，扳机键控制夹爪。

---

## 架构选型说明

### 为什么不用 Gen72 双臂方案（合并 IK）

Gen72 双臂把两臂合并成一个 14-DOF URDF，用单个 Placo 实例统一求解 IK，再把结果拆分发给两臂。这个设计的出发点是两臂共享一个基座，IK 可以感知双臂之间的约束关系。

Piper 不需要这样做，原因有三：

1. **URDF 不完整**：`assets/piper/dual_piper.urdf` 目前只有右臂，是残缺的，强行用它会引入额外工作量
2. **控制协议不同**：Gen72 用 CAN-FD 流式控制，两臂共享 SDK 初始化（需要 `skip_sdk_init` 绕过），Piper 每个实例绑定独立 CAN 端口，天然隔离，不存在这个问题
3. **没有必要**：双臂 Piper 在实际使用中两臂独立运动，不需要联合约束求解

### 为什么不用 UR5e 双臂方案（多线程 servo）

UR5e 需要独立的 servo 线程持续发送心跳维持 RTDE 连接，否则机械臂会断开。Piper 用 CAN 总线，发完命令就完事，不需要心跳线程，UR5e 的线程模型对 Piper 是过度设计。

### 为什么采用当前方案（两个独立控制器实例）

直接参考 dora 版 `dora_node_piper.py` 已验证的做法：两个 `PiperTeleopController` 实例，各自持有独立的 `PiperInterface`（绑定不同 CAN 端口）和独立的 Placo IK 求解器，在同一个控制循环里顺序执行。

优点：

- **复用现有代码**：`PiperTeleopController` 完全不用改，双臂逻辑只是"跑两次单臂"
- **故障隔离**：一臂异常不影响另一臂，控制循环里各自 try/except
- **调试简单**：两臂完全解耦，可以单独注释掉一臂测试
