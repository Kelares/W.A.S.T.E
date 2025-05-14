from picamera2 import Picamera2
import time

picam2 = Picamera2()

config = picam2.create_still_configuration(
    main={"size": (3280, 2464), "format": "RGB888"},
    display=None
)
picam2.configure(config)

picam2.start(show_preview=False)
picam2.set_controls({
    "AwbEnable": True,
    "AeEnable": True
})

print("Letting AWB settle on white reference...")
time.sleep(3)

metadata = picam2.capture_metadata()
gains = metadata.get("ColourGains", (1.0, 1.0))
print("Suggested manual ColourGains:", gains)

picam2.stop()
