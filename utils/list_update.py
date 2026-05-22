#!/usr/bin/env python3

from datetime import timedelta, datetime
import json
import re
import requests
from requests.adapters import HTTPAdapter
from urllib.parse import quote

# 文件路径定义
# sub_list_json = './sub/sub_list.json'

def url_updated(url):  # 判断远程远程链接是否 уже обновлена
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    try:
        resp = s.get(url, timeout=4)
        status = resp.status_code
    except Exception:
        status = 404
    return status == 200


class update_url():

    def update_main(use_airport=False, airports_id: [] = [5], sub_list_json='./sub/sub_list.json'):
        try:
            with open(sub_list_json, 'r', encoding='utf-8') as f:  # Загружаем список подписок
                raw_list = json.load(f)
        except Exception as e:
            print(f"Ошибка чтения {sub_list_json}: {e}")
            return

        for sub in raw_list:
            sub_modified = False
            id = sub.get('id')
            current_url = sub.get('url', '')

            try:
                if not use_airport:
                    if id not in airports_id and sub.get('update_method') != 'update_airports':
                        if sub.get('update_method') != 'auto' and sub.get('enabled', False):
                            print(f'Поиск обновлений для ID {id}')
                            if sub.get('update_method') == 'change_date':
                                new_url = update_url.change_date(id, current_url)
                                if new_url == current_url:
                                    print(f'Обновлений для ID {id} не найдено\n')
                                else:
                                    sub['url'] = new_url
                                    sub_modified = True
                                    print(f'ID {id} обновлен: {new_url}\n')
                            elif sub.get('update_method') == 'page_release':
                                new_url = update_url.find_link(id, current_url)
                                if new_url == current_url:
                                    print(f'Обновлений для ID {id} не найдено\n')
                                else:
                                    sub['url'] = new_url
                                    sub_modified = True
                                    print(f'ID {id} обновлен: {new_url}\n')
                            elif sub.get('update_method') == 'update_airports':
                                new_url = update_url.update_airports(id, current_url)
                                if new_url == current_url:
                                    print(f'Обновлений для ID {id} не найдено\n')
                                else:
                                    sub['url'] = new_url
                                    sub_modified = True
                                    print(f'ID {id} обновлен: {new_url}\n')
                else:
                    if id in airports_id:
                        if sub.get('update_method') != 'auto' and sub.get('enabled', False):
                            print(f'Поиск обновлений для ID {id}')
                            if sub.get('update_method') == 'change_date':
                                new_url = update_url.change_date(id, current_url)
                                if new_url == current_url:
                                    print(f'Обновлений для ID {id} не найдено\n')
                                else:
                                    sub['url'] = new_url
                                    sub_modified = True
                                    print(f'ID {id} обновлен: {new_url}\n')
                            elif sub.get('update_method') == 'page_release':
                                new_url = update_url.find_link(id, current_url)
                                if new_url == current_url:
                                    print(f'Обновлений для ID {id} не найдено\n')
                                else:
                                    sub['url'] = new_url
                                    sub_modified = True
                                    print(f'ID {id} обновлен: {new_url}\n')
                            elif sub.get('update_method') == 'update_airports':
                                new_url = update_url.update_airports(id, current_url)
                                if new_url == current_url:
                                    print(f'Обновлений для ID {id} не найдено\n')
                                else:
                                    sub['url'] = new_url
                                    sub_modified = True
                                    print(f'ID {id} обновлен: {new_url}\n')
            except KeyError:
                print(f'ID {id}: метод обновления не задан, ссылка не изменена\n')

            if sub_modified:
                updated_list = json.dumps(raw_list, sort_keys=False, indent=2, ensure_ascii=False)
                try:
                    with open(sub_list_json, 'w', encoding='utf-8') as file:
                        file.write(updated_list)
                except Exception as e:
                    print(f"Ошибка записи {sub_list_json}: {e}")

    def update_airports(id, current_url):
        new_url = current_url
        if id == 5:
            try:
                s = requests.Session()
                s.mount('http://', HTTPAdapter(max_retries=2))
                s.mount('https://', HTTPAdapter(max_retries=2))

                urllist = []
                for url in [
                    'https://raw.githubusercontent.com/RenaLio/Mux2sub/main/urllist',
                    'https://raw.githubusercontent.com/RenaLio/Mux2sub/main/sub_list',
                    'https://raw.githubusercontent.com/rxsweet/getAirport/main/config/sublist_free',
                    'https://raw.githubusercontent.com/rxsweet/getAirport/main/config/sublist_mining'
                ]:
                    try:
                        resp = s.get(url, timeout=4)
                        if resp.status_code == 200:
                            lines = resp.text.split("\n")
                            valid = list(filter(lambda x: x.strip() and x.strip().startswith("http"), lines))
                            urllist.extend(valid)
                    except Exception as e:
                        print(f"Ошибка получения {url}: {e}")

                if urllist:
                    new_url = "|".join(list(set(urllist)))
            except Exception as e:
                print(f"Ошибка в update_airports: {e}")
        return new_url

    def change_date(id, current_url):
        new_url = current_url
        try:
            if id == 0:
                today = datetime.today().strftime('%m%d')
                new_url = f'https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/{today}.txt'
            elif id == 1:
                today = datetime.today().strftime('%Y%m%d')
                this_year = datetime.today().strftime('%Y')
                this_month = datetime.today().strftime('%m')
                new_url = f'https://nodefree.org/dy/{this_year}/{this_month}/{today}.yaml'
            elif id == 3:
                today = datetime.today().strftime('%Y%m%d')
                this_month = datetime.today().strftime('%m')
                this_year = datetime.today().strftime('%Y')
                new_url = f'https://v2rayshare.com/wp-content/uploads/{this_year}/{this_month}/{today}.txt'
            elif id == 4:
                today = datetime.today().strftime('%Y%m%d')
                this_month = datetime.today().strftime('%m')
                this_year = datetime.today().strftime('%Y')
                new_url = f'https://clashnode.com/wp-content/uploads/{this_year}/{this_month}/{today}.txt'

            if url_updated(new_url):
                return new_url
        except Exception as e:
            print(f"Ошибка в change_date для ID {id}: {e}")
        return current_url

    def find_link(id, current_url):
        if id == 2:
            try:
                res = requests.get('https://api.github.com/repos/mianfeifq/share/contents/', timeout=4)
                if res.status_code == 200:
                    res_json = res.json()
                    for file in res_json:
                        if file.get('name', '').startswith('data'):
                            return file.get('download_url', current_url)
            except Exception as e:
                print(f"Ошибка в find_link для ID {id}: {e}")
        return current_url


if __name__ == '__main__':
    update_url.update_main()
