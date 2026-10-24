# Сайт «Очаково — Первая смена»

Актуальные файлы сайта, backend и конфигурация из `Hackathon_2026_Ochakovo` (версия `750f2fcc840c09d0b793cba76a85f6cd553b7c6f`).

## Запуск

Скопируйте `.env.example` в `.env`, задайте значения секретов и запустите сервисы:

```sh
cp .env.example .env
docker compose up --build
```

Сайт будет доступен на `http://localhost:8080`.

## Игровая сцена

WebGL-сборки Unity в исходном проекте пока нет. Поэтому `web/public/unity/index.html` содержит заглушку: iframe загружается без ошибки и сообщает, что сцена готовится. Сам проект Unity хранится в исходном репозитории в `OchakovoFactoryWorld/`.
