# Piper 快速启动指南

⏱️ **预计时间**: 5 分钟

---

## ✅ 前提条件

- [x] Piper 机械臂已连接到 CAN 端口
- [x] CAN 总线已配置（can0 @ 1Mbps）
- [x] Pico 4 Ultra 头显已安装 XRoboToolkit 应用
- [x] 头显和控制电脑在同一网络

---

## 🚀 三步启动

### 步骤 1: 启动 PC Service（终端 1）

```bash
cd /opt/apps/roboticsservice
bash runService.sh
```

### 步骤 2: 启动 Piper 遥操作（终端 2）

```bash
conda activate pico
cd ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python
python scripts/hardware/teleop_piper_hardware.py --can-port can0
```

### 步骤 3: 连接 Pico 头显

1. 戴上 Pico 4 Ultra 头显
2. 打开 **XRoboToolkit** 应用
3. 输入控制电脑的 IP 地址
4. 勾选：**head**, **hand**, **controller**
5. 点击连接

---

## 🎮 开始控制

- **按住右手握持键 (Grip)** → 激活机械臂控制
- **移动右手控制器** → 控制机械臂位置和姿态
- **按右手扳机键 (Trigger)** → 控制夹爪开合

---

## 🔧 常用命令

### 基本运行
```bash
python scripts/hardware/teleop_piper_hardware.py --can-port can0
```

### 带可视化
```bash
python scripts/hardware/teleop_piper_hardware.py \
    --can-port can0 \
    --visualize-placo
```

### 测试硬件连接
```bash
python scripts/hardware/test_piper_interface.py --can-port can0
```

---

## ❓ 遇到问题？

### CAN 连接失败
```bash
# 检查 CAN 状态
ip link show can0

# 重启 CAN
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up
```

### 控制不响应
- 确认 PC Service 正在运行
- 检查头显是否已连接
- 确认勾选了 head, hand, controller
- 按住右手握持键激活控制

### 更多问题
查看 **[常见问题解答](./FAQ.md)**

---

## 📚 下一步

- 详细使用说明 → [使用手册](./02_USER_GUIDE.md)
- 技术细节 → [集成文档](./03_INTEGRATION.md)
- 返回文档首页 → [README](./README.md)

---

**提示**: 首次使用建议先运行测试脚本验证硬件连接。
