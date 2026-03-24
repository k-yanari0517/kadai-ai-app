# 1. ベースイメージの指定
FROM python:3.11-slim

# 2. 作業ディレクトリの作成
WORKDIR /app

# 3. OS依存パッケージのインストール（PillowやOpenCV用）
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. 依存ライブラリのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. アプリケーションコードのコピー
COPY . .

# 6. 保存先ディレクトリの作成
RUN mkdir -p static/uploads instance

# 7. 実行コマンド (Gunicornを使用)
# AIモデルのロード時間を考慮し、タイムアウトを長めに設定
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app", "--workers", "1", "--timeout", "300"]