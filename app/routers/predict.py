import os
import hashlib
from fastapi import APIRouter, UploadFile, File
from app.services.inference_service import run_inference
from app.db.database import get_connection
from app.schemas import PredictionResponse

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    file_bytes = await file.read()

    # 파일 저장
    stored_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(stored_path, "wb") as f:
        f.write(file_bytes)

    # 파일 해시 계산
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    file_size = len(file_bytes)

    # AI 추론
    result = run_inference(file_bytes, file.filename)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 1. uploaded_images에 저장
        cursor.execute(
            """
            INSERT INTO uploaded_images (user_id, original_filename, stored_path, mime_type, file_size, file_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                1,  # 추후 인증 구현 시 실제 user_id로 교체
                file.filename,
                stored_path,
                file.content_type,
                file_size,
                file_hash
            )
        )
        image_id = cursor.lastrowid

        # 2. predictions에 저장
        cursor.execute(
            """
            INSERT INTO predictions (image_id, user_id, label, confidence, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                image_id,
                1,  # 추후 인증 구현 시 실제 user_id로 교체
                result["prediction"],
                result["confidence"],
                "success"
            )
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()

    return result
