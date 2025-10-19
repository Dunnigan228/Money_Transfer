# Money Transfer Service

**[English](#english) | [Русский](#russian)**

---

<a name="english"></a>
## EN English

### What is this?

REST API for money transfers between accounts with automatic currency conversion.

### Tech Stack

- FastAPI + PostgreSQL
- RabbitMQ for async tasks
- Redis for caching
- Docker

### Quick Start

1. **Clone repo:**
```bash
git clone https://github.com/Dunnigan228/Money_Transfer.git
cd teh_zadanie
```

2. **Copy environment file:**
```bash
cp .env.example .env
```

3. **Run with Docker:**
```bash
docker-compose up -d
```

4. **Done!** API runs on http://localhost:8000

### API Docs

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### How it works

The system has:
- **API** - handles requests
- **Workers** - process transfers in background
- **PostgreSQL** - stores data
- **RabbitMQ** - task queue
- **Redis** - cache for exchange rates

When you create a transfer, API saves it to database and sends task to worker. Worker processes it asynchronously.

---

<a name="russian"></a>
## RU Русский

### Что это?

REST API для денежных переводов между счетами с автоматической конвертацией валют.

### Технологии

- FastAPI + PostgreSQL
- RabbitMQ для асинхронных задач
- Redis для кеширования
- Docker

### Быстрый запуск

1. **Склонировать репозиторий:**
```bash
git clone https://github.com/Dunnigan228/Money_Transfer.git
cd teh_zadanie
```

2. **Скопировать файл окружения:**
```bash
cp .env.example .env
```

3. **Запустить через Docker:**
```bash
docker-compose up -d
```

4. **Готово!** API доступен на http://localhost:8000

### Документация API

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Как это работает

В системе есть:
- **API** - принимает запросы
- **Worker'ы** - обрабатывают переводы в фоне
- **PostgreSQL** - хранит данные
- **RabbitMQ** - очередь задач
- **Redis** - кеш для курсов валют

Когда создаешь перевод, API сохраняет его в базу и отправляет задачу worker'у. Worker обрабатывает асинхронно.
