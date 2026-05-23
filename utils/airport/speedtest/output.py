import json
import base64
import os
import time

out_json = './output.json'

Eternity_Air = "./EternityAir"
airport_all_base64 = "./sub/airport_merge_base64.txt"
sub_all = "./sub/airport_sub_merge.txt"
Eternity_Air_file = "./EternityAir.txt"


def read_json(file):  
    # Твоя железная логика: если файла нет — создаем пустой шаблон на месте, чтобы не было 6-часового цикла
    if not os.path.isfile(file):
        print(f"⚠️ Файла {file} нет. Создаем пустой шаблон для предотвращения зависания.")
        default_data = {"nodes": []}
        with open(file, 'w', encoding='utf-8') as tmp_f:
            json.dump(default_data, tmp_f)
            
    with open(file, 'r', encoding='utf-8') as f:
        print('Reading output.json')
        try:
            data = json.load(f)
            if data and "nodes" in data:
                proxies_all = data["nodes"]
            else:
                proxies_all = []
        except Exception as e:
            print(f"Ошибка чтения JSON: {e}. Пул пуст.")
            proxies_all = []
    return proxies_all


def output(list, num):
    # Гарантируем, что папка sub существует
    os.makedirs("./sub", exist_ok=True)

    # Если результатов нет — просто пишем пустые документы (перезаписываем старые)
    if not list:
        print("📊 Список пуст. Просто перезаписываем документы пустыми значениями.")
        for path in [sub_all, airport_all_base64, Eternity_Air, Eternity_Air_file, './LogInfoAir.txt']:
            with open(path, 'w', encoding='utf-8') as dummy_f:
                dummy_f.write("")
        return ""

    # Если данные есть — сортируем по средней скорости и перезаписываем всё сверху
    list = sorted(list, key=lambda x: x['avg_speed'], reverse=True)

    def arred(x, n): return x*(10**n)//1/(10**n)
    print("Top Proxy: " + str(list[0]))
    
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

    # Чистое обновление файлов поверх существующего контента
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
    
    # Мы УБРАЛИ os.unlink отсюда! Теперь файл, созданный твоим тестом скорости, НЕ удаляется!
    value = read_json(out_json)
    
    # Перезаписываем все текстовые документы поверх старых
    output(value, len(value) if len(value) <= num else num)
    print('🔄 Файлы успешно перезаписаны новыми результатами теста!')
