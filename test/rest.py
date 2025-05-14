import RPi.GPIO as GPIO
import time

servo_pin = 17  # GPIO17 (Pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

# Create PWM instance with 50Hz frequency (standard for servos)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)

def set_angle(angle):
    duty = 2 + (angle / 18)  # Convert angle to duty cycle
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    pwm.ChangeDutyCycle(0)  # Stop signal to avoid jitter


while True:
    for angle in range(0, 181, 30):  # Sweep 0 to 180
        set_angle(angle)
        time.sleep(1)
    for angle in range(180, -1, -30):  # Sweep back
        set_angle(angle)
        time.sleep(1)


pwm.stop()
GPIO.cleanup()