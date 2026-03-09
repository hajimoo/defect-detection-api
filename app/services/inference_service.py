def run_inference(file_bytes: bytes, file_name: str):
    # 나중에 실제 모델추론 결과로 대체
    prediction = "defect"
    confidence = 0.91

    return {
        "image_name": file_name,
        "prediction": prediction,
        "confidence": confidence
    }
