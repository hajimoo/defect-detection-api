# CNN Defect Detection API

FastAPI ベースのバックエンドで、製造業における欠陥検出モデルを REST API として提供する推論サービス。

## Status
**開発中（Work in Progress）**

## Overview
本プロジェクトは、訓練済みCNN欠陥検出モデルをREST APIとして公開し、
外部システムが検査画像を送信して予測結果を取得できるようにすることを目的としています。

このモデルはもともとノートブック環境で開発・評価されましたが、
実際のアプリケーションで利用できるようにするため、
FastAPI を用いた軽量な推論 API を構築しています。

## Planned Features

- 画像アップロードによる欠陥予測エンドポイント
- CNNモデル推論の統合
- 入力画像のバリデーション
- 信頼度スコア付き予測レスポンス
- 推論ログの記録

## Tech Stack

- FastAPI
- Python
- TensorFlow / AutoKeras
- Pillow
- NumPy

## Project Structure

```
app
├ main.py
├ routers
│   └ health.py
│   └ predict.py
├ schemas.py
└ services(미완)
    └ model_loader.py(미완)
```
