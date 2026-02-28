# ---------- Base Image ----------
FROM python:3.11-slim

# ---------- Environment ----------
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# ---------- Working Directory ----------
WORKDIR /app

# ---------- System Dependencies ----------
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---------- Upgrade pip ----------
RUN pip install --upgrade pip

# ---------- Install Python Dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy Application ----------
COPY app.py .
COPY src ./src
COPY artifacts ./artifacts

# ---------- Expose Ports ----------
EXPOSE 8000
EXPOSE 8501

# ---------- Start Services ----------
CMD bash -c "\
uvicorn src.main:app --host 0.0.0.0 --port 8000 & \
streamlit run app.py --server.address=0.0.0.0 --server.port=8501"