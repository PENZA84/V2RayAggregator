import json
import base64
import os
import time

# Определяем путь к файлу в той же папке, где лежит сам скрипт
current_dir = os.path.dirname(os.path.abspath(__file__))
out_json = os.path.join(current_dir, 'output.json')

Eternity_Air = "./EternityAir"
airport_all_base64 = "./sub/airport_merge_base64.txt"
sub_all = "./sub/airport_sub_merge.txt"
Eternity_Air_file = "./EternityAir.txt"


def read_json(file):  
    # Твоя железная логика: если файла нет, создаем пустой шаблон и пишем туда, чтобы не было зависаний
    if not os.path.isfile(file):
        print(f"⚠️ Файла {file} не найдено. Создаем чистый output.json в рабочей папке.")
        default_data = {"nodes": []}
        with open(file, 'w', encoding='utf-8') as tmp_f:
            json.dump(default_data, tmp_f, ensure_ascii=False, indent=4)
            
    with open(file, 'r', encoding='utf-8') as f:
        print(f'Reading {file}...')
        try:
            data = json.load(f)
            if data and "nodes" in data:
                proxies_all = data["nodes"]
            else:
                proxies_all = []
        except Exception as e:
            print(f"Ошибка чтения JSON: {e}. Используем пустой пул.")
            proxies_all = []
    return proxies_all


def output(list, num):
    # Гарантируем, что папка для сохранения подписок sub существует
    os.makedirs("./sub", exist_ok=True)

    # Если результатов нет — просто обновляем все документы пустыми значениями поверх старых
    if not list:
        print("📊 Спидтест пуст. Просто перезаписываем документы чистыми значениями.")
        for path in [sub_all, airport_all_base64, Eternity_Air, Eternity_Air_file, './LogInfoAir.txt']:
            with open(path, 'w', encoding='utf-8') as dummy_f:
                dummy_f.write("")
        return ""

    # Если данные есть — сортируем по средней скорости и жестко переписываем файлы сверху
    list = sorted(list, key=lambda x: x['avg_speed'], reverse=True)

    def arred(x, n): return x*(10**n)//1/(10**n)
    print("🚀 Лучший прокси из output.json: " + str(list[0]))
    
    output_list = []
    for item in list:
        info = "id: %s | remarks: %s | protocol: %s | ping: %s MS | avg_speed: %s MB | max_speed: %s MB | Link: %s\n" % (
            str(item["id"]), item["remarks"], item["protocol"], 
            str(item["ping"]), str(arred(item["avg_speed"] * 0.00000095367432, 3)), 
            str(arred(item["max_speed"] * 0.00000095367432, 3)), item["link"]
        )
        output_list.append(info)

    with open('./LogInfoAir.txt', 'w', encoding='utf-8') as f1:
        f1.writelines(output_list)
        print('Write Log Success!')

    output_list = []
    for index in range(len(list)):
        proxy = list[index]['link']
        output_list.append(proxy)

    content = '\n'.join(output_list)
    content_base64 = base64.b64encode('\n'.join(output_list).encode('utf-8')).decode('ascii')
    content_base64_part = base64.b64encode('\n'.join(output_list[0:num]).encode('utf-8')).decode('ascii')

    # Прямая перезапись документов без лишних вопросов
    with open(sub_all, 'w', encoding='utf-8') as f:
        f.write(content)
        print('Write All Urls Success!')
        
    with open(airport_all_base64, 'w+', encoding='utf-8') as f:
        f.write(content_base64)
        print('Write All Base64 Success!')
        
    with open(Eternity_Air, 'w+', encoding='utf-8') as f:
        f.write(content_base64_part)
        print('Write Part Base64 Success!')

    with open(Eternity_Air_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_list[0:num]))
        print('Write Part Base Success!')

    return content


if __name__ == '__main__':
    num = 200
    
    # 1. Читаем из папки скрипта (если файла нет — он автоматически создается и записывается)
    value = read_json(out_json)
    
    # 2. Перезаписываем все текстовые базы и логи поверх старых
    output(value, len(value) if len(value) <= num else num)
    print('🔄 Все файлы на Поставщике успешно перезаписаны. Ротация завершена!')
