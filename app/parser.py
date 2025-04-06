import re

def parse_transactions(text: str, source_hint: str = None, pdf_path: str = None):
    if source_hint is None:
        source_hint = detect_bank_source(text)

    if source_hint == "kaspi":
        return parse_kaspi(text, source_hint)
    elif source_hint == "halyk":
        return parse_halyk(text, source_hint)
    print(f"[DEBUG] Источник: {source_hint}")
    print(f"[DEBUG] Длина текста: {len(text.splitlines())} строк")

    return []

def detect_bank_source(text: str):
    lower_text = text.lower()
    if "kaspi" in lower_text:
        return "kaspi"
    elif "halyk" in lower_text or "халык" in lower_text:
        return "halyk"
    else:
        return "unknown"

def parse_kaspi(text: str, source: str):
    # Пример строки: 04.04.25 - 2 100,00 ₸ Purchases OtbasyBank
    pattern = r"(\d{2}\.\d{2}\.\d{2})\s+([+-]?\s*\d[\d\s]*,[\d]{2})\s+₸\s+(Purchases|Replenishment|Transfers|Withdrawals|Others)\s+(.+)"
    matches = re.findall(pattern, text)
    transactions = []

    for date, raw_amount, operation, details in matches:
        clean_amount = raw_amount.replace(" ", "").replace(",", ".").replace("+", "").replace("−", "-")

        try:
            amount = float(clean_amount)
        except ValueError:
            continue

        tx_type = "доход" if operation == "Replenishment" else "расход"

        transactions.append({
            "date": date,
            "description": f"{operation} {details.strip()}",
            "amount": round(abs(amount), 2),
            "type": tx_type,
            "source": source,
        })

    return transactions

def parse_halyk(text: str, source_hint: str = "halyk") -> list[dict]:
    import re

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    transactions = []

    pattern = re.compile(r"(?P<date>\d{2}\.\d{2}\.\d{4})\s+(?P<desc>.+?)\s+(-?\d[\d\s]*,[\d]{2})\s+KZT")
    i = 0

    while i < len(lines):
        match = pattern.search(lines[i])
        if match:
            date = match.group("date")
            description = match.group("desc")
            amount_str = match.group(3).replace(" ", "").replace(",", ".")

            try:
                amount = float(amount_str)
            except ValueError:
                i += 1
                continue

            tx_type = "доход" if amount > 0 else "расход"

            transactions.append({
                "date": date,
                "description": description.strip(),
                "amount": round(abs(amount), 2),
                "type": tx_type,
                "source": source_hint
            })

        else:
            # 👇 Попытка найти двухстрочную транзакцию
            if i + 1 < len(lines) and re.match(r"^-?\d[\d\s]*,[\d]{2}$", lines[i + 1]):
                date_match = re.match(r"(\d{2}\.\d{2}\.\d{4})", lines[i])
                if date_match:
                    date = date_match.group(1)
                    description = lines[i][len(date):].strip()
                    amount_str = lines[i + 1].replace(" ", "").replace(",", ".").replace("−", "-")
                    try:
                        amount = float(amount_str)
                        tx_type = "доход" if amount > 0 else "расход"
                        transactions.append({
                            "date": date,
                            "description": description.strip(),
                            "amount": round(abs(amount), 2),
                            "type": tx_type,
                            "source": source_hint
                        })
                        i += 2
                        continue
                    except ValueError:
                        pass
        i += 1

    print(f"[DEBUG] Найдено {len(transactions)} транзакций ({source_hint})")
    return transactions