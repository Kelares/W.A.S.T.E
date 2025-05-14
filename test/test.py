import cv2
from ultralytics import YOLO
import numpy as np

# 1. Load your fine-tuned classification model
model = YOLO('v11s.onnx', task='classify')

# 2. Invert the names dict to map class name → index
name2id = {v: k for k, v in model.names.items()}
bg_idx = name2id.get('background')   # index for 'background'

# 3. Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError('Cannot open webcam')

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 4. Run classification
    r = model.predict(
        source=frame,
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
        # print to console
        print(f"Detected: {label} ({conf:.2f})")

        # overlay on frame
        cv2.putText(
            frame,
            f"{label} {conf:.2f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 255, 0), 2
        )
        break

    # 7. Display
    cv2.imshow('YOLOv8 Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
