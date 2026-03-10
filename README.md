# CNN Defect Detection API

製造業の欠陥検出モデルを REST API として提供する推論バックエンドのプロトタイプです。  
ノートブックでの実験を超えて、**実際のアプリケーションで利用可能な ML 推論サービス**として構築することを目的としています。

---

##  Problem

初期の CNN モデルは高い Accuracy を示しましたが、**Confusion Matrix**では欠陥サンプルを正常と誤判定するケースが確認されました。  
製造業の検査システムでは **欠陥を見逃す (False Negative)** ことが重大なリスクとなります。

- Accuracy が高くても信頼できない可能性
- クラス不均衡による評価の歪み

---

##  Investigation

データセットに深刻な **クラス不均衡** が存在していました。

| Split | Normal | Defect |
|-------|--------|--------|
| Train | 1102   | 59     |
| Test  | 276    | 15     |

このため、Accuracy だけでは信頼性を評価できないと判断しました。

---

##  Approach

評価戦略を **Accuracy 中心 → Recall 重視** に変更しました。

使用した評価指標:
- Accuracy
- Precision
- **Recall (Primary metric)**
- F1 Score
- Confusion Matrix
- ROC Curve

---

##  Model Development

ノートブック環境でモデル開発・評価を実施。  
技術スタック: **TensorFlow**, **AutoKeras ImageClassifier**

### 前処理
- RGB 変換
- 256×256 リサイズ
- ピクセル値正規化 [0,1]

### ラベル
| Label | Meaning |
|-------|---------|
| 0     | Normal  |
| 1     | Defect  |

### 学習設定
| Parameter | Value |
|-----------|-------|
| Loss      | Binary Cross Entropy |
| Validation Split | 0.2 |
| Epochs    | 3 |

---

##  From Experiment to System

ノートブックでは扱えない課題:
- 外部システムとの統合
- 推論ログ管理
- モニタリング

 **FastAPI** を用いて REST API 化しました。

---

##  API Design

### Endpoints
- `GET /health` : API health check
- `POST /predict` : 画像アップロードによる欠陥予測

### Response Example
```json
{
  "image_name": "sample.jpg",
  "prediction": "defect",
  "confidence": 0.91
}

推論フロー

Inspection Image
        ↓
POST /predict
        ↓
Image preprocessing
        ↓
CNN inference
        ↓
Prediction result
        ↓
MySQL logging

Prediction Logging
MySQL に推論結果を保存。

column	description
id	primary key
image_name	uploaded image name
prediction	predicted label
confidence	model confidence
created_at	timestamp
ログ保存により:

誤検知分析

モデル改善

モニタリング

が可能。

Project Structure

defect-detection-api
│
├── app
│   ├── routers
│   │   ├── health.py
│   │   └── predict.py
│   ├── services
│   │   ├── inference_service.py
│   │   └── model_loader.py
│   ├── db
│   │   ├── database.py
│   │   └── init.sql
│   ├── config.py
│   ├── schemas.py
│   └── main.py
│
├── notebook
│   └── notebook.ipynb
│
├── models
├── README.md
└── requirements.txt
Current Limitations
データセットが小さい

クラス不均衡が大きい

train/test サンプルの類似性

必要な検証:

Cross Validation

外部データセット評価

Threshold calibration

Future Work
モデル改善
Data Augmentation

Class weighting

Cross Validation

Larger dataset

システム改善
Docker コンテナ化

Model version 管理

推論モニタリング

API validation 強化

ech Stack
Python

FastAPI

TensorFlow

AutoKeras

MySQL

NumPy

Pillow




