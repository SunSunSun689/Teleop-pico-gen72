# Piper 遥操作故障排查记录

## 问题日期：2026-03-31

### 问题描述
换到新机器后，Piper机械臂遥操作无法正常工作，机械臂不响应VR手柄的控制指令。

---

## 问题排查过程

### 1. XR数据接收问题

**现象**：
- XRoboToolkit PC Service虽然运行，但所有XR数据（位置、按钮）都返回0
- 测试脚本显示：位置 `[0.000, 0.000, 0.000]`，Grip: `0.000`，Trigger: `0.000`

**原因**：
- XRoboToolkit PC Service只监听在 `127.0.0.1:60061`（本地回环地址）
- Pico头显无法连接到本地回环地址，需要连接到实际的网络IP地址

**解决方案**：
- 重新配置XRoboToolkit PC Service，确保头显正确连接
- 头显IP：`10.168.129.153`，PC IP：`10.168.129.15`
- 确认头显和PC在同一WiFi网络下

**验证**：
```bash
# 测试XR数据接收
python3 scripts/hardware/test_xr_buttons.py
```
成功后应该能看到实时的位置和按钮数据变化。

---

### 2. Piper机械臂第6关节使能失败

**现象**：
```
TimeoutError: Failed to enable Piper robot within timeout, status: [True, True, True, True, True, False]
```
- 前5个关节成功使能，第6个关节始终无法使能
- 第6个关节位置读数异常：`20865`（其他关节为0）

**原因**：
- 硬件故障或电源问题
- 可能是第6关节的电机驱动器、CAN通信线路或编码器故障

**解决方案**：
- **重启Piper机械臂**（断电重启）
- 重新设置CAN总线：
```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 1000000
```

**验证**：
```bash
# 测试关节使能状态
python3 scripts/hardware/test_piper_enable.py
```
成功后应该显示：`使能后状态: [True, True, True, True, True, True]`

---

### 3. Dora框架依赖问题（未解决）

**现象**：
```
ModuleNotFoundError: No module named 'xrobotoolkit_teleop'
ModuleNotFoundError: No module named 'meshcat'
```

**原因**：
- Dora使用系统Python（`/usr/bin/python3`）而不是虚拟环境中的Python
- 系统Python缺少必要的依赖包

**临时解决方案**：
- 直接使用虚拟环境中的Python运行遥操作脚本，绕过Dora框架：
```bash
/home/dora/RoboDriver/robodriver/teleoperators/robodriver-teleoperator-pico-ultra4-dora/.venv/bin/python3 \
    scripts/hardware/teleop_piper_hardware.py
```

**长期解决方案**（待实施）：
- 在系统Python中安装所有依赖包
- 或修改Dora配置使用虚拟环境中的Python

---

## 最终解决方案

### 启动步骤

1. **设置CAN总线**：
```bash
sudo ip link set can0 up type can bitrate 1000000
```

2. **启动XRoboToolkit PC Service**（如果未运行）：
```bash
cd /opt/apps/roboticsservice
bash run3D.sh > /tmp/robotics_service.log 2>&1 &
```

3. **确认头显连接**：
- 头显和PC在同一WiFi网络
- 头显上的XRoboToolkit应用正在运行
- 测试XR数据接收正常

4. **启动Piper遥操作**：
```bash
cd /home/dora/teleop_pico/XRoboToolkit-Teleop-Sample-Python
/home/dora/RoboDriver/robodriver/teleoperators/robodriver-teleoperator-pico-ultra4-dora/.venv/bin/python3 \
    scripts/hardware/teleop_piper_hardware.py
```

5. **操作方式**：
- 按住右手柄的**grip按钮**（握持键）激活遥操作
- 移动手柄控制机械臂位置
- 按下**trigger按钮**（扳机键）控制夹爪

---

## 关键检查点

### 检查XR连接
```bash
# 测试XR数据
python3 scripts/hardware/test_xr_buttons.py
```
应该看到实时的位置和按钮数据。

### 检查Piper状态
```bash
# 测试Piper使能和位置
python3 scripts/hardware/test_piper_enable.py
```
应该显示所有6个关节都已使能。

### 检查CAN总线
```bash
# 查看CAN总线状态
ip link show can0
```
应该显示 `UP` 状态。

---

## 常见问题

### Q: 机械臂不响应手柄控制
**A**: 检查以下几点：
1. 是否按住了grip按钮（握持键）？只有按住grip才会激活控制
2. XR数据是否正常接收？运行测试脚本验证
3. Piper是否所有关节都已使能？运行测试脚本验证

### Q: 第6关节无法使能
**A**:
1. 断电重启Piper机械臂
2. 重新设置CAN总线
3. 检查第6关节的电源和CAN通信线连接

### Q: XR数据全是0
**A**:
1. 确认头显和PC在同一WiFi网络
2. 重启XRoboToolkit PC Service
3. 重启头显上的XRoboToolkit应用

---

## 测试脚本

### test_xr_buttons.py
测试XR手柄数据接收，显示实时的位置和按钮状态。

### test_piper_enable.py
测试Piper机械臂的使能状态和关节位置读数。

---

## 相关文件

- 遥操作主程序：`scripts/hardware/teleop_piper_hardware.py`
- Piper接口：`xrobotoolkit_teleop/hardware/interface/piper.py`
- Piper控制器：`xrobotoolkit_teleop/hardware/piper_teleop_controller.py`
- Dora配置：`/home/dora/RoboDriver/robodriver/teleoperators/robodriver-teleoperator-pico-ultra4-dora/dora/dataflow.yml`

---

## 更新日期
2026-03-31
