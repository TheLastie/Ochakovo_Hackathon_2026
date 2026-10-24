FROM node:24-slim AS frontend
WORKDIR /app
COPY Цифровой инструмент/site/package*.json Цифровой инструмент/site/tsconfig.json Цифровой инструмент/site/vite.config.js ./
COPY Цифровой инструмент/site/web ./web
RUN npm ci && npm run build

FROM python:3.13-slim
WORKDIR /app
COPY Цифровой инструмент/site/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY Цифровой инструмент/site/backend ./backend
COPY Цифровой инструмент/site/brand ./brand
COPY Цифровой инструмент/site/web/content.json ./web/content.json
COPY Цифровой инструмент/site/web/templates ./web/templates
COPY Цифровой инструмент/site/web/public ./web/public
COPY Видеоролик о компании ./company-videos
COPY Концепция бренда/Документы ./concept-docs
COPY --from=frontend /app/web/dist ./web/dist
ENV PYTHONUNBUFFERED=1
WORKDIR /app/backend
