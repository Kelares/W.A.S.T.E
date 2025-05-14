from picamera2 import Picamera2
from PIL import Image
import time

# Initialize the camera
picam2 = Picamera2()

# Grab the exact full sensor resolution
full_res = next(m["size"] for m in picam2.sensor_modes if m["size"] == (3280, 2464))

# Force a clean still config with no preview and no lores
config = picam2.create_still_configuration(
    main={"size": full_res, "format": "RGB888"},
    lores=None,
    display=None,
    raw=None
)
picam2.configure(config)

# Let the camera warm up
picam2.start(show_preview=False)
time.sleep(2)

# NOW force ScalerCrop after everything is set up
picam2.set_controls({
    "ScalerCrop": (0, 0, *full_res),
    "AeEnable": True,
    "AwbEnable": True
})

# Allow settings to settle
time.sleep(1)

# Check the actual scaler crop
meta = picam2.capture_metadata()
print("ScalerCrop now:", meta["ScalerCrop"])  # Should show full frame

# Capture image
image = picam2.capture_array()
picam2.stop()

Image.fromarray(image).save("final_image.jpg", quality=95)
