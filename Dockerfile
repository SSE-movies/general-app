# === Stage 1: Build the Frontend ===
FROM node:18 AS frontend

WORKDIR /frontend
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# === Stage 2: Build the Backend ===
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY app.py .
COPY src/ ./src/

# Copy frontend build to backend's static folder
COPY --from=frontend /frontend/src/static/css/styles.css /app/static/css/

# Expose the port Flask runs on
EXPOSE 5000

# Start Flask with Gunicorn (production-ready)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]