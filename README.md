# VSTK Schedule System

> Система получения актуального расписания пар для учащихся и преподавателей
> УО «Витебский государственный технический колледж» через Telegram-бот.

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-@lessons__vstk__bot-2CA5E0?logo=telegram&logoColor=white)](https://t.me/lessons_vstk_bot)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Deploy-Docker%20%2B%20k3s-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

---

## Содержание

- [О проекте](#о-проекте)
- [Возможности](#возможности)
- [Архитектура](#архитектура)
- [Технологический стек](#технологический-стек)
- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Конфигурация](#конфигурация)
- [API Reference](#api-reference)
- [Тестирование](#тестирование)
- [Структура проекта](#структура-проекта)

---

## О проекте

**VSTK Schedule System** — микросервисная система, которая автоматически получает расписание занятий с официального сайта колледжа и предоставляет его более чем **600 учащимся и преподавателям** через Telegram-бот в удобном формате.

**Проблема:** официальный сайт колледжа неудобен для просмотра расписания с мобильного устройства, а уведомления об изменениях отсутствуют.

**Решение:** Telegram-бот с поддержкой подписки на группу или кабинет, отображением расписания на сегодня/завтра и мгновенными уведомлениями при изменении расписания.

🤖 **Бот доступен по адресу:** [@lessons_vstk_bot](https://t.me/lessons_vstk_bot)

---

## Возможности

- **Расписание по группе** — учащийся выбирает свою группу и получает расписание на сегодня или завтра.
- **Расписание по кабинету** — преподаватель выбирает кабинет и видит, какие пары в нём проходят.
- **Гибкий поиск** — ввод номера группы или кабинета в произвольном формате (`ЖБИ-31`, `жби31`, `ОС 31`).
- **Подписка на уведомления** — оперативное оповещение при изменении расписания.
- **Профиль пользователя** — раздельный режим для учащихся и преподавателей, управление уведомлениями.
- **Актуальность данных** — парсер регулярно обновляет расписание из источника.

---

## Архитектура

Система состоит из **трёх независимых микросервисов** и общей библиотеки моделей БД:

```
┌─────────────────────────────────────────────────────────┐
│                    Сайт колледжа                        │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (расписание в HTML)
                         ▼
┌─────────────────────────────────────────────────────────┐
│              service_parser (Парсер)                    │
│  • Загружает HTML, парсит расписание (BS4 + lxml)       │
│  • Обрабатывает матрицу расписания (NumPy)              │
│  • CPU-bound задачи изолированы от обработки сообщений  │
│  • Сохраняет данные в PostgreSQL                        │
└────────────────────────┬────────────────────────────────┘
                         │ PostgreSQL (общая БД)
                         ▼
┌─────────────────────────────────────────────────────────┐
│              service_api (REST API)                     │
│  • FastAPI — предоставляет расписание по HTTP           │
│  • Redis — кэширование ответов                          │
│  • Watchfiles — горячая замена секретов                 │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (HTTPX)
                         ▼
┌─────────────────────────────────────────────────────────┐
│              service_bot (Telegram-бот)                 │
│  • Aiogram — интерфейс для пользователей                │
│  • Jinja2 — шаблонизация сообщений                      │
│  • PostgreSQL — хранение профилей пользователей         │
│  • Redis — состояния FSM                                │
└────────────────────────┬────────────────────────────────┘
                         │ Telegram Bot API
                         ▼
                    Пользователи
```

**Ключевое преимущество изоляции:** сбой или высокая нагрузка на один сервис не влияет на доступность остальных.

**Хранилище секретов:** HashiCorp Vault с «горячей» заменой через watchfiles — секреты обновляются без перезапуска сервисов.

**Архитектурный паттерн:** DDD (Domain-Driven Design) — каждый сервис имеет явно разделённые слои `domain`, `application`, `infrastructure`, `presentation`.

---

## Технологический стек

| Компонент | Технологии |
|---|---|
| **Парсер** | Python 3.12, BeautifulSoup4, lxml, NumPy, SQLAlchemy, asyncpg, Dishka, Redis, HTTPX |
| **API** | Python 3.12, FastAPI, Uvicorn, SQLAlchemy, asyncpg, Dishka, Redis, watchfiles |
| **Бот** | Python 3.12, Aiogram 3, HTTPX, SQLAlchemy, asyncpg, Dishka, Jinja2, Redis, watchfiles |
| **База данных** | PostgreSQL |
| **Кэш / FSM** | Redis |
| **Миграции** | Alembic |
| **Зависимости** | Poetry |
| **DI-фреймворк** | Dishka |
| **Секреты** | HashiCorp Vault |
| **Тесты** | Pytest, pytest-asyncio, pytest-httpx, testcontainers, aiogram-test-framework, pytest-cov |
| **Деплой** | Docker, Kubernetes (k3s) |
| **Линтер** | Ruff |

---

## Требования

- Python **3.12–3.14**
- [Poetry](https://python-poetry.org/) `>= 2.0`
- PostgreSQL
- Redis
- Docker и Docker Compose (для контейнерного запуска)

---

## Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/AL32029/VSTKScheduleSystem.git
cd VSTKScheduleSystem
git checkout dev
```

### 2. Установите зависимости для нужного сервиса

```bash
# Например, для API-сервиса
cd services/service_api
poetry install
```

### 3. Настройте переменные окружения

Скопируйте примеры конфигурации и заполните значения:

```bash
cp env/base.env.example env/base.env
cp env/database.env.example env/database.env
cp env/redis.env.example env/redis.env
```

Подробнее — в разделе [Конфигурация](#конфигурация).

### 4. Примените миграции

```bash
# Из корня репозитория
alembic -c schedule_alembic.ini upgrade head
```

### 5. Запустите сервис

```bash
# Из директории сервиса, например service_api
poetry run python src/service_api/main.py
```

### Запуск через Docker

Каждый сервис содержит `Dockerfile` с многоэтапной сборкой:

```bash
# Пример сборки и запуска API-сервиса
docker build \
  --build-arg libs=../../libs \
  -t vstk-service-api \
  services/service_api/

docker run --env-file services/service_api/env/base.env vstk-service-api
```

---

## Конфигурация

Конфигурация каждого сервиса задаётся через `.env`-файлы. Примеры находятся в папке `env/` каждого сервиса.

### Общие настройки (`base.env`)

```dotenv
# База данных
DATABASE_HOST=<хост>
DATABASE_PORT=<порт>
DATABASE_BASE=<имя БД>
DATABASE_SETTINGS_ENV=<путь к файлу с учётными данными БД>  # из Vault, по умолчанию /vault/secrets/database.env
DATABASE_SSL_CERT_REQS=<none|optional|required>
DATABASE_SSL_CHECK_HOSTNAME=<true|false>

# Redis
REDIS_HOST=<хост>
REDIS_PORT=<порт>
REDIS_DB_NUMBER=<номер БД>
REDIS_SETTINGS_ENV=<путь к файлу с учётными данными Redis>  # из Vault, по умолчанию /vault/secrets/redis.env
REDIS_SSL_CERT_REQS=<none|optional|required>
REDIS_SSL_CHECK_HOSTNAME=<true|false>
```

### Настройки бота (`bot_settings.env`)

```dotenv
BOT_TOKEN=<токен бота из @BotFather>
```

### Настройки подключения к API (`api_settings.env`, только для бота)

```dotenv
API_SCHEDULE_URL=<базовый URL API-сервиса, например http://service-api:8000>
```

> **Секреты** (токен бота, пароли к БД) рекомендуется хранить в **HashiCorp Vault**.
> Сервисы поддерживают «горячую» замену секретов через `watchfiles` без перезапуска.

---

## API Reference

API-сервис предоставляет REST API с автодокументацией по адресу `/docs` (Swagger UI) и `/redoc`.

### Расписание

#### `GET /schedule/group`

Расписание для группы.

| Параметр | Тип | Описание |
|---|---|---|
| `group_number` | `string` | Номер группы (в произвольном формате) |
| `schedule_to` | `today` \| `tomorrow` | На сегодня или завтра |

```bash
curl "http://localhost:8000/schedule/group?group_number=ЖБИ-31&schedule_to=today"
```

#### `GET /schedule/cabinet`

Расписание для кабинета.

| Параметр | Тип | Описание |
|---|---|---|
| `cabinet_number` | `string` | Номер кабинета (в произвольном формате) |
| `schedule_to` | `today` \| `tomorrow` | На сегодня или завтра |

```bash
curl "http://localhost:8000/schedule/cabinet?cabinet_number=52к&schedule_to=tomorrow"
```

### Группы

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/groups/` | Список всех групп |
| `GET` | `/groups/{group_number}` | Информация о конкретной группе |

### Кабинеты

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/cabinets/` | Список всех кабинетов |
| `GET` | `/cabinets/{cabinet_number}` | Информация о конкретном кабинете |

---

## Тестирование

В каждом сервисе есть полный набор тестов, покрывающий слои `domain`, `infrastructure` и `presentation`.

```bash
# Из директории нужного сервиса
cd services/service_api   # или service_bot / service_parser

# Запуск всех тестов
poetry run pytest

# С отчётом о покрытии
poetry run pytest --cov

# Запуск конкретного слоя
poetry run pytest tests/domain/
poetry run pytest tests/infrastructure/
poetry run pytest tests/presentation/
```

Для интеграционных тестов репозиториев используются **testcontainers** — PostgreSQL и Redis поднимаются автоматически в Docker-контейнерах.

---

## Структура проекта

```
VSTKScheduleSystem/
├── libs/
│   └── schedule_db_models/      # Общая библиотека ORM-моделей (переиспользуется всеми сервисами)
├── schedule_alembic/            # Миграции Alembic (общая схема БД)
├── schedule_alembic.ini
└── services/
    ├── service_parser/          # Микросервис: парсер расписания
    │   ├── src/service_parser/
    │   │   ├── domain/          # Доменные сущности и исключения
    │   │   ├── application/     # Порты (интерфейсы) и use cases
    │   │   └── infrastructure/  # Клиенты, репозитории, конфигурация, DI
    │   └── tests/
    ├── service_api/             # Микросервис: REST API
    │   ├── src/service_api/
    │   │   ├── domain/
    │   │   ├── application/
    │   │   ├── infrastructure/
    │   │   └── presentation/    # FastAPI-роутеры
    │   └── tests/
    └── service_bot/             # Микросервис: Telegram-бот
        ├── src/service_bot/
        │   ├── domain/
        │   ├── application/
        │   ├── infrastructure/
        │   └── presentation/    # Aiogram-хэндлеры
        ├── templates/           # Jinja2-шаблоны сообщений и клавиатур
        └── tests/
```

---

## Автор

**Никита Бондарев** — [nikitabondarevvitebsk@gmail.com](mailto:nikitabondarevvitebsk@gmail.com)

---

*Проект не имеет лицензии — все права защищены автором.*
