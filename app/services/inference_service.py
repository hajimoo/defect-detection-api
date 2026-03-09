def run_inference(file_name: str):
    # 실제로는 모델 추론 결과를 반환
    prediction = "defect"
    confidence = 0.91

    return {
        "image_name": file_name,
        "prediction": prediction,
        "confidence": confidence
    }
