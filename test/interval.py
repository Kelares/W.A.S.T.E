from ultralytics import YOLO
import numpy as np
from io import BytesIO

# 1. Load your fine-tuned classification model
model = YOLO('model.onnx', task='classify')

# 2. Invert the names dict to map class name → index
print(model.names.items())
name2id = {v: k for k, v in model.names.items()}
bg_idx = name2id.get('background')   # index for 'background'

from picamera2 import Picamera2
from PIL import Image
import time
from libcamera import Transform

# Initialize the camera
picam2 = Picamera2()

# Grab the exact full sensor resolution
#full_res = (3280,2464) #(1920, 1080) 
full_res = (640, 480)

#full_res = next(m["size"] for m in picam2.sensor_modes if m["size"] == (3280, 2464))
#full_rest = (224,224)

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

# Check the actual scaler crop
meta = picam2.capture_metadata()
print("ScalerCrop now:", meta["ScalerCrop"])  # Should show full frame'
print("max", picam2.camera_properties)
print("ColourGains:", meta.get("ColourGains"))

choices = {}
s = time.time()
for i in range(30):
    image = picam2.capture_array()
    #Image.fromarray(image).save(f"images/took_{i}.png", quality=95)

    # 4. Run classification
    r = model.predict(
        source=image,
        imgsz=224
    )[0]  # single Results object

    # 5. Extract raw tensor, move to CPU, convert to numpy
    probs = r.probs.data.cpu().numpy()  # shape (num_classes,)

    # 6. Iterate from highest to lowest confidence
    for cls in np.argsort(probs)[::-1]:
        conf = probs[cls]
        # skip background or anything ≤ 0.8
        if cls == bg_idx or conf <= 0.8:
            continue

        label = model.names[cls]
        if label in choices:
            choices[label] += 1
        else:
            choices[label] = 1
        # print to console
        print(f"Detected: {label} ({conf:.2f})")
        #Image.fromarray(image).save(f"images/{label}_{i}.png", quality=95)
        #print(f"images/{label}_{i}.png")
print(time.time() - s, "seconds")
print(choices)
print(max(choices, key=lambda x: choices[x]))

picam2.stop()

