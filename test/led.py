from gpiozero import LED
from time import sleep

led = LED(26) #15)  # GPIO22 is pin 15
while True:
	led.on()
	sleep(0.1)
	led.off()
	sleep(0.1)
sleep(1)
led.on()
sleep(1)
#while True:
#	led.on()       # Turn the LED on
#	sleep(2)       # Keep it on for 5 seconds
#	led.off()
#led.off()   
