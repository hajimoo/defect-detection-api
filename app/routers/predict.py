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

    # ファイルを保存
    stored_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(stored_path, "wb") as f:
        f.write(file_bytes)

    # ファイルハッシュを計算
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    file_size = len(file_bytes)

    # AI推論を実行
    result = run_inference(file_bytes, file.filename)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. uploaded_imagesに保存
        cursor.execute(
            """
            INSERT INTO uploaded_images (user_id, original_filename, stored_path, mime_type, file_size, file_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                1,  # 認証実装後に実際のuser_idに置き換え
                file.filename,
                stored_path,
                file.content_type,
                file_size,
                file_hash
            )
        )
        image_id = cursor.lastrowid

        # 2. predictionsに保存
        cursor.execute(
            """
            INSERT INTO predictions (image_id, user_id, label, confidence, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                image_id,
                1,  # 認証実装後に実際のuser_idに置き換え
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
