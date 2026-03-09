from pydantic import BaseModel

class PredictionResponse(BaseModel):
    image_name: str
    prediction: str
    confidence: float
