# 1. ใช้ Python 3.11 เป็นฐาน
FROM python:3.11-slim

# 2. ติดตั้ง FFmpeg ในระดับระบบ (Linux)
# ขั้นตอนนี้จะทำให้ไฟล์ ffmpeg ไปอยู่ที่ /usr/bin/ffmpeg แน่นอน
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. ตั้งโฟลเดอร์ทำงาน
WORKDIR /app

# 4. ติดตั้ง Python Libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. ก๊อปปี้โค้ดบอททั้งหมดลงไป
COPY . .

# 6. สั่งรันบอท
CMD ["python", "main.py"]