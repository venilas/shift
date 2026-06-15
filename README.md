# Локальный запуск

## 1. Клонирование репозитория

```bash
git clone https://github.com/venilas/shift.git
cd shift

```

## 2. Установка зависимостей
```bash
make install
```

или

```bash
poetry install
```

## 3. Настройка переменных окружения

Создайте файл `.env` из шаблона:

```bash
cp .env.example .env
```

Для локального запуска значение переменной должно быть следующим:

```env
POSTGRES_HOST=localhost
```

## 4. Запуск PostgreSQL

Перед запуском приложения необходимо поднять контейнер с базой данных:

```bash
docker compose up -d database
```

## 5. Применение миграций
```bash
make upgrade
```

## 6. Запуск приложения
```bash
poetry run uvicorn src.main:app --reload --env-file .env
```

После запуска приложение будет доступно по адресу:

```
http://localhost:8000
```

Документация API:
- Swagger: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

---

# Запуск через Docker

## 1. Настройка переменных окружения

Создайте файл `.env` из шаблона:

```bash
cp .env.example .env
```

Для Docker значение переменной должно быть следующим:

```env
POSTGRES_HOST=database
```

## 2. Сборка и запуск контейнеров

```bash
make docker-up
```

После запуска сервис будет доступен по адресу:

```
http://localhost:8000
```


## 3. Остановка контейнеров

```bash
make docker-down
```

---

# Работа с миграциями

## Создание миграции

```bash
make migrate msg="create bookings table"
```

## Применение миграции

```bash
make upgrade
```

## Откат последней миграции

```bash
make downgrade
```

---

# Тестирование

## Запуск тестов

```bash
make test
```

## Проверка качества кода

```bash
make lint
```

## Автоматическое форматирование

```bash
make format
```
