import json
import base64
import os
import time

# 📌 Пути — точно как у тебя настроено
out_json = './out.json'

sub_all_base64 = "./sub/sub_merge_base64.txt"
sub_all = "./sub/sub_merge.txt"
Eternity_file_base64 = "./Eternity"
Eternity_file = "./Eternity.txt"
Eternity_Base = "./EternityBase"

splitted_output = "./sub/splitted/"


def read_json(file):
    """Чтение файла результатов теста — ждём пока появится, если ещё идёт проверка"""
    while not os.path.isfile(file):
        print('⏳ Ожидаю завершения теста скорости...')
        time.sleep(30)
    with open(file, 'r', encoding='utf-8') as f:
        print('📖 Читаю результат: out.json')
        proxies_all = json.load(f)["nodes"]
        f.close()
    return proxies_all


def output(proxy_list, num):
    """Обработка, сортировка, разделение по протоколам и сохранение во все файлы"""
    # Сортируем по СРЕДНЕЙ скорости (как у тебя было, а не по максимальной)
    proxy_list = sorted(proxy_list, key=lambda x: x['avg_speed'], reverse=True)

    # Логи для контроля
    print("🔝 Лучший узел:", proxy_list[0])
    print("🔚 Последний узел:", proxy_list[-1])

    # Вспомогательная функция для округления
    def arred(x, n): return x * (10 ** n) // 1 / (10 ** n)

    # 📝 Формируем лог с полной информацией по каждому узлу
    log_lines = []
    for item in proxy_list:
        info = (
            f"id: {item['id']} | "
            f"метка: {item['remarks']} | "
            f"протокол: {item['protocol']} | "
            f"задержка: {item['ping']} мс | "
            f"средняя скорость: {arred(item['avg_speed'] * 0.00000095367432, 3)} МБ/с | "
            f"макс скорость: {arred(item['max_speed'] * 0.00000095367432, 3)} МБ/с | "
            f"ссылка: {item['link']}\n"
        )
        log_lines.append(info)

    with open('./LogInfo.txt', 'w', encoding='utf-8') as f1:
        f1.writelines(log_lines)
        print('✅ Лог информации сохранён: LogInfo.txt')

    # 📋 Вытаскиваем только ссылки на подключение
    link_list = [item['link'] for item in proxy_list]

    # Кодируем в Base64 (всё и часть топовых)
    content_all = '\n'.join(link_list)
    content_all_b64 = base64.b64encode(content_all.encode('utf-8')).decode('ascii')
    content_part = '\n'.join(link_list[:num])
    content_part_b64 = base64.b64encode(content_part.encode('utf-8')).decode('ascii')

    # 📂 Разделяем узлы по протоколам в отдельные файлы
    os.makedirs(splitted_output, exist_ok=True)
    vmess = []
    trojan = []
    ssr = []
    ss = []

    for link in link_list:
        if link.startswith("vmess://"):
            vmess.append(link)
        elif link.startswith("trojan://"):
            trojan.append(link)
        elif link.startswith("ssr://"):
            ssr.append(link)
        elif link.startswith("ss://"):
            ss.append(link)

    with open(os.path.join(splitted_output, "vmess.txt"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(vmess))
        print('✅ vmess.txt готов')

    with open(os.path.join(splitted_output, "trojan.txt"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(trojan))
        print('✅ trojan.txt готов')

    with open(os.path.join(splitted_output, "ssr.txt"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(ssr))
        print('✅ ssr.txt готов')

    with open(os.path.join(splitted_output, "ss.txt"), 'w', encoding='utf-8') as f:
        f.write('\n'.join(ss))
        print('✅ ss.txt готов')

    # 💾 Записываем во все основные файлы
    with open(sub_all_base64, 'w+', encoding='utf-8') as f:
        f.write(content_all_b64)
        print('✅ sub_merge_base64.txt обновлён')

    with open(Eternity_file_base64, 'w+', encoding='utf-8') as f:
        f.write(content_part_b64)
        print('✅ Eternity (Base64) готов')

    with open(sub_all, 'w', encoding='utf-8') as f:
        f.write(content_all)
        print('✅ sub_merge.txt обновлён')

    with open(Eternity_Base, 'w', encoding='utf-8') as f:
        f.write(content_all)
        print('✅ EternityBase готов')

    with open(Eternity_file, 'w', encoding='utf-8') as f:
        f.write(content_part)
        print('✅ Eternity.txt готов')

    return content_all


if __name__ == '__main__':
    num_top = 200  # Сколько лучших узлов оставляем в выборке
    proxies_data = read_json(out_json)
    take_num = num_top if len(proxies_data) > num_top else len(proxies_data)
    output(proxies_data, take_num)
