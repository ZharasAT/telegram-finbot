from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analyze_transactions_with_gpt(transactions):
    prompt = "Вот список транзакций:\n\n"
    for t in transactions:
        prompt += f"{t['date']} | {t['amount']} | {t['description']}\n"

    prompt += "\nПроанализируй данные: какие категории трат ты видишь? Какие советы можешь дать для улучшения финансового поведения?"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты финансовый помощник. Проанализируй транзакции и предложи улучшения."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
