# CNN Defect Detection API

본 프로젝트는 불균형 데이터에서 Accuracy가 오해를 불러일으키는 문제를 Recall 우선 전략으로 해결하는 것을 목적으로 합니다.

제조업의 결함 검출 모델을 **REST API로 제공하는 추론 백엔드 프로토타입**입니다.

---

##  Problem
초기 CNN 모델은 테스트 데이터에서 **높은 Accuracy**를 보였습니다.  
그러나 **Confusion Matrix**를 확인한 결과, 결함 샘플을 정상으로 잘못 판정하는 경우가 존재했습니다.

제조업 검사 시스템에서는 **"결함을 놓치는 것 (False Negative)"** 이 중대한 리스크가 됩니다.
이에 따라 다음과 같은 문제가 드러났습니다.

* Accuracy가 높아도 신뢰할 수 없을 가능성
* 클래스 불균형으로 인한 평가 왜곡

---

##  Investigation
데이터셋을 분석한 결과, 다음과 같은 **심각한 클래스 불균형**이 존재했습니다.

| Split | Normal | Defect |
| :--- | :--- | :--- |
| **Train** | 1102 | 59 |
| **Test** | 276 | 15 |

이러한 데이터에서는 모델이 항상 **Normal로 예측하기만 해도 높은 Accuracy**를 달성할 수 있습니다. 따라서 **Accuracy만으로는 모델의 신뢰성을 평가할 수 없다**고 판단했습니다.

---

## Approach
평가 전략을 **"Accuracy 중심 → Recall 중시"** 로 변경했습니다.  
제조업 검사 시스템에서는 **결함의 누락을 최소화하는 것이 가장 중요**하기 때문입니다.

**사용한 평가 지표:**
* Accuracy / Precision / **Recall (Primary Metric)** / F1 Score
* Confusion Matrix
* ROC Curve

---

## Model Development
모델 개발 및 평가는 **Jupyter Notebook 환경**에서 수행했습니다.

**사용 기술:**
* TensorFlow / AutoKeras ImageClassifier

### Preprocessing
* RGB 변환 / 256×256 리사이즈 / 픽셀값 정규화 `[0, 1]`

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
노트북 환경의 과제(외부 시스템 통합, 로그 관리, 모니터링)를 해결하기 위해, 본 프로젝트에서는 CNN 모델을 **FastAPI를 이용한 추론 API**로 구현했습니다.

### API Design (Endpoints)
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | API health check |
| `/auth/register` | `POST` | 사용자 등록 |
| `/auth/token` | `POST` | 로그인 / access token + refresh token 발급 |
| `/auth/refresh` | `POST` | refresh token을 통한 토큰 재발급 |
| `/auth/logout` | `POST` | 로그아웃 / refresh token 무효화 |
| `/auth/password` | `PATCH` | 비밀번호 변경 |
| `/auth/me` | `DELETE` | 회원 탈퇴 |
| `/predict` | `POST` | 이미지 업로드를 통한 결함 예측 |

**Auth Response Example (`/auth/token`):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

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

## Prediction Logging

추론 결과는 추적성(트레이서빌리티)과 향후 분석을 위해 MySQL에 저장됩니다.

상세한 데이터베이스 스키마와 ER 다이어그램은 별도의 저장소(`ai-defect-detection-db`)에서 관리됩니다.

---

##  Project Structure

