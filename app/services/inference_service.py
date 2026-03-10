from io import BytesIO
import numpy as np
from PIL import Image

from app.services.model_loader import load_model


def preprocess_image(file_bytes: bytes):
    image = Image.open(BytesIO(file_bytes))
    image = image.convert("RGB")
    image = image.resize((256, 256))
    image = np.array(image, dtype=np.float32) / 255.0
    image = np.expand_dims(image, axis=0)
    return image


def run_inference(file_bytes: bytes, file_name: str):
    print("run_inference called")

    model = load_model()
    print("model loaded")

    input_image = preprocess_image(file_bytes)
    print("input shape:", input_image.shape)

    pred = model.predict(input_image)
    print("raw prediction:", pred)

    confidence = float(pred[0][0])

    if confidence >= 0.5:
        prediction = "defect"
    else:
        prediction = "normal"

    return {
        "image_name": file_name,
        "prediction": prediction,
        "confidence": confidence
    }
