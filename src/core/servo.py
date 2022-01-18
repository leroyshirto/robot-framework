import math
from machine import PWM, Pin
from .pca9685 import PCA9685


def map_angle(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


class Servo:
    """
    A abstract base class for controlling hobby servos.
    Parent classes must implement the duty methos
    Args:
        freq (int): The frequency of the signal, in hertz.
        min_pulse_us (int microseconds): The minimum signal length supported by the servo.
        max_pulse_us (int microseconds): The maximum signal length supported by the servo.
        actuation_range (int): The range between the minimum and maximum positions.
    """

    def __init__(
        self,
        freq=50,
        min_pulse_us: int = 500,
        max_pulse_us: int = 2000,
        actuation_range: int = 180,
    ):
        self.freq = freq
        self.set_pulse_width_range(min_pulse_us, max_pulse_us)
        """The physical range of motion of the servo in degrees."""
        self.actuation_range = actuation_range

    def _us2duty(self, value):
        period = 1000000 / self.freq
        print(f"period: {period}")
        return int(1024 * value / period)

    def set_pulse_width_range(self, min_pulse: int = 750, max_pulse: int = 2250):
        """Change min and max pulse widths."""
        # self._min_duty = int((min_pulse * self.freq) / 1000000 * 0xFFFF)
        self._min_duty = self._us2duty(min_pulse)
        print(f"min duty: {self._min_duty}")
        # max_duty = (max_pulse * self.freq) / 1000000 * 0xFFFF
        max_duty = self._us2duty(max_pulse)
        print(f"max duty: {max_duty}")
        self._duty_range = int(max_duty - self._min_duty)
        print(f"duty range: {self._duty_range}")

    @property
    def fraction(self):
        """Pulse width expressed as fraction between 0.0 (`min_pulse`) and 1.0 (`max_pulse`).
        For conventional servos, corresponds to the servo position as a fraction
        of the actuation range. Is None when servo is diabled (pulsewidth of 0ms).
        """
        if self.duty() == 0:  # Special case for disabled servos
            return None
        return (self.duty() - self._min_duty) / self._duty_range

    @fraction.setter
    def fraction(self, value: float = None):
        if value is None:
            self.duty(0)  # disable the motor
            return
        if not 0.0 <= value <= 1.0:
            raise ValueError("Must be 0.0 to 1.0")
        duty_cycle = self._min_duty + int(value * self._duty_range)
        print(f"duty: {duty_cycle}")
        self.duty(duty_cycle)

    @property
    def angle(self):
        """The servo angle in degrees. Must be in the range ``0`` to ``actuation_range``.
        Is None when servo is disabled."""
        if self.fraction is None:  # special case for disabled servos
            return None
        return self.actuation_range * self.fraction

    @angle.setter
    def angle(self, new_angle: int = None):
        if new_angle is None:  # disable the servo by sending 0 signal
            self.fraction = None
            return
        if new_angle < 0 or new_angle > self.actuation_range:
            raise ValueError("Angle out of range")
        self.fraction = new_angle / self.actuation_range

    def duty(self, duty: int = None):
        raise Exception("duty function must be implemented in parent")


class DirectServo(Servo):
    def __init__(
        self,
        pin: Pin,
        freq=50,
        min_pulse_us=400,
        max_pulse_us=2400,
        actuation_range=180,
    ):
        self.pin = pin
        self.pwm = PWM(pin, freq=freq, duty=0)

        super().__init__(freq, min_pulse_us, max_pulse_us, actuation_range)

    def duty(self, duty: int = None):
        if not duty:
            return self.pwm.duty()
        return self.pwm.duty(duty)


class PCAServo(Servo):
    def __init__(
        self,
        pca9685: PCA9685,
        channel: int,
        freq=50,
        min_pulse_us=600,
        max_pulse_us=2700,
        actuation_range=180,
    ):
        self.pca9685 = pca9685
        self.pca9685.freq(freq)
        self.channel = channel

        super().__init__(freq, min_pulse_us, max_pulse_us, actuation_range)

    def _us2duty(self, value):
        period = 1000000 / self.freq
        print(f"period: {period}")
        # TODO: Work out why servos on the pca need 4095
        return int(4095 * value / period)

    def duty(self, duty: int = None):
        if not duty:
            return self.pca9685.duty(self.channel)
        return self.pca9685.duty(self.channel, duty)

    def release(self):
        self.pca9685.duty(self.channel, 0)
