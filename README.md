# CNN Defect Detection API

製造業における欠陥検出モデルを **REST API として提供する推論バックエンドのプロトタイプ**です。

本プロジェクトは、ノートブック環境で開発した CNN モデルを実際のアプリケーションで利用可能な **ML 推論サービス**として構築することを目的としています。

---

##  Problem
初期の CNN モデルはテストデータに対して **高い Accuracy** を示しました。  
しかし **Confusion Matrix** を確認したところ、欠陥サンプルを正常と誤判定するケースが存在していました。

製造業の検査システムでは **「欠陥を見逃す (False Negative)」** ことが重大なリスクになります。
このため、以下の問題が明らかになりました。

* Accuracy が高くても信頼できない可能性
* クラス不均衡による評価の歪み

---

##  Investigation
データセットを分析した結果、以下のような **深刻なクラス不均衡** が存在していました。

| Split | Normal | Defect |
| :--- | :--- | :--- |
| **Train** | 1102 | 59 |
| **Test** | 276 | 15 |

このようなデータでは、モデルが常に **Normal と予測するだけでも高い Accuracy** を達成できてしまいます。そのため **Accuracy だけではモデルの信頼性を評価できない** と判断しました。

---

## Approach
評価戦略を **「Accuracy 中心 → Recall 重視」** へ変更しました。  
理由は、製造業の検査システムでは **欠陥の見逃しを最小化することが最も重要** だからです。

**使用した評価指標:**
* Accuracy / Precision / **Recall (Primary Metric)** / F1 Score
* Confusion Matrix
* ROC Curve

---

## Model Development
モデル開発および評価は **Jupyter Notebook 環境** で実施しました。

**使用技術:**
* TensorFlow / AutoKeras ImageClassifier

### Preprocessing
* RGB 変換 / 256×256 リサイズ / ピクセル値の正規化 `[0, 1]`

### Label
| Label | Meaning |
| :--- | :--- |
| 0 | Normal |
| 1 | Defect |

### Training Configuration
| Parameter | Value |
| :--- | :--- |
| Loss | Binary Cross Entropy |
| Validation Split | 0.2 |
| Epochs | 3 |

---

## From Experiment to System
ノートブック環境での課題（外部システム統合、ログ管理、モニタリング）を解決するため、本プロジェクトでは CNN モデルを **FastAPI を用いた推論 API** として実装しました。

### API Design (Endpoints)
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | API health check |
| `/predict` | `POST` | 画像アップロードによる欠陥予測 |

**Response Example:**
```json
{
  "image_name": "sample.jpg",
  "prediction": "defect",
  "confidence": 0.91
}

```

### Inference Pipeline

1. **Inspection Image** (Input)
2. **POST /predict** (API Call)
3. **Image Preprocessing**
4. **CNN Inference**
5. **Prediction Result** (Output)
6. **MySQL Logging** (Data Storage)

---

##  Prediction Logging

推論結果は MySQL データベースに保存され、以下の分析が可能になります。

| Column | Description |
| --- | --- |
| `id` | Primary key |
| `image_name` | Uploaded image name |
| `prediction` | Predicted label |
| `confidence` | Model confidence |
| `created_at` | Timestamp |

* **活用例:** 誤検知分析、モデル改善、将来的なモニタリング。

---

##  Project Structure

```text
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

```

---

##  Dataset

本プロジェクトで使用したデータセットは以下のリンクから取得できます。

> [Dataset Download (Google Drive)](https://drive.google.com/drive/folders/1_mUbemlmzwXYeZPI5Bj3cG7FG53OFrxj)

*注意: 本モデルはこのデータセットを前提として学習されています。異なるドメインの画像では予測精度が低下する可能性があります。*

---

##  Current Limitations

* データセットサイズが小さい / クラス不均衡が大きい。
* Train/Test サンプルの類似性により、性能が楽観的に見えている可能性。
* **必要な検証:** Cross Validation、外部データセット評価、Threshold calibration。

---

## Future Work

* **Model:** Data Augmentation, Class Weighting, Larger Dataset.
* **System:** Docker コンテナ化, Model Version 管理, API Validation 強化.



## Tech Stack (技術スタック)

**Backend**
- Python
- FastAPI
- MySQL

**ML / DL**
- TensorFlow
- AutoKeras
- NumPy
- Pillow

---

## Setup (セットアップ)


### 1. Clone the repository
```bash
git clone https://github.com/hajimoo/defect-detection-api.git
cd defect-detection-api
```

### 2. Create virtual environment (仮想環境を作成)
```bash
python -m venv .venv
```

### 3. Activate environment (環境を有効化)
**Windows:**
```bash
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```
```


### 4. Install dependencies (依存関係をインストール)
```bash
pip install -r requirements.txt
```

### 5. Start MySQL container (MySQLコンテナを起動)
```bash
docker start mysql-container
```

### 6. Initialize database (データベース初期化)
```bash
docker exec -i mysql-container mysql -u root -p < app/db/init.sql
```

### 7. Run API server (APIサーバーを起動)
```bash
uvicorn app.main:app --reload
```

### 8. Open API documentation (APIドキュメントを開く)
```
http://127.0.0.1:8000/docs
```
## Architecture Diagram (アーキテクチャ図)

React Frontend  
  ↓  
[FastAPI Backend (API Repo)](https://github.com/hajimoo/defect-detection-api/tree/main)  
  ↓  
[CNN Model (GitHub Repo)](https://github.com/hajimoo/cnn-manufacturing-defect)  
  ↓  
MySQL 



