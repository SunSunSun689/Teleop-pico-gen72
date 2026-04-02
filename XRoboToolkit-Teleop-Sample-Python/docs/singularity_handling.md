# 奇异点处理分析：xr_teleoperate vs 本项目

## 1. xr_teleoperate 的方案

### 核心思路
**没有显式奇异点检测**，而是通过优化求解器的内在特性 + 多层约束隐式规避。

### IK 求解器：CasADi + IPOPT
将 IK 建模为约束非线性优化问题，天然比 Jacobian 伪逆法更鲁棒（伪逆法在奇异点附近会数值爆炸）。

目标函数：
```python
opti.minimize(
    50   * translational_cost    # 位置误差（高权重）
  + 1.0  * rotation_cost         # 姿态误差
  + 0.02 * regularization_cost   # 正则化：sumsqr(q)，拉向零位
  + 0.1  * smooth_cost           # 平滑：sumsqr(q - q_last)，抑制突变
)
```

硬约束：关节限位直接排除大量奇异构型（如肘关节完全伸直）。

### 热启动（Warm Start）
每帧从上一帧关节角初始化，求解器在构型空间中平滑移动，不会跳入奇异区域。

### 求解失败 Fallback
```python
except Exception as e:
    sol_q = self.opti.debug.value(self.var_q)  # 取最优中间解
    return current_lr_arm_motor_q, np.zeros(...)  # 失败则保持当前位置
```
IPOPT 不收敛时（奇异点附近最可能触发），机械臂原地保持，不产生危险运动。

### 加权移动平均滤波
```python
WeightedMovingFilter(np.array([0.4, 0.3, 0.2, 0.1]), 14)
```
对 IK 输出做时域平滑，抑制奇异点附近解的抖动。

### 执行层速度限幅（最后一道防线）
```python
def clip_arm_q_target(self, target_q, velocity_limit):
    delta = target_q - current_q
    motion_scale = np.max(np.abs(delta)) / (velocity_limit * control_dt)
    return current_q + delta / max(motion_scale, 1.0)
```
即使 IK 输出突变解，电机指令层也按比例缩放，限制每帧最大关节速度。

---

## 2. 本项目的方案（Placo）

```python
# base_teleop_controller.py:160
manipulability = solver.add_manipulability_task(link_name, "both", 1.0)
manipulability.configure("manipulability", "soft", 1e-2)
```

Placo 通过 manipulability task 作为软约束，在 IK 求解时倾向于远离奇异构型。权重 `1e-2` 较弱，末端跟随任务优先级更高。

---

## 3. 对比

| 特性 | xr_teleoperate (IPOPT) | 本项目 (Placo) |
|------|----------------------|----------------|
| IK 方法 | 非线性优化 | 数值 IK |
| 奇异点检测 | 无显式检测 | manipulability 软约束 |
| 奇异点回避 | 正则化 + 关节限位硬约束 | manipulability 权重 |
| 失败处理 | 保持当前位置 | 无显式 fallback |
| 输出平滑 | 加权移动平均滤波 | 无 |
| 执行层限幅 | 有（速度限幅） | 无 |

---

## 4. 能否复用

### 可以直接复用的部分

**① 执行层速度限幅**（优先级最高，改动最小）

在 `Gen72Interface.set_joint_positions` 中加入：

```python
def _clip_joint_target(self, target_q, max_deg_per_step=2.0):
    current_q = self.get_joint_positions()  # 弧度
    delta = target_q - current_q
    max_delta = np.deg2rad(max_deg_per_step)
    scale = np.max(np.abs(delta)) / max_delta
    if scale > 1.0:
        target_q = current_q + delta / scale
    return target_q
```

**② 加权移动平均滤波**（改动小，效果明显）

```python
class WeightedMovingFilter:
    def __init__(self, weights, dim):
        self.weights = weights / weights.sum()
        self.buffer = deque(maxlen=len(weights))
        self.dim = dim

    def update(self, new_data):
        self.buffer.append(new_data)
        data = np.array(self.buffer)
        w = self.weights[-len(data):]
        w = w / w.sum()
        return (data * w[:, None]).sum(axis=0)
```

**③ IK 失败 Fallback**（在 `_send_command` 中加保护）

当 Placo 求解结果与当前关节角偏差过大时，跳过本帧命令。

### 不建议复用的部分

- **IPOPT 替换 Placo**：工程量大，且 Placo 已经集成在项目中，稳定运行
- **正则化目标函数**：Placo 内部已有类似机制

---

## 5. 建议优先实施

1. **速度限幅**：最简单，直接防止奇异点附近的关节突变
2. **加权移动平均滤波**：平滑 IK 输出，减少抖动
3. **提高 manipulability 权重**：将 `1e-2` 适当提高到 `5e-2`，增强回避能力
