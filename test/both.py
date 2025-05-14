from gpiozero import Servo
from time import sleep
from gpiozero.pins.rpigpio import RPiGPIOFactory
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero.pins.pigpio import PiGPIOFactory

# Use GPIO17 (pin 11) — adjust if using another pin
#factory = LGPIOFactory() #RPiGPIOFactory()
#factory = PiGPIOFactory()
servo_l = Servo(18) #, pin_factory=factory)
servo_r = Servo(12) #, pin_factory=factory)
servo_l.max()
servo_r.min()
try:
    while True:
#        print("Center")
 #       servo.mid()
  #      sleep(1)

        print("max")
        servo_l.max()
        servo_r.min()
        sleep(3)

        print("min")
        servo_l.min()
        servo_r.max()
        sleep(3)

except KeyboardInterrupt:
    print("Exiting...")
