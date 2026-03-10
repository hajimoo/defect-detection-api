# CNN Defect Detection API

FastAPI ベースのバックエンドで、製造業における欠陥検出モデルを REST API として提供する推論サービスのプロトタイプです。

このプロジェクトは、ノートブック環境で開発した CNN 欠陥検出モデルを、実際のアプリケーションで利用可能な API として統合することを目的として作成しました。

単なるモデル実験ではなく、

* モデル推論
* API
* 推論ログ管理

を組み合わせた **実運用を意識した ML バックエンド構造**の構築を目指しています。

---

# Problem

最初に CNN モデルを構築した際、モデルは非常に高い **Accuracy** を示しました。

しかし、詳細な評価を確認すると、いくつかの **欠陥サンプルが正常として予測されている**ことに気づきました。

製造業の検査システムでは、欠陥品を見逃すこと（False Negative）は重大な財務的・安全上のリスクになります。

つまり、

> Accuracy が高いモデルでも、実際の検査システムとしては信頼できない可能性がある

という問題がありました。

---

# Investigation

Confusion Matrix と予測結果を確認したところ、データセットには深刻な **クラス不均衡**が存在していました。

| Split | Normal | Defect |
| ----- | ------ | ------ |
| Train | 1102   | 59     |
| Test  | 276    | 15     |

このようなデータでは、モデルは単純に **「正常」と予測するだけでも高い Accuracy を達成できてしまいます。**

このため、Accuracy だけではモデルの信頼性を評価できないと判断しました。

---

# Approach

そこで本プロジェクトでは、評価戦略を以下のように変更しました。

* Accuracy だけではなく
* **Recall（再現率）を重視した評価**

を行うようにしました。

評価指標:

* Accuracy
* Precision
* **Recall**
* F1 Score
* Confusion Matrix
* ROC Curve

このアプローチは、実際の製造検査システムのリスク構造により近い評価方法になります。

---

# Model Development

モデル開発はノートブック環境で実施しました。

関連ノートブック:

```
notebook/notebook.ipynb
```

使用技術:

* TensorFlow
* AutoKeras ImageClassifier

前処理:

* RGB 変換
* 256×256 リサイズ
* ピクセル値の正規化 `[0,1]`

ラベル:

| Label | Meaning |
| ----- | ------- |
| 0     | Normal  |
| 1     | Defect  |

学習設定:

| Parameter        | Value                |
| ---------------- | -------------------- |
| Loss             | Binary Cross Entropy |
| Validation Split | 0.2                  |
| Epochs           | 3                    |

---

# From Experiment to Application

ノートブックでモデルの評価を行った後、次の課題が見えてきました。

モデル実験だけでは、

* 外部システムとの統合
* 推論ログの管理
* 将来的なモニタリング

といった **実運用の課題を扱えない**という点です。

そこで、このモデルを **FastAPI ベースの推論 API**として公開するバックエンドを構築しました。

---

# API Design

現在の API は以下のエンドポイントを提供します。

| Endpoint      | Description      |
| ------------- | ---------------- |
| GET /health   | API health check |
| POST /predict | 画像アップロードによる欠陥予測  |

推論結果は JSON として返されます。

例:

```json
{
  "image_name": "sample.jpg",
  "prediction": "defect",
  "confidence": 0.91
}
```

---

# Prediction Logging

実際の ML システムでは、推論結果のログが非常に重要になります。

このプロジェクトでは **MySQL を使用して推論ログを保存**しています。

テーブル構造:

| column     | description      |
| ---------- | ---------------- |
| id         | primary key      |
| image_name | uploaded image   |
| prediction | predicted label  |
| confidence | model confidence |
| created_at | timestamp        |

ログを保存することで、

* モデルの誤検知分析
* モデル改善
* 将来のモニタリング

が可能になります。

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

---

# Current Status

現在の `/predict` エンドポイントは **プロトタイプ実装**であり、
推論部分はプレースホルダーとなっています。

今後、

* 学習済みモデルのロード
* 実際の画像前処理
* CNN 推論パイプライン

を統合予定です。

---

# Limitations

現在の実験結果には以下の制限があります。

* データセットが小さい
* クラス不均衡が大きい
* train/test データの類似性

そのため、実運用前には追加の検証が必要です。

---

# Future Work

今後の改善予定:

* CNN モデル推論の統合
* データ拡張
* Cross Validation
* モデルバージョン管理
* Docker コンテナ化
* 推論モニタリング

---

# Engineering Takeaways

このプロジェクトから得られた重要な知見:

* 高い Accuracy は必ずしも信頼性を意味しない
* クラス不均衡データでは評価指標が重要
* ML システムには **モデル + インフラ**の両方が必要

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
