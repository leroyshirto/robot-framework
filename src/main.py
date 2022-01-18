from core.pca9685 import PCA9685
from core.robot import Robot
import time

min_pos = 50
max_pos = 70

robot = Robot.from_config("21-dof-humanoid")

while True:

    for joint in robot.joints.values():
        print(f"moving {joint.name} to {min_pos} degrees")
        joint.angle = min_pos

    time.sleep(1)

    for joint in robot.joints.values():
        print(f"moving {joint.name} to {max_pos} degrees")
        joint.angle = max_pos

    time.sleep(2)
