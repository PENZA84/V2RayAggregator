import re
import yaml
import json
import time
import os

from sub_convert import sub_convert
from subs_function import subs_function
from list_merge_airport import sub_merge

Eterniy_file = './EternityAir'
Eternity_yml_file = './EternityAir.yml'
log_file = './LogInfoAir.txt'

provider_path = './update/provider/'
update_path = './update/'

sub_list_json = './sub/sub_list.json'

config_file = './update/provider/config.yml'
config_global_file = './update/provider/config-global.yml'


# Отключение псевдонимов в YAML — как указал автор
class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def substrings(string, left, right):
    value = string.replace('\n', '').replace(' ', '')
    start = value.index(left)
    end = value[start:].index(right) + (len(value) - len(value[start:]))
    final_value = value[start:end].replace(left, '')
    return final_value


def eternity_convert(file, config, output, provider_file_enabled=True):
    # Получение списка узлов для airport — без изменений
    all_provider = subs_function.convert_sub(
        "https://raw.githubusercontent.com/mahdibland/SSAggregator/master/sub/airport_merge_base64.txt",
        'clash',
        "http://0.0.0.0:25500",
        False,
        extra_options="&udp=false"
    )

    # Добавление информации в логи — строго как в оригинале
    temp_providers = all_provider.split('\n')
    try:
        with open(log_file, 'r', encoding='utf-8') as log_reader:
            log_lines = log_reader.readlines()
    except:
        log_lines = []

    indexx = 0
    for line in temp_providers:
        if line != 'proxies:':
            try:
                server_name = substrings(line, "name:", ",")
                server_type = substrings(line, "type:", ",")
                if indexx < len(log_lines):
                    log_lines[indexx] = f"name: {server_name} | type: {server_type} | {log_lines[indexx]}"
                indexx += 1
            except:
                print("Несовпадение длины логов и списка узлов")

    with open(log_file, 'w', encoding='utf-8') as log_writer:
        log_writer.writelines(log_lines)


    # Удаление строк с битым символом
    removed_bad_char = list(filter(lambda x: "�" not in x, all_provider.split("\n")[1:]))
    log_lines_without_bad_char = list(filter(lambda x: "�" not in x, log_lines))

    print(f"Узлов после очистки: {len(removed_bad_char)} | Строк логов: {len(log_lines_without_bad_char)}")

    # Ограничение до 200 узлов — как задумано
    num = 200
    if len(removed_bad_char) < num:
        num = len(removed_bad_char)

    # Удаление узлов с нулевой скоростью — логика автора сохранена
    removed_bad_char_without_zero = []
    for index, item in enumerate(removed_bad_char[:num + 1]):
        if index < len(log_lines_without_bad_char) and "avg_speed: 0.0 MB" not in log_lines_without_bad_char[index]:
            removed_bad_char_without_zero.append(item)

    all_provider = "proxies:\n" + "\n".join(removed_bad_char_without_zero)

    lines = re.split(r'\n+', all_provider)

    proxy_all = []
    indexx = 0
    for line in lines:
        if line != 'proxies:':
            try:
                name = substrings(line, "name:", ",")
                speed = ""
                if indexx < len(log_lines_without_bad_char):
                    speed_raw = substrings(log_lines_without_bad_char[indexx], "avg_speed:", "|")
                    if speed_raw:
                        speed = speed_raw
                if speed:
                    line = re.sub(r"name:\s*(.*?),", f"name: {name} | {speed},", line)
            except:
                if indexx < len(log_lines_without_bad_char):
                    print(log_lines_without_bad_char[indexx])
                pass

            line = line.replace('- ', '').strip()
            if not line:
                indexx += 1
                continue

            try:
                linee = yaml.safe_load(line)
                proxy_all.append(linee)
            except:
                pass

            indexx += 1


    # Сохранение провайдера для airport — как в оригинале
    if provider_file_enabled:
        providers_files = {'all': provider_path + 'provider-all-airport.yml'}
        eternity_providers = {'all': all_provider}

        print("Запись файлов провайдеров...")
        for key in providers_files.keys():
            with open(providers_files[key], 'w', encoding='utf-8') as f:
                f.write(eternity_providers[key])
        print("Готово!\n")


    # Чтение основного конфига
    with open(config, 'r', encoding='utf-8') as f:
        config_raw = f.read()
    config = yaml.safe_load(config_raw)

    all_provider_dic = {'proxies': []}
    provider_dic = {'all': all_provider_dic}

    for key in eternity_providers.keys():
        provider_load = yaml.safe_load(eternity_providers[key])
        if provider_load:
            provider_dic[key].update(provider_load)


    # Формирование списка имён
    all_name = []
    name_dict = {'all': all_name}
    indexx = 0

    for key in provider_dic.keys():
        if provider_dic[key].get('proxies'):
            for proxy in provider_dic[key]['proxies']:
                try:
                    speed = ""
                    if indexx < len(log_lines_without_bad_char):
                        speed = substrings(log_lines_without_bad_char[indexx], "avg_speed:", "|")
                    name_entry = str(proxy['name']).replace(" ", "")
                    if speed:
                        name_entry += f" | {speed}"
                    name_dict[key].append(name_entry)
                except:
                    name_dict[key].append(str(proxy.get('name', 'Unknown')).replace(" ", ""))
                    if indexx < len(log_lines_without_bad_char):
                        print(log_lines_without_bad_char[indexx])
                indexx += 1
        else:
            name_dict[key].append('DIRECT')


    # Заполнение групп по Tier — строго как в авторском коде
    proxy_groups = config.get('proxy-groups', [])
    proxy_group_fill = [rule['name'] for rule in proxy_groups if rule.get('proxies') is None]

    full_size = len(all_name)
    part_size = int(full_size / 4) if full_size > 0 else 0

    for rule_name in proxy_group_fill:
        for rule in proxy_groups:
            if rule['name'] == rule_name:
                if "Tier 1" in rule_name and part_size > 0:
                    rule['proxies'] = all_name[:part_size]
                elif "Tier 2" in rule_name and part_size > 0:
                    rule['proxies'] = all_name[part_size:part_size*2]
                elif "Tier 3" in rule_name and part_size > 0:
                    rule['proxies'] = all_name[part_size*2:part_size*3]
                elif "Tier 4" in rule_name and part_size > 0:
                    rule['proxies'] = all_name[part_size*3:full_size]


    # Обновление конфига
    config.update(all_provider_dic)
    config['proxy-groups'] = proxy_groups
    config['proxies'] = proxy_all


    # Сохранение готового файла
    config_yaml = yaml.dump(
        config,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=750,
        indent=2,
        Dumper=NoAliasDumper
    )

    with open(output, 'w+', encoding='utf-8') as f:
        f.write(config_yaml)


if __name__ == '__main__':
    sub_merge.geoip_update('https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb')
    eternity_convert(Eterniy_file, config_file, output=Eternity_yml_file)
