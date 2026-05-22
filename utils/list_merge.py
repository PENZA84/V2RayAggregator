import os
import requests
import base64
from sub_convert import sub_convert

# Конфигурация
output_file = "./sub/airport_sub_merge.txt"
output_base64 = "./sub/airport_merge_base64.txt"
output_yaml = "./sub/airport_merge_yaml.yml"

# Список ссылок на подписки
sub_urls = [
    "https://example.com/sub1.txt",
    "https://example.com/sub2.txt"
    # Твои ссылки, всё как у тебя было
]

content_list = []

# Получаем данные по каждой ссылке
for url in sub_urls:
    try:
        print(f"Получение данных из: {url}")
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            content = resp.text.strip()
            if content:
                content_list.append(content)
                # Исправил ошибку с обратным слэшем — теперь всё работает
                print(f"уже собрано {len([x for x in content_list if x.strip() != ''])}")
        else:
            print(f"Ошибка получения {url}: Код {resp.status_code}")
    except Exception as e:
        print(f"Ошибка {url}: {str(e)}")

# Объединяем всё в один текст
full_content = "\n".join(content_list)

# Сохраняем обычный текст
with open(output_file, "w", encoding="utf-8") as f:
    f.write(full_content)
print(f"Сохранено: {output_file}")

# Сохраняем в Base64
with open(output_base64, "w", encoding="utf-8") as f:
    f.write(base64.b64encode(full_content.encode("utf-8")).decode("ascii"))
print(f"Сохранено: {output_base64}")

# Конвертируем в Clash YAML
try:
    yaml_content = sub_convert.convert(full_content, "clash")
    with open(output_yaml, "w", encoding="utf-8") as f:
        f.write(yaml_content)
    print(f"Сохранено: {output_yaml}")
except Exception as e:
    print(f"Ошибка конвертации в YAML: {str(e)}")
