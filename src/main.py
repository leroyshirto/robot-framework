from core.pca9685 import PCA9685
from core.servo import DirectServo, PCAServo
import machine
import time

sda = machine.Pin(22)
scl = machine.Pin(21)

i2c = machine.I2C(sda=sda, scl=scl)
i2c.scan()
pca9685 = PCA9685(i2c)

min_pos=0
max_pos=180

head_servo = DirectServo(machine.Pin(19), min_pulse_us=400, max_pulse_us=2400, actuation_range=180)
arm_servo = PCAServo(pca9685, channel=0, min_pulse_us=600, max_pulse_us=2700, actuation_range=180)

while True:
    print(f"moving head to {min_pos} degrees")
    head_servo.angle = min_pos
    print(f"moving arm to {min_pos} degrees")
    arm_servo.angle = min_pos
    time.sleep(2)
    print(f"moving head to {max_pos} degrees")
    head_servo.angle = max_pos
    print(f"moving arm to {max_pos} degrees")
    arm_servo.angle = max_pos
    time.sleep(5)
