from ultralytics import YOLO
import numpy as np
from io import BytesIO
from multiprocessing import Process, Event
from time import sleep
from picamera2 import Picamera2
from PIL import Image
import time
from libcamera import Transform
from gpiozero import DistanceSensor, Servo

# 1. Load your fine-tuned classification model
model = YOLO('model.onnx', task='classify')

# 2. Invert the names dict to map class name → index
print(model.names.items())
name2id = {v: k for k, v in model.names.items()}
bg_idx = name2id.get('background')   # index for 'background'

# Set of all classes which open left or right trash can
left = ("paper", "cardboard")
right = ("metal", "plastic")



# Initialize the camera
picam2 = Picamera2()

# Grab the exact full sensor resolution
full_res = (640, 480)


# Force a clean still config with no preview and no lores
config = picam2.create_still_configuration(
    main={"size": full_res, "format": "RGB888"},
    lores=None,
    display=None,
    raw=None,
    buffer_count=1,
    transform=Transform(vflip=True)
)
picam2.configure(config)

# Let the camera warm up
picam2.start(show_preview=False)
time.sleep(2)
picam2.set_controls({
    "ScalerCrop": picam2.camera_properties["ScalerCropMaximum"],
})

# Allow settings to settle
time.sleep(1)

# Check the actual zoom and crop. We dont want any.
meta = picam2.capture_metadata()
print("ScalerCrop now:", meta["ScalerCrop"])  # Should show full frame'
print("max", picam2.camera_properties)
print("ColourGains:", meta.get("ColourGains"))

ultrasonic = DistanceSensor(echo=17, trigger=4)

# A function to run in the background while the scan is on going.
def blink_led(stop_event):
    led = LED(22)  # Make sure this is BCM pin 22
    try:
        while not stop_event.is_set():
            led.on()
            time.sleep(0.2)
            led.off()
            time.sleep(0.2)
    finally:
        led.off()  # Clean up
        print("LED turned off cleanly.")


# Initialize two servos
servo_r = Servo(18)
servo_l = Servo(27)

print("READY TO WORK")
try:
    while True: # MAIN LOOP.
        ultrasonic.wait_for_in_range() # WAIT FOR SOMETING TO MOVE IN FRONT OF THE SENSOR.

        # INITATE BLINKING
        stop_event = Event()
        p = Process(target=blink_led, args=(stop_event,))
        p.start()
        # ----- #

        s = time.time() # Initiate timer
        choices = {}
        for i in range(50):
            image = picam2.capture_array() # Take a picture

            # Run classification
            r = model.predict(
                source=image,
                imgsz=224
            )[0]  # single Results object
            
            # EXTRACT THE RESULT OF PREDICTION 
            # -----------------------------------------------#
            # 5. Extract raw tensor, move to CPU, convert to numpy
            probs = r.probs.data.cpu().numpy()  # shape (num_classes,)

            # 6. Iterate from highest to lowest confidence
            for cls in np.argsort(probs)[::-1]:
                conf = probs[cls]
                # Continue the search if background or anything ≤ 0.8. DIDNT CHOOSE ANYTHING
                if cls == bg_idx or conf <= 0.8:
                    continue

                label = model.names[cls]
                
                # STORE WHAT WAS SELECTED FROM SINGULAR PICTURE
                if label in choices:
                    choices[label] += 1
                else:
                    choices[label] = 1
                # print selected label to the console
                print(f"Detected: {label} ({conf:.2f})")

            # -------------------------------------------- END OF EXTRACTION #

        print(time.time() - s, "seconds") # PRINT HOW LONG 50 PICTURES TOOK
        print(choices)  # PRINT COUNTERS. HOW MANY TIMES DIFFERENT LABELS HAVE BEEN SELECTED

        if choices:
            label = max(choices, key=lambda x: choices[x])
            print(label)   # PRINT WHICH LABEL WAS SELECTED THE MOST FROM 50 PICS

            if label in left:   # OPEN LEFT LID
                print("Left")
                servo_l.max()
                time.sleep(5)
                servo_l.min()

            elif label in right:    # OPEN RIGHT LID 
                print("right")
                servo_r.min()q
                time.sleep(5)
                servo_r.max()
        # STOP BLINKING #
        stop_event.set()  # Tell subprocess to stop
        p.join() 
        # ------------- #
    
except KeyboardInterrupt:   # WHEN PROGRAM IS STOPPED VIA ctrl + C. Turn off the camera gracefully.
    print("Exiting...")
    picam2.stop()
