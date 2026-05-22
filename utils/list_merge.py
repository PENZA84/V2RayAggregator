#!/usr/bin/env python3

# Python 之间互相调用文件https://blog.csdn.net/winycg/article/details/78512300
from sub_convert import sub_convert
from list_update import update_url
from get_subs import subs

import json
import re
import os
import yaml
from urllib import request


# 分析当前项目依赖 https://blog.csdn.net/lovedingd/article/details/102522094


# 文件路径定义
Eterniy = './Eternity'
readme = './README.md'

sub_list_json = './sub/sub_list.json'
sub_merge_path = './sub/'
sub_list_path = './sub/list/'

ipv4 = r"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"
ipv6 = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'


def add_valid(line):
    if (line and ("ssr://" in line or "ss://" in line
            or "trojan://" in line or "vmess://" in line)):
        return line
    return ''


class sub_merge():
    def sub_merge(url_list):  # 将转换后的所有 Url 链接内容合并转换 YAML or Base64, ，并输出文件，输入订阅列表。

        content_list = []
        for t in os.walk(sub_list_path):
            for f in t[2]:
                os.remove(os.path.join(t[0], f))

        for (index, url_container) in enumerate(url_list):
            ids = url_list[index]['id']
            remarks = url_list[index]['remarks']
            if isinstance(url_container.get("url"), list):
                for each_url in url_container["url"]:
                    content = ''
                    print("gather server from " + each_url)
                    try:
                        content = sub_convert.convert_remote(each_url, 'url', 'http://127.0.0.1:25500')
                    except Exception as e:
                        print(f"convert_remote error: {e}")
                        content = 'Url 解析错误'

                    if content == 'Url 解析错误':
                        try:
                            content = sub_convert.main(each_url, 'url', 'url')
                        except Exception as e:
                            print(f"sub_convert.main error: {e}")
                            content = 'Url 解析错误'

                        if content != 'Url 解析错误':
                            if add_valid(content) != '':
                                content_list.append(content)
                            else:
                                print(f'this url failed {each_url}')
                            print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                        else:
                            print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')

                        try:
                            with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                file.write(content)
                        except Exception as e:
                            print(f"File write error: {e}")

                    elif content == 'Url 订阅内容无法解析':
                        try:
                            with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                file.write('Url Subscription could not be parsed')
                        except Exception as e:
                            print(f"File write error: {e}")
                        print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')

                    elif content is not None and content != '':
                        if add_valid(content) != '':
                            content_list.append(content)
                        else:
                            print(f'this url failed {each_url}')
                        try:
                            with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                file.write(content)
                        except Exception as e:
                            print(f"File write error: {e}")
                        print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')

                    else:
                        try:
                            with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                file.write('Url Subscription could not be parsed')
                        except Exception as e:
                            print(f"File write error: {e}")
                        print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')

            else:
                each_url = url_container.get("url", "")
                content = ''
                print("gather server from " + each_url)
                try:
                    content = sub_convert.convert_remote(each_url, 'url', 'http://127.0.0.1:25500')
                except Exception as e:
                    print(f"convert_remote error: {e}")
                    content = 'Url 解析错误'

                if content == 'Url 解析错误':
                    try:
                        content = sub_convert.main(each_url, 'url', 'url')
                    except Exception as e:
                        print(f"sub_convert.main error: {e}")
                        content = 'Url 解析错误'

                    if content != 'Url 解析错误':
                        if add_valid(content) != '':
                            content_list.append(content)
                        else:
                            print(f'this url failed {each_url}')
                        print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                    else:
                        print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')

                    try:
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write(content)
                    except Exception as e:
                        print(f"File write error: {e}")

                elif content == 'Url 订阅内容无法解析':
                    try:
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write('Url Subscription could not be parsed')
                    except Exception as e:
                        print(f"File write error: {e}")
                    print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')

                elif content is not None and content != '':
                    content_list.append(content)
                    try:
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write(content)
                    except Exception as e:
                        print(f"File write error: {e}")
                    print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')

                else:
                    try:
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write('Url Subscription could not be parsed')
                    except Exception as e:
                        print(f"File write error: {e}")
                    print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')

            print('already gathered ' + str(len(''.join(content_list).split('\n')) if content_list else 0))
            print('\n')

        print('Merging nodes...\n')

        content_list = list(filter(lambda x: x != '', ''.join(content_list).split("\n")))
        content_list = list(filter(lambda x: x.startswith(("ssr://", "ss://", "trojan://", "vmess://")), content_list))
        content_list = list(filter(lambda x: "订阅内容解析错误" not in x, content_list))
        content_raw = "\n".join(content_list)

        print(f"it's fine till here with {len(content_list)} lines")

        try:
            content_yaml = sub_convert.main(content_raw, 'content', 'YAML', {
                'dup_rm_enabled': True, 'format_name_enabled': True})
        except Exception as e:
            print(f"YAML convert error: {e}")
            content_yaml = ""

        yaml_proxies = content_yaml.split('\n')[1:] if content_yaml else []
        temp = list(filter(lambda x: re.search(ipv6, x) is None or re.search(ipv4, x) is not None, yaml_proxies))
        temp = list(filter(lambda x: re.search("path: /(.*?)\?(.*?)=(.*?)}", x) is None, temp))

        temp2 = temp
        temp = []
        for pr in temp2:
            try:
                yaml.safe_load(pr)
                temp.append(pr)
            except Exception as e:
                print(e)

        print(f"found {len(yaml_proxies) - len(temp)} bad lines :)")

        content_yaml = "\n".join(temp)
        if content_yaml and content_yaml.endswith('\n'):
            content_yaml = content_yaml.rstrip('\n')
        content_yaml = 'proxies:\n' + content_yaml

        try:
            content_raw = sub_convert.yaml_decode(content_yaml)
        except Exception as e:
            print(f"yaml_decode error: {e}")
            content_raw = ""

        try:
            content_base64 = sub_convert.base64_encode(content_raw)
        except Exception as e:
            print(f"base64_encode error: {e}")
            content_base64 = ""

        content = content_raw

        def content_write(file, output_type):
            try:
                with open(file, 'w+', encoding='utf-8') as f:
                    f.write(output_type if output_type else '')
            except Exception as e:
                print(f"Write {file} error: {e}")

        write_list = [f'{sub_merge_path}/sub_merge.txt',
                      f'{sub_merge_path}/sub_merge_base64.txt', f'{sub_merge_path}/sub_merge_yaml.yml']
        content_type = (content, content_base64, content_yaml)
        for index in range(len(write_list)):
            content_write(write_list[index], content_type[index])
        print('Done!\n')

    def read_list(json_file, remote=False):  # 将 sub_list.json Url 内容读取为列表
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                raw_list = json.load(f)
        except Exception as e:
            print(f"Read json error: {e}")
            return []

        input_list = []
        for item in raw_list:
            if item.get('enabled', False):
                if not remote:
                    urls = re.split(r'\|', item.get('url', ''))
                else:
                    urls = item.get('url', '')
                item['url'] = urls
                input_list.append(item)
        return input_list

    def geoip_update(url):
        print('Downloading Country.mmdb...')
        try:
            request.urlretrieve(url, './utils/Country.mmdb')
            print('Success!\n')
        except Exception as e:
            print(f'Failed: {e}\n')
            pass

    def readme_update(readme_file='./README.md', sub_list=[]):  # 更新 README 节点信息
        print('Update README.md file...')
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Read README error: {e}")
            return

        total = 0
        try:
            with open('./sub/sub_merge.txt', 'r', encoding='utf-8') as f:
                total = len(f.readlines())
        except Exception:
            pass
        total_line = f'Total number of merged nodes: `{total}`\n'

        thanks = []
        for repo in sub_list:
            if repo.get('enabled', False):
                try:
                    id = repo['id']
                    remarks = repo['remarks']
                    repo_site = repo.get('site', '#')
                    amount = 0
                    try:
                        with open(f'./sub/list/{id:0>2d}.txt', 'r', encoding='utf-8') as f:
                            data = f.read()
                            if data not in ['Url 解析错误', '订阅内容解析错误']:
                                amount = len(data.splitlines())
                    except Exception:
                        pass
                    thanks.append(f'- [{remarks}]({repo_site}), number of nodes: `{amount}`\n')
                except Exception:
                    continue

        # Обновляем блок с быстрыми узлами
        for idx in range(len(lines)):
            if lines[idx].strip() == '### high-speed node':
                while idx + 1 < len(lines) and not lines[idx+1].strip().startswith('###'):
                    lines.pop(idx+1)
                top_amount = 0
                proxies = []
                try:
                    with open('./Eternity', 'r', encoding='utf-8') as f:
                        proxies_base64 = f.read()
                        proxies_raw = sub_convert.base64_decode(proxies_base64)
                        proxies = ['    ' + p + '\n' for p in proxies_raw.splitlines() if p.strip()]
                        top_amount = len(proxies)
                except Exception:
                    pass
                lines.insert(idx+1, f'high-speed node quantity: `{top_amount}`\n')
                lines[idx+2:idx+2] = proxies
                break

        # Обновляем блок со всеми узлами
        for idx in range(len(lines)):
            if lines[idx].strip() == '### all nodes':
                while idx + 1 < len(lines) and not lines[idx+1].strip().startswith('###'):
                    lines.pop(idx+1)
                total_all = 0
                try:
                    with open('./sub/sub_merge_yaml.yml', 'r', encoding='utf-8') as f:
                        total_all = max(0, len(f.readlines()) - 1)
                except Exception:
                    pass
                lines.insert(idx+1, f'merge nodes w/o dup: `{total_all}`\n')
                break

        # Обновляем блок источников
        for idx in range(len(lines)):
            if lines[idx].strip() == '### node sources':
                while idx + 1 < len(lines) and not lines[idx+1].strip().startswith('###') and lines[idx+1].strip() != '':
                    lines.pop(idx+1)
                for line in reversed(thanks):
                    lines.insert(idx+1, line)
                break

        # Записываем обратно
        try:
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print('Finish!\n')
        except Exception as e:
            print(f"Write README error: {e}")


if __name__ == '__main__':
    update_url.update_main(use_airport=False, airports_id=[5], sub_list_json="./sub/sub_list.json")
    sub_merge.geoip_update('https://raw.githubusercontent.com/Loyalsoldier/geoip/release/Country.mmdb')

    sub_list = sub_merge.read_list(sub_list_json)
    # sub_list_remote = sub_merge.read_list(sub_list_json, True)

    # Стандартные методы — оставил как комментарии, как у автора
    # sub_merge.sub_merge(sub_list)
    # sub_merge.readme_update(readme, sub_list)
    # subs.get_subs(sub_list)
    # subs.get_subs_v2(sub_list)

    # Основной рабочий метод из кода
    subs.get_subs_v3([x for x in sub_list if x.get('id') != 5])
    sub_merge.readme_update(readme, sub_list)
