from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas import PredictionResponse

from PIL import Image
import io

router = APIRouter(tags=["predict"])

@router.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    # 1) 파일 타입 체크
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Only jpg/png images are supported")

    # 2) bytes 읽기
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # 3) 이미지가 진짜 열리는지 체크 (깨진 파일 방지)
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # 4) TODO: 여기에 전처리/모델추론 붙이면 됨
    #    예) img = img.resize((256, 256))
    #    예) model.predict(...)

    # 지금은 더미 응답
    return PredictionResponse(label="normal", confidence=0.50)