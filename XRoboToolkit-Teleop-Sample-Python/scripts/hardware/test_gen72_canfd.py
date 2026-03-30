"""
测试 Gen72 通信：
Test 1: rm_movej 规划运动到 joint7=30°
Test 2: rm_movej_canfd follow=False 低跟随正弦波
"""
import sys
import time
import numpy as np

sys.path.insert(0, ".")
from Robotic_Arm.rm_robot_interface import RoboticArm, rm_thread_mode_e

IP = "192.168.1.19"
PORT = 8080

print(f"Connecting to {IP}:{PORT}...")
arm = RoboticArm(rm_thread_mode_e.RM_TRIPLE_MODE_E)
handle = arm.rm_create_robot_arm(IP, PORT)
print(f"Connected, handle id: {handle.id}")

# 切换到真实模式（必须在任何运动指令之前）
ret_mode = arm.rm_set_arm_run_mode(1)
print(f"Set real mode ret={ret_mode}")
time.sleep(0.5)

ret, mode = arm.rm_get_arm_run_mode()
print(f"Current run mode: {mode}  (0=sim, 1=real)")

ret, cur = arm.rm_get_joint_degree()
print(f"Current joints (deg): {[round(v, 2) for v in cur[:7]]}")

# 回零
print("Moving to home...")
ret = arm.rm_movej([0.0]*7, 20, 0, 0, 1)
print(f"rm_movej home ret={ret}")
time.sleep(3.0)
ret, cur = arm.rm_get_joint_degree()
print(f"After home (deg): {[round(v, 2) for v in cur[:7]]}")

# --- Test 1: 规划运动 ---
print("\n--- Test 1: rm_movej to joint7=30° ---")
target = [0.0]*7
target[6] = 30.0
ret = arm.rm_movej(target, 20, 0, 0, 1)
print(f"rm_movej ret={ret}")
time.sleep(3.0)
ret, cur = arm.rm_get_joint_degree()
print(f"After movej (deg): {[round(v, 2) for v in cur[:7]]}")

# 回零
arm.rm_movej([0.0]*7, 20, 0, 0, 1)
time.sleep(3.0)

# --- Test 2: canfd follow=False ---
print("\n--- Test 2: canfd follow=False ±30° sine ---")

AMPLITUDE = 30.0
FREQ = 0.3
DURATION = 6.0
dt = 0.02
errors = 0
t0 = time.time()
while True:
    t = time.time() - t0
    if t > DURATION:
        break
    tgt = [0.0] * 7
    tgt[6] = AMPLITUDE * np.sin(2 * np.pi * FREQ * t)
    ret = arm.rm_movej_canfd(tgt, False)
    if ret != 0:
        errors += 1
        print(f"  canfd error ret={ret} t={t:.2f}s")
    time.sleep(dt)

print(f"canfd done. errors={errors}")
ret, cur = arm.rm_get_joint_degree()
print(f"Final joints (deg): {[round(v, 2) for v in cur[:7]]}")

# 回零
print("Returning to home...")
arm.rm_movej([0.0]*7, 20, 0, 0, 1)
time.sleep(3.0)
print("Done.")
