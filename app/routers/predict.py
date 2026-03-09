from fastapi import APIRouter, UploadFile, File,HTTPException
from app.services.inference_service import run_inference
from app.db.database import get_connection

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    result = run_inference(file.filename)

    conn = get_connection()
    cursor = conn.cursor()

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
    cursor.close()
    conn.close()

    return result
