import tensorflow as tf
import autokeras as ak

MODEL_PATH = "models/defect_model.keras"

_model = None

def load_model():
    global _model

    if _model is None:
        print("Loading model...")
        _model = tf.keras.models.load_model(
            MODEL_PATH,
            custom_objects=ak.CUSTOM_OBJECTS,
            compile=False,
        )

    return _model
