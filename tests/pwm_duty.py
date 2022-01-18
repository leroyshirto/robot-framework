def us2duty(value, freq):
    period = 1000000 / freq
    print(f"period: {period}")
    return int(4095 * value / period)

def calc_pulse_width_range(freq=50, min_pulse: int = 750, max_pulse: int = 2250):
    """Change min and max pulse widths."""
    # min_duty = int((min_pulse * freq) / 1000000 * 0xFFFF)
    min_duty = us2duty(value=min_pulse, freq=freq)
    print(f"min duty: {min_duty}")
    # max_duty = (max_pulse * freq) / 1000000 * 0xFFFF
    max_duty = us2duty(value=max_pulse, freq=freq)
    print(f"max duty: {max_duty}")
    duty_range = int(max_duty - min_duty)
    print(f"duty range: {duty_range}")

if __name__ == '__main__':
    # calc_pulse_width_range(freq=50, min_pulse = 400, max_pulse = 2500)
    calc_pulse_width_range(freq=50, min_pulse = 600, max_pulse = 2400)