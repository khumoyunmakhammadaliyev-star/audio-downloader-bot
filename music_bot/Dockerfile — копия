FROM python:3.11-slim

# ffmpeg - audio/video qayta ishlash uchun MAJBURIY (yt-dlp va audio ajratish uchun)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=10000
EXPOSE 10000

CMD ["python", "main.py"]
