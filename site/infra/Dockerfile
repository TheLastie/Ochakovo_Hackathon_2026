FROM node:24-slim AS frontend
WORKDIR /app
COPY package*.json tsconfig.json vite.config.js ./
COPY web ./web
RUN npm ci && npm run build
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY brand ./brand
COPY web/content.json ./web/content.json
COPY web/templates ./web/templates
COPY --from=frontend /app/web/dist ./web/dist
ENV PYTHONUNBUFFERED=1
WORKDIR /app/backend
