from gpiozero import Servo
from time import sleep

# Use GPIO17 (pin 11) — adjust if using another pin
servo = Servo(27)

try:
    while True:
#        print("Center")
 #       servo.mid()
  #      sleep(1)

        print("Right")
        servo.max()
        sleep(5)

        print("Left")
        servo.min()
        sleep(5)

except KeyboardInterrupt:
    print("Exiting...")