```text
defect-detection-api
│
├── docs/
│   ├── system_design_ja.md  
│   └── system_design_ko.md   
│
├── app
│   ├── auth
│   │   └── security.py
│   ├── routers
│   │   ├── auth.py
│   │   ├── health.py
│   │   └── predict.py
│   ├── services
│   │   ├── inference_service.py
│   │   └── model_loader.py
│   ├── db
│   │   └── database.py
│   ├── config.py
│   ├── schemas.py
│   └── main.py
│
├── ai-defect-detection-db/
│   └── sql/
│       ├── 01_schema.sql
│       ├── 02_indexes.sql
│       ├── 03_views.sql
│       └── 04_sample_data.sql
├── notebook
│   └── notebook.ipynb
│
├── models
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

##  Dataset

본 프로젝트에서 사용한 데이터셋은 아래 링크에서 받을 수 있습니다.

> [Dataset Download (Google Drive)](https://drive.google.com/drive/folders/1_mUbemlmzwXYeZPI5Bj3cG7FG53OFrxj)

*주의: 본 모델은 이 데이터셋을 전제로 학습되었습니다. 다른 도메인의 이미지에서는 예측 정확도가 떨어질 수 있습니다.*

---

##  Current Limitations

* 데이터셋 크기가 작음 / 클래스 불균형이 큼.
* Train/Test 샘플 간의 유사성으로 인해 성능이 낙관적으로 보일 가능성.
* **필요한 검증:** Cross Validation, 외부 데이터셋 평가, Threshold calibration.

---

##  System Design

- 🇯🇵 Japanese Spec: docs/system_design_ja.pdf
- 🇰🇷 Korean Spec: docs/system_design_ko.pdf

This project focuses on recall-oriented defect detection under class imbalance.

---

## Tech Stack (기술 스택)

**Backend**
- Python
- FastAPI
- MySQL
- Redis

**ML / DL**
- TensorFlow
- AutoKeras
- NumPy
- Pillow

**Infrastructure**
- Docker
- Docker Compose

---

## Setup (설정)

### Docker를 이용한 설정 (권장)

#### 1. .env 파일 생성
```bash
cp .env.example .env
# .env를 편집하여 각 값을 설정
```

#### 2. 컨테이너 실행
```bash
docker-compose up --build
```

#### 3. 확인
- 프론트엔드: http://localhost
- API 문서: http://localhost:8000/docs

---

### 로컬 환경에서의 설정

#### 1. Clone the repository
```bash
git clone https://github.com/hajimoo/defect-detection-api.git
cd defect-detection-api
```

#### 2. Create virtual environment (가상 환경 생성)
**Windows:**
```bash
py -3.11 -m venv .venv
```

**macOS/Linux:**
```bash
python3.11 -m venv .venv
```

#### 3. Activate environment (환경 활성화)
**Windows:**
```bash
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

#### 4. Install dependencies (의존성 설치)
```bash
pip install -r requirements.txt
```

#### 5. Database Setup

본 프로젝트에서는 MySQL 데이터베이스를 별도의 저장소에서 관리하고 있습니다.

https://github.com/hajimoo/ai-defect-detection-db

API를 실행하기 전에, 위 저장소의 절차에 따라 데이터베이스를 설정해 주세요.

#### 6. Run API server (API 서버 실행)
```bash
uvicorn app.main:app --reload
```

#### 7. Open API documentation (API 문서 열기)
```
http://localhost:8000/docs
```

---

## Architecture Diagram (아키텍처 다이어그램)

[React Frontend(UI)](https://github.com/hajimoo/defect-detection-frontend) 

  ↓  
[FastAPI Backend (API Repo)](https://github.com/hajimoo/defect-detection-api/tree/main)  

  ↓  
[CNN Model (GitHub Repo)](https://github.com/hajimoo/cnn-manufacturing-defect)  

  ↓  
[MySQL](https://github.com/hajimoo/ai-defect-detection-db)

---

## Authentication & Session Management

본 프로젝트에서는 JWT 기반 인증에 더해, Redis를 이용한 refresh token 관리를 도입했습니다.

### Authentication Flow
1. `/auth/register`로 사용자 등록
2. `/auth/token`으로 access token / refresh token 발급
3. access token을 사용해 보호된 API에 접근
4. access token 만료 시 `/auth/refresh`로 재발급
5. `/auth/logout`으로 refresh token 무효화
6. 비밀번호 변경 / 탈퇴 시 Redis 상의 refresh token 전체 삭제

### Security Features
- Password hashing with bcrypt
- JWT access token
- JWT refresh token
- Redis-based refresh token storage
- token_version을 통한 기존 토큰 무효화
- soft delete를 통한 탈퇴 처리

