Telegram Finance Bot

Overview
This project is a Telegram bot that parses bank PDF statements (Kaspi and Halyk), extracts transactions, and generates a summary in Excel format. Users can also request GPT-powered analysis of their financial data.

Features
- Upload PDF statements via Telegram
- Extract and merge transactions from multiple banks
- Generate a summary Excel file
- Ask GPT for insights and recommendations
- Full support for Docker deployment
- Ready for PostgreSQL integration in future

Project Structure
- app/
    - ai_analysis.py         - GPT integration
    - bot.py                 - Telegram bot logic
    - main.py                - FastAPI entrypoint for Docker
    - parser.py              - Transaction parsing logic
    - utils/
        - excel_exporter.py  - Save transactions to Excel
        - freedom_excel_parser.py - OCR + Excel parser for Freedom Bank (if needed)
- temp/                      - Temporary files (mounted in Docker)
- pyproject.toml            - Poetry configuration
- Dockerfile                - Docker image definition
- .env                      - Environment variables (not committed)
- .dockerignore             - Docker ignore rules
- .gitignore                - Git ignore rules

Setup
1. Clone the repository:
   git clone git@github.com:ZharasAT/telegram-finbot.git

2. Create a virtual environment and install dependencies:
   poetry install

3. Create a `.env` file with your Telegram and OpenAI keys:
   TELEGRAM_TOKEN=your-telegram-token
   OPENAI_API_KEY=your-openai-api-key

Run Locally
poetry run uvicorn app.main:app --reload

Docker Deployment
Build the image:
docker build -t finance-bot .

Run the container:
docker run -it --rm \
  -v "$(pwd)/temp:/app/temp" \
  --env-file .env \
  -p 8000:8000 \
  finance-bot poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

Planned Enhancements
- PostgreSQL storage for transactions
- Analytics dashboard
- Multi-language support
- Integration with bank APIs (Kaspi, Halyk, Freedom)

Author
Zharas Tuyanov