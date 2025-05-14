from gpiozero import Servo
from time import sleep

# Use GPIO17 (pin 11) — adjust if using another pin
servo = Servo(27)

servo.min()
servo.max()
