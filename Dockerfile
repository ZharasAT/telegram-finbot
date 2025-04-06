# Используем лёгкий Python-образ
FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-rus \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем poetry
RUN pip install poetry

# Указываем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости без установки проекта
RUN poetry config virtualenvs.create false && poetry install --only main --no-root

# Копируем всё остальное
COPY . .

# Запускаем бота
CMD ["poetry", "run", "python", "-m", "app.main"]