# 📦 Сервис доставки (FastAPI)

Микросервис для регистрации посылок и расчета стоимости международной доставки.

Проект учебный, но сделан в формате, который нормально показывать на ревью и в портфолио: API, БД, кэш, фоновые задачи, тесты, линтеры, Docker.

## ✨ Что умеет сервис

- регистрирует посылку (`POST /api/v1/parcels/`)
- отдает справочник типов (`GET /api/v1/parcel-types/`)
- показывает список **моих** посылок с фильтрами и пагинацией (`GET /api/v1/parcels/`)
- отдает одну посылку по id, если она моя (`GET /api/v1/parcels/{id}`)
- раз в 5 минут считает `delivery_cost_rub` для необработанных посылок (Celery Beat + Worker)

Формула из ТЗ:

```text
(weight_kg * 0.5 + declared_cost_usd * 0.01) * usd_rub_rate
```

Курс USD/RUB берется из CBR (`https://www.cbr-xml-daily.ru/daily_json.js`) и кешируется в Redis.

## 🧰 Стек

- FastAPI (async)
- SQLAlchemy (async) + Alembic
- PostgreSQL
- Redis
- Celery (worker + beat)
- Poetry
- Pytest + httpx
- Ruff + pre-commit
- Docker Compose

## 🚀 Быстрый старт (Docker)

1. env-шаблон:

```bash
cp .env.example .env
```

2. Сервисы:

```bash
make up
```

3. Миграции:

```bash
make dmigrate
```

4. Открой Swagger:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

Примечание:
- авторизации нет специально (по ТЗ)
- пользователь определяется по cookie `delivery_session_id`
- в dev cookie `secure=False`, чтобы работало по обычному `http`

## 🔌 API

Все ручки живут под префиксом `/api/v1`.

### Получить типы посылок

```bash
curl -s http://127.0.0.1:8000/api/v1/parcel-types/
```

### Зарегистрировать посылку (создаст cookie)

```bash
curl -i -c cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"title":"Наушники","weight_kg":0.4,"type_id":2,"declared_cost_usd":150}' \
  http://127.0.0.1:8000/api/v1/parcels/
```

### Получить список своих посылок

```bash
curl -s -b cookies.txt "http://127.0.0.1:8000/api/v1/parcels/?page=1&size=20"
```

Фильтры:
- `type_id` — по типу
- `has_delivery_cost=true|false` — рассчитана стоимость или нет

Пример:

```bash
curl -s -b cookies.txt "http://127.0.0.1:8000/api/v1/parcels/?has_delivery_cost=false"
```

### Получить одну посылку по id

```bash
curl -s -b cookies.txt http://127.0.0.1:8000/api/v1/parcels/<PARCEL_ID>
```

Если открыть посылку из другой cookie-сессии, будет `404`.

## ⚙️ Фоновые задачи

Периодический пересчет запускается Celery Beat каждые 5 минут.

### Ручной запуск задачи (вне расписания)

Локально:

```bash
make task-once
```

В Docker:

```bash
make dtask-once
```

Полезно для отладки: не надо ждать 5 минут, чтобы проверить расчет.

## 🛠 Разработка

Локальный запуск без Docker:

```bash
poetry install
poetry run pre-commit install
poetry run alembic upgrade head
poetry run uvicorn delivery_service.main:app --reload
```

## 🧪 Тесты

Быстрый запуск:

```bash
poetry run pytest -q
```

Для интеграционных API-тестов нужен Postgres и переменная `TEST_DB_DSN`, например:

```bash
export TEST_DB_DSN='postgresql+asyncpg://delivery_user:delivery_password@localhost:5432/delivery_service'
poetry run pytest -q
```

## 🧹 Линтинг

```bash
poetry run ruff check .
poetry run ruff format .
poetry run pre-commit run --all-files
```

## 📌 Ограничения и заметки

- Здесь нет auth/jwt — это по ТЗ.
- Сессия живет в cookie: если удалить cookie, для API это уже “другой пользователь”.
- Это не production-конфиг “как есть”, а аккуратная учебная версия.
