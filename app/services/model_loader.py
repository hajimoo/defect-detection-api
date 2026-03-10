import tensorflow as tf

MODEL_PATH = "models/defect_model.keras"

_model = None

def load_model():
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(MODEL_PATH)
    return _model
