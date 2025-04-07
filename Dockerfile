# Базовый образ Python
FROM python:3.12-slim

# Устанавливаем Poetry
RUN pip install poetry

# Создаём рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Установка зависимостей без создания виртуального окружения
RUN poetry config virtualenvs.create false && poetry install --only main --no-root

# Копируем оставшийся код проекта
COPY . .

# Создаём папку для временных файлов (если не существует)
RUN mkdir -p temp

# Указываем порт (Render сам выберет)
EXPOSE 8000

# Запуск FastAPI приложения с webhook
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]