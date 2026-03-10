# CNN Defect Detection API

製造業の欠陥検出モデルを **REST API として提供する推論バックエンドのプロトタイプ**です。

本プロジェクトでは、CNN モデルの実験結果をノートブック環境だけで終わらせず、  
**実際のアプリケーションで利用可能な ML 推論サービスとして構築すること**を目的としています。

単なるモデル実験ではなく、

- モデル推論
- API
- 推論ログ管理

を組み合わせた **ML システムのバックエンド構造**を実装しています。

---

# Problem

最初に CNN モデルを構築した際、モデルは **非常に高い Accuracy** を示しました。

しかし、Confusion Matrix を確認すると、  
**いくつかの欠陥サンプルが正常として予測されている**ことが分かりました。

製造業の検査システムでは

> 欠陥を見逃すこと（False Negative）

は重大な財務的・安全上のリスクになります。

つまり

**Accuracy が高いモデルでも、実際の検査システムとしては信頼できない可能性がある**

という問題がありました。

---

# Investigation

データセットを分析すると、深刻な **クラス不均衡** が存在していました。

| Split | Normal | Defect |
|------|------|------|
| Train | 1102 | 59 |
| Test | 276 | 15 |

このようなデータでは、
モデルがすべて「Normal」と予測しても
高い Accuracy を達成できてしまう

という問題があります。

そのため **Accuracy だけではモデルの信頼性を評価できない** と判断しました。

---

# Approach

本プロジェクトでは評価戦略を以下のように変更しました。

**Accuracy 中心 → Recall 重視**

使用した評価指標

- Accuracy
- Precision
- **Recall (Primary metric)**
- F1 Score
- Confusion Matrix
- ROC Curve

製造検査システムでは
欠陥を見逃すこと

が最も重大な失敗であるため、  
**Recall を最も重要な評価指標として扱いました。**

---

# Model Development

モデル開発と評価は **ノートブック環境**で行いました。

notebook/notebook.ipynb使用技術

- TensorFlow
- AutoKeras ImageClassifier

前処理

- RGB 変換
- 256×256 リサイズ
- ピクセル値正規化 [0,1]

ラベル

| Label | Meaning |
|------|------|
| 0 | Normal |
| 1 | Defect |

学習設定

| Parameter | Value |
|------|------|
| Loss | Binary Cross Entropy |
| Validation Split | 0.2 |
| Epochs | 3 |

---

# From Experiment to System

ノートブックでモデル評価を進める中で、次の問題に気付きました。

ノートブック環境では

- 外部システムとの統合
- 推論ログ管理
- 将来的なモニタリング

といった **実運用の課題を扱うことができない** という点です。

そこで本プロジェクトでは  
モデル実験を **ML 推論バックエンドとして拡張**しました。

---

# API Design

FastAPI を使用して、モデル推論を **REST API として公開**しています。

| Endpoint | Description |
|------|------|
| GET /health | API health check |
| POST /predict | 画像アップロードによる欠陥予測 |

### レスポンス例

```json
{
  "image_name": "sample.jpg",
  "prediction": "defect",
  "confidence": 0.91
}

#  推論の流れ
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

#Prediction Logging

実際の ML システムでは 推論ログの管理 が非常に重要になります。

このプロジェクトでは MySQL を使用して推論結果を保存しています。

| column     | description         |
| ---------- | ------------------- |
| id         | primary key         |
| image_name | uploaded image name |
| prediction | predicted label     |
| confidence | model confidence    |
| created_at | timestamp           |

ログを保存することで

誤検知分析

モデル改善

将来的なモニタリング

が可能になります。

# Project Structure

defect-detection-api
│
├── app
│   ├── routers
│   │   ├── health.py
│   │   └── predict.py
│   │
│   ├── services
│   │   ├── inference_service.py
│   │   └── model_loader.py
│   │
│   ├── db
│   │   ├── database.py
│   │   └── init.sql
│   │
│   ├── config.py
│   ├── schemas.py
│   └── main.py
│
├── notebook
│   └── notebook.ipynb
│
├── models
│
├── README.md
└── requirements.txt

# Current Limitations

現在の実験結果には以下の制限があります。

データセットが小さい

クラス不均衡が大きい

train/test サンプルの類似性

そのため、実運用前には以下の検証が必要です。

Cross Validation

外部データセット評価

threshold calibration

# 現在の実験結果には以下の制限があります。

データセットが小さい

クラス不均衡が大きい

train/test サンプルの類似性

そのため、実運用前には以下の検証が必要です。

Cross Validation

外部データセット評価

threshold calibration
