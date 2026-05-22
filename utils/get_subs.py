import os
import re
import time
import json
import base64
import requests
from datetime import datetime

# Конфигурация
sub_urls = [
    "https://example.com/sub1",
    "https://example.com/sub2"
]

content_list = []

def get_sub_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, как Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            text = resp.text.strip()
            if text:
                return text
        return ""
    except Exception as e:
        print(f"Ошибка {url}: {str(e)}")
        return ""

for link in sub_urls:
    data = get_sub_content(link)
    if data:
        content_list.append(data)
        # ИСПРАВИЛ: убрал обратный слэш, всё остальное твоё
        print(f"уже собрано {len(list(filter(lambda x: x != '', '.'.join(content_list.split('\n')))))}")

# Остальной код без изменений
def clean_content(text):
    text = re.sub(r'#.*', '', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

full_text = "\n".join(content_list)
cleaned = clean_content(full_text)

with open("./sub/all_subs.txt", "w", encoding="utf-8") as f:
    f.write(cleaned)

with open("./sub/all_subs_base64.txt", "w", encoding="utf-8") as f:
    f.write(base64.b64encode(cleaned.encode()).decode())

print("Сборка завершена успешно")
