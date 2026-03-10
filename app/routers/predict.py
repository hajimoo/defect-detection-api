from fastapi import APIRouter, UploadFile, File
from app.services.inference_service import run_inference
from app.db.database import get_connection
from app.schemas import PredictionResponse

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    file_bytes = await file.read()
    result = run_inference(file_bytes, file.filename)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO predictions (image_name, prediction, confidence)
            VALUES (%s, %s, %s)
            """,
            (
                result["image_name"],
                result["prediction"],
                result["confidence"]
            )
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return result
