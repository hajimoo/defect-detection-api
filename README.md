# CNN Defect Detection API

FastAPI ベースのバックエンドで、製造業における欠陥検出モデルを REST API として提供する推論サービスのプロトタイプです。

このプロジェクトでは、ノートブック環境で開発・評価された CNN 欠陥検出モデルを、実際のアプリケーションで利用可能な API として統合することを目的としています。

現在は FastAPI バックエンド構造と MySQL による予測ログ保存機能を実装しており、今後 CNN モデル推論パイプラインを統合する予定です。

---

# Status

Work in Progress

現在の実装は **API バックエンドの基本構造とログ記録機能**を中心としたプロトタイプです。
CNN モデル推論部分は今後統合予定です。

---

## Motivation

最初の実験では、モデルは非常に高い Accuracy を示しました。

しかし、Confusion Matrix を確認すると、
いくつかの欠陥サンプルが「正常」と予測されていることに気づきました。

製造業の検査システムでは、
欠陥品の見逃し（False Negative）は重大なリスクになります。

この経験から、

「Accuracy が高いモデルは本当に信頼できるのか？」

という疑問を持つようになりました。

そこで本プロジェクトでは、
単に Accuracy を最大化するのではなく、
Recall を重視した評価戦略を採用しました。

---

# Model Development

CNN モデルの開発および評価はノートブック環境で実施しました。

関連ノートブック:

```
notebook/notebook.ipynb
```

## Dataset

クラス不均衡のある製造検査データセットを使用。

| Split | 正常   | 欠陥 |
| ----- | ---- | -- |
| Train | 1102 | 59 |
| Test  | 276  | 15 |

欠陥サンプルが非常に少ないため、Accuracy だけではモデルの信頼性を適切に評価できません。

---

## Preprocessing

画像は以下の前処理を行いました。

* RGB 変換
* 256 × 256 にリサイズ
* ピクセル値を `[0,1]` に正規化

---

## Label Encoding

| Label | Meaning |
| ----- | ------- |
| 0     | Normal  |
| 1     | Defect  |

---

## Training Setup

使用したツール:

* TensorFlow
* AutoKeras ImageClassifier

学習設定:

| Parameter        | Value                |
| ---------------- | -------------------- |
| Loss             | Binary Cross Entropy |
| Validation Split | 0.2                  |
| Epochs           | 3                    |

---

## Evaluation Metrics

本プロジェクトでは **Recall（再現率）を重視した評価**を行いました。

使用指標:

* Accuracy
* Precision
* Recall
* F1 Score
* Confusion Matrix
* ROC Curve

---

## Reliability Considerations

初期実験では高い精度が確認されましたが、以下の理由から結果が過度に楽観的である可能性があります。

* データセットサイズが小さい
* クラス不均衡が非常に大きい
* train / test サンプルの類似性

そのため、実運用前には以下の追加検証が必要です。

* Cross Validation
* 外部データセット評価
* データ拡張

---

# API Overview

本プロジェクトでは、学習済みモデルを REST API として公開する FastAPI バックエンドを構築しています。

現在の API は以下の機能を提供します。

| Endpoint      | Description        |
| ------------- | ------------------ |
| GET /health   | API health check   |
| POST /predict | 画像をアップロードして予測結果を取得 |

現在 `/predict` エンドポイントは **推論パイプライン統合前のプロトタイプ実装**であり、
プレースホルダー推論結果を返します。

---

# Architecture

```
Inspection Image
        ↓
FastAPI /predict
        ↓
Image Validation
        ↓
Inference Service
        ↓
Prediction Result
        ↓
MySQL Logging
```

将来的には以下の構成を想定しています。

```
Inspection System
        ↓
FastAPI API
        ↓
CNN Model Inference
        ↓
Prediction Result
        ↓
MySQL Prediction Logs
        ↓
Monitoring / Analytics
```

---

# Project Structure

```
app
├── routers
│   ├── health.py
│   └── predict.py
│
├── services
│   ├── model_loader.py
│   └── inference_service.py
│
├── db
│   ├── database.py
│   └── init.sql
│
├── config.py
├── schemas.py
└── main.py

notebook
└── notebook.ipynb
```

---

# Database

MySQL を使用して推論ログを保存します。

## Table

```
predictions
```

| column     | description      |
| ---------- | ---------------- |
| id         | primary key      |
| image_name | uploaded image   |
| prediction | predicted label  |
| confidence | model confidence |
| created_at | timestamp        |

---

# Setup

## Install dependencies

```
pip install -r requirements.txt
```

## Configure environment variables

`.env` ファイルを作成します。

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=defect_detection
```

---

## Initialize database

```
mysql -u root -p < app/db/init.sql
```

---

## Run API

```
uvicorn app.main:app --reload
```

API documentation:

```
http://127.0.0.1:8000/docs
```

---

# Example Response

```
{
  "image_name": "sample.jpg",
  "prediction": "defect",
  "confidence": 0.91
}
```

---

# Future Work

今後の改善予定:

* CNN モデル推論の統合
* 入力画像バリデーション
* モデルバージョン管理
* 推論ログ分析
* モニタリングダッシュボード
* Docker コンテナ化
* CI/CD パイプライン

---

# Engineering Takeaways

このプロジェクトを通じて得られた重要な知見:

* Accuracy はクラス不均衡データでは信頼できない
* ML システムにはモデル以外のインフラが重要
* 推論ログはモデル改善に不可欠

---

# Tech Stack

* Python
* FastAPI
* TensorFlow
* AutoKeras
* MySQL
* NumPy
* Pillow
* Matplotlib
