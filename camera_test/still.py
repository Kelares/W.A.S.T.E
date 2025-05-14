from picamera2 import Picamera2
from PIL import Image
import time
from libcamera import Transform

picam2 = Picamera2()

full_res = (640, 480)

# Force a clean still config with no preview and no lores
config = picam2.create_still_configuration(
    main={"size": full_res}, #, "format": "RGB888"},
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
meta = picam2.capture_metadata()
print("ScalerCrop now:", meta["ScalerCrop"])  # Should show full frame'
print("max", picam2.camera_properties)
print("ColourGains:", meta.get("ColourGains"))

# Check the actual scaler crop
image = picam2.capture_array()

Image.fromarray(image).save(f"test.png", quality=95)

picam2.stop()

