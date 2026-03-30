FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 전체 복사 (models/, app/, main.py 전부 포함)
COPY . .

RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

그리고 `.dockerignore` 파일도 같이 만들어야 해. 없으면 `notebook/`, `.env` 같은 불필요한 파일까지 이미지에 들어가:
```
.env
.env.*
.gitignore
notebook/
docs/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
README.md
