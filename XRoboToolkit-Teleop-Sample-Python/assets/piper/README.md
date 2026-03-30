# 松灵 Piper 机械臂 URDF 文件

## 说明

此目录用于存放松灵 Piper 机械臂的 URDF 模型文件。

## 获取 URDF 文件

### 方法 1：从松灵官方获取
联系松灵机器人技术支持获取 Piper 的官方 URDF 文件。

### 方法 2：从 ROS 包提取
如果你已经安装了 Piper 的 ROS 包：

```bash
# 查找 Piper description 包
rospack find piper_description

# 复制 URDF 文件
cp $(rospack find piper_description)/urdf/piper.urdf ~/teleop_pico/XRoboToolkit-Teleop-Sample-Python/assets/piper/
```

### 方法 3：从其他项目获取
如果你有其他使用 Piper 的项目，可以从中提取 URDF 文件。

## URDF 要求

Piper URDF 文件需要满足以下要求：

1. **关节命名**：
   - 6 个主关节：`joint1`, `joint2`, `joint3`, `joint4`, `joint5`, `joint6`
   - 夹爪关节：`gripper_joint`（可选）

2. **链接命名**：
   - 基座：`base_link`
   - 末端执行器：`link6`

3. **包含文件**：
   - URDF 文件：`piper.urdf`
   - Mesh 文件：`meshes/` 目录（如果有）

## 放置位置

将 URDF 文件放置在此目录：
```
assets/piper/
├── piper.urdf          # 主 URDF 文件
└── meshes/             # 可视化 mesh 文件（可选）
    ├── link1.stl
    ├── link2.stl
    └── ...
```

## 验证 URDF

安装 URDF 文件后，可以使用以下命令验证：

```bash
# 检查 URDF 语法
check_urdf assets/piper/piper.urdf

# 可视化 URDF
urdf_to_graphiz assets/piper/piper.urdf
```

## 临时解决方案

如果暂时没有 URDF 文件，可以：
1. 使用其他机械臂的 URDF 进行测试（如 UR5e）
2. 创建简化的 URDF 模型
3. 联系松灵技术支持获取官方文件

## 联系方式

- 松灵机器人官网：https://www.agilex.ai/
- 技术支持邮箱：support@agilex.ai
