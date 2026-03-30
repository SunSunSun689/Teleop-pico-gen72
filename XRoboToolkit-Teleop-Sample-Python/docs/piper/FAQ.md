# Piper 常见问题解答 (FAQ)

---

## 🔌 硬件连接问题

### Q1: CAN 设备未找到
**问题**: 运行时提示找不到 can0

**解决方案**:
```bash
# 检查 CAN 设备
ls /sys/class/net/ | grep can

# 如果没有，检查 CAN 适配器
lsusb
dmesg | grep can
```

### Q2: CAN 连接失败
**问题**: 提示 "Failed to connect CAN port"

**解决方案**:
```bash
# 重新配置 CAN
sudo ip link set can0 down
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up

# 验证状态
ip -details link show can0
```

### Q3: 权限被拒绝
**问题**: Permission denied 错误

**解决方案**:
```bash
# 添加用户到 dialout 组
sudo usermod -a -G dialout $USER

# 重新登录生效
```

---

## 🤖 机械臂控制问题

### Q4: 机械臂不响应
**可能原因**:
1. 未按住握持键激活控制
2. PC Service 未运行
3. 头显未连接

**解决方案**:
```bash
# 检查 PC Service
ps aux | grep RoboticsService

# 重启 PC Service
cd /opt/apps/roboticsservice
bash runService.sh
```

### Q5: 机械臂运动异常
**问题**: 机械臂运动不流畅或抖动

**解决方案**:
```bash
# 降低控制频率
python scripts/hardware/teleop_piper_hardware.py \
    --can-port can0 \
    --control-rate-hz 30

# 调整缩放因子
python scripts/hardware/teleop_piper_hardware.py \
    --can-port can0 \
    --scale-factor 1.0
```

### Q6: 关节超出限位
**问题**: 警告 "Joint X position clipped"

**说明**: 这是正常的安全保护，关节位置被限制在安全范围内。

**解决方案**: 调整 VR 控制器的移动范围或减小 scale_factor。

---

## 🎮 VR 控制问题

### Q7: 头显连接不上
**检查清单**:
- [ ] 头显和电脑在同一网络
- [ ] PC Service 正在运行
- [ ] 输入了正确的 IP 地址
- [ ] 勾选了 head, hand, controller

**获取电脑 IP**:
```bash
ip addr show | grep inet
```

### Q8: 控制延迟高
**优化方案**:
1. 确保在同一局域网（不要跨路由器）
2. 降低控制频率到 30-40 Hz
3. 关闭其他占用网络的程序

### Q9: 夹爪不工作
**检查**:
- 是否按了右手扳机键
- 夹爪是否已校准

**测试夹爪**:
```bash
python scripts/hardware/test_piper_interface.py --can-port can0
```

---

## 💻 软件问题

### Q10: SDK 导入失败
**问题**: ModuleNotFoundError: No module named 'piper_sdk'

**解决方案**:
```bash
conda activate pico
cd /home/dora/SDK/piper_sdk
pip install --force-reinstall .
```

### Q11: URDF 文件未找到
**问题**: FileNotFoundError: assets/piper/piper.urdf

**解决方案**:
```bash
# 检查文件是否存在
ls ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python/assets/piper/piper.urdf

# 如果不存在，重新复制
cp /home/dora/github_ros2_dora_migration/github_ros2_dora_migration/questVR_ws/src/Piper_ros/src/piper_description/urdf/piper_description.urdf \
   ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python/assets/piper/piper.urdf
```

### Q12: Placo 可视化失败
**问题**: 启用 --visualize-placo 后报错

**解决方案**:
```bash
# 检查 meshcat 是否安装
conda activate pico
pip install meshcat

# 或不使用可视化
python scripts/hardware/teleop_piper_hardware.py --can-port can0
```

---

## 🔧 配置问题

### Q13: 如何更改 CAN 端口？
```bash
# 使用 can1
python scripts/hardware/teleop_piper_hardware.py --can-port can1
```

### Q14: 如何调整控制灵敏度？
```bash
# 降低灵敏度（更稳定）
--scale-factor 1.0

# 提高灵敏度（更快响应）
--scale-factor 2.0
```

### Q15: 如何记录遥操作数据？
```bash
python scripts/hardware/teleop_piper_hardware.py \
    --can-port can0 \
    --enable-log-data \
    --log-dir logs/my_experiment
```

---

## 📊 性能问题

### Q16: 控制频率太低
**目标**: 50 Hz
**实际**: < 30 Hz

**优化**:
1. 关闭可视化 (--visualize-placo)
2. 降低日志频率
3. 检查 CPU 占用

### Q17: 内存占用过高
**解决方案**:
- 禁用数据记录
- 减少日志频率
- 定期清理日志文件

---

## 🛡️ 安全问题

### Q18: 如何紧急停止？
**方法 1**: 松开握持键（立即停止控制）
**方法 2**: 按 Ctrl+C 终止程序
**方法 3**: 断开 CAN 连接

### Q19: 机械臂碰撞怎么办？
1. 立即松开握持键
2. 按 Ctrl+C 停止程序
3. 检查机械臂状态
4. 运行测试脚本验证功能

---

## 📞 获取帮助

### 还有其他问题？

1. **查看详细文档**
   - [使用手册](./02_USER_GUIDE.md)
   - [集成文档](./03_INTEGRATION.md)

2. **查看测试报告**
   - [测试报告](./TEST_REPORT.md)

3. **检查日志**
   ```bash
   # 查看最近的日志
   ls -lt logs/piper/
   ```

4. **联系支持**
   - XRoboToolkit: https://xr-robotics.github.io/
   - 松灵机器人: support@agilex.ai

---

**最后更新**: 2026-03-11
