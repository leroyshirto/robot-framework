from core.pca9685 import PCA9685
from core.robot import Robot
import time

min_pos = 70
max_pos = 100

robot = Robot.from_config("21-dof-humanoid")

while True:

    for joint in robot.joints.values():
        print(f"moving {joint.name} to {min_pos} degrees")
        joint.angle = min_pos
        print(f"{joint.name} current angle: {joint.angle}")

    time.sleep(1)

    for joint in robot.joints.values():
        print(f"moving {joint.name} to {max_pos} degrees")
        joint.angle = max_pos
        print(f"{joint.name} current angle: {joint.angle}")

    time.sleep(2)
