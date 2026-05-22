from sub_convert import sub_convert
from subs_function import subs_function

import json
import re
import os
import yaml

sub_list_json = './sub/sub_list.json'
sub_merge_path = './sub/'
sub_list_path = './sub/list/'

ipv4 = r"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"
ipv6 = r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'
ill = ['|', '?', '[', ']', '@', '!', '%', ':']
valid_ss_cipher_methods = ["aes-128-gcm", "aes-192-gcm", "aes-256-gcm", "aes-128-cfb", "aes-192-cfb", "aes-256-cfb", "aes-128-ctr", "aes-192-ctr", "aes-256-ctr", "rc4-md5", "chacha20-ietf", "xchacha20", "chacha20-ietf-poly1305", "xchacha20-ietf-poly1305"]
valid_ss_plugins = ["obfs","v2ray-plugin"]

class subs:

    def get_subs(content_urls: []):
        if content_urls == []:
            return

        for t in os.walk(sub_list_path):
            for f in t[2]:
                f = t[0]+f
                os.remove(f)

        content_list = []
        for (index, url_container) in enumerate(content_urls):
            ids = content_urls[index]['id']
            remarks = content_urls[index]['remarks']
            if type(url_container['url']) == list:
                for each_url in url_container["url"]:
                    print("gather server from " + each_url)
                    content = subs_function.convert_sub(
                        each_url, 'mixed', "http://0.0.0.0:25500")
                    print("added content: %s" %
                          str(len(content.split('\n')) if content else 0))
                    if content == 'Err: No nodes found' or content == 'Err: failed to parse sub':
                        print("host convertor failed. trying manually...")
                        content = sub_convert.main(each_url, 'url', 'url')
                        if content != 'Url 解析错误' and content != '订阅内容解析错误':
                            if content and subs_function.is_line_valid(content, False) != '':
                                content_list.append(content)
                            else:
                                print(f'this url failed{each_url}')
                            print(
                                f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                        else:
                            print(
                                f'Writing error of {remarks} to {ids:0>2d}.txt\n')

                            if content == 'Err: No nodes found':
                                with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                    file.write(content)

                            if content == 'Err: failed to parse sub':
                                with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                    file.write('Err: failed to parse sub')

                    elif content is not None and content != '':
                        if subs_function.is_line_valid(content, False) != '':
                            content_list.append(content)
                        else:
                            print(f'this url failed {each_url}')
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write(content)
                        print(
                            f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                    else:
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write('Url Subscription could not be parsed')
                        print(
                            f'Writing error of {remarks} to {ids:0>2d}.txt\n')

            print('already gathered ' +
                  str(len(''.join(content_list).split('\n'))))
            print('\n')

        print('Merging nodes...\n')

        content_list = list(
            filter(lambda x: x != '', ''.join(content_list).split("\n")))
        content_raw = "\n".join(content_list)

        print(f"it's fine till here with {len(content_list)} lines")

        content_yaml = sub_convert.main(content_raw, 'content', 'YAML', {
            'dup_rm_enabled': True, 'format_name_enabled': True})

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
        if content_yaml and content_yaml[-1:] == '\n':
            content_yaml = content_yaml[:-1]
        content_yaml = 'proxies:\n' + content_yaml

        content_raw = sub_convert.yaml_decode(content_yaml)

        content_base64 = sub_convert.base64_encode(content_raw)
        content = content_raw

        def content_write(file, output_type):
            with open(file, 'w+', encoding='utf-8') as f:
                f.write(output_type if output_type else '')

        write_list = [f'{sub_merge_path}/sub_merge.txt',
                      f'{sub_merge_path}/sub_merge_base64.txt', f'{sub_merge_path}/sub_merge_yaml.yml']
        content_type = (content, content_base64, content_yaml)
        for index in range(len(write_list)):
            content_write(write_list[index], content_type[index])
        print('Done!\n')

    def get_subs_v2(content_urls: []):
        if content_urls == []:
            return

        for t in os.walk(sub_list_path):
            for f in t[2]:
                f = t[0]+f
                os.remove(f)

        content_list = []
        corresponding_list = []
        corresponding_id = 0
        bad_lines = 0
        for (index, url_container) in enumerate(content_urls):
            ids = content_urls[index]['id']
            remarks = content_urls[index]['remarks']
            if type(url_container['url']) == list:
                for each_url in url_container["url"]:
                    print("gather server from " + each_url)

                    content = subs_function.convert_sub(
                        each_url, 'mixed', "http://0.0.0.0:25500", False)
                    content_clash = subs_function.convert_sub(
                        each_url, 'clash', "http://0.0.0.0:25500", False)

                    if content == 'Err: No nodes found' or content == 'Err: failed to parse sub' or content_clash == 'Err: No nodes found' or content_clash == 'Err: failed to parse sub':
                        print("host convertor failed. just continue & ignore...")

                        if content == 'Err: No nodes found' or content_clash == 'Err: No nodes found':
                            with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                file.write('Err: No nodes found')

                        if content == 'Err: failed to parse sub' or content_clash == 'Err: failed to parse sub':
                            with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                file.write('Err: failed to parse sub')

                    elif content is not None and content != '':
                        single_url_gather_quantity = len(list(filter(lambda x: x != '', content.split('\n'))))
                        print(f"added content of current url : {single_url_gather_quantity}")
                        if subs_function.is_line_valid(content, False) != '':
                            content_list.append(content)
                            with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                file.write(content)
                            print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')

                            mixed_content = list(filter(lambda x: x != '', content.split('\n')))
                            clash_content = list(filter(lambda x: x != '', content_clash.split('\n')[1:])) if content_clash else []

                            if len(mixed_content) == len(clash_content) and len(clash_content) > 0:
                                safe_clash = []
                                safe_mixed = []
                                for (idx, cl) in enumerate(clash_content):
                                    try:
                                        if re.search(ipv6, str(cl)) is None or re.search(ipv4, str(cl)) is not None:
                                            if re.search("path: /(.*?)\?(.*?)=(.*?)}", str(cl)) is None:
                                                cl_res = yaml.safe_load(cl)
                                                if cl_res is not None:
                                                    safe_clash.append(cl_res)
                                                    safe_mixed.append(mixed_content[idx])
                                    except Exception as e:
                                        bad_lines += 1

                                if len(safe_clash) == len(safe_mixed) and len(safe_clash) > 0:
                                    print("Check Points Passed 👍\n")
                                    for (i, each_mixed_proxy) in enumerate(safe_mixed):
                                        if subs_function.is_line_valid(each_mixed_proxy, False):
                                            corresponding_list.append(
                                                {"id": corresponding_id, "c_clash": safe_clash[i], "c_mixed": each_mixed_proxy})
                                            corresponding_id += 1
                                else:
                                    print(f'unmatched length in sources {each_url}')
                                    with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                        file.write("unmatched length in sources")
                                    print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                            else:
                                print(f'unmatch length in both sources first stage {each_url}')
                                with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                    file.write("unmatch length in both sources first stage")
                                print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                        else:
                            print(f'started with a invalid url {each_url}')
                            with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                file.write("started with a invalid url")
                            print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                    else:
                        with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                            file.write('Url Subscription could not be parsed')
                        print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')

        print(f"already gathered {len(list(filter(lambda x: x != '', ''.join(content_list).split('\n'))))}")
        print('\n----------------------------------------------\n')
        print('Merging nodes...\n')

        content_list = list(filter(lambda x: x != '', ''.join(content_list).split('\n')))
        content_raw = "\n".join(content_list)
        print(f"{len(content_list)} lines - {bad_lines} bad lines => total is {len(content_list) - bad_lines}")

        corresponding_list = subs_function.fix_proxies_name(corresponding_proxies=corresponding_list)
        corresponding_list = subs_function.fix_proxies_duplication(corresponding_proxies=corresponding_list)
        print(f"\nfinal sub length => {len(corresponding_list)}")

        clash = list(map(lambda x: f"  - {x['c_clash']}", corresponding_list))
        mixed = list(map(lambda x: x["c_mixed"], corresponding_list))
        content_raw = "\n".join(mixed)
        content_yaml = 'proxies:\n' + "\n".join(clash)
        content_base64 = sub_convert.base64_encode(content_raw)
        content = content_raw

        def content_write(file, output_type):
            with open(file, 'w+', encoding='utf-8') as f:
                f.write(output_type if output_type else '')

        write_list = [f'{sub_merge_path}/sub_merge.txt',
                      f'{sub_merge_path}/sub_merge_base64.txt', f'{sub_merge_path}/sub_merge_yaml.yml']
        content_type = (content, content_base64, content_yaml)
        for index in range(len(write_list)):
            content_write(write_list[index], content_type[index])
        print('Done!\n')

    def get_subs_v3(content_urls: [], output_path="sub_merge_yaml", should_cleanup=True, specific_files_cleanup=["05.txt"]):
        if content_urls == []:
            return

        if should_cleanup:
            for t in os.walk(sub_list_path):
                for f in t[2]:
                    if specific_files_cleanup.__contains__(f) == False:
                        os.remove(os.path.join(t[0], f))
        else:
            for t in os.walk(sub_list_path):
                for f in t[2]:
                    if specific_files_cleanup.__contains__(f):
                        os.remove(os.path.join(t[0], f))

        content_list = []
        corresponding_list = []
        corresponding_id = 0
        bad_lines = 0
        for (index, url_container) in enumerate(content_urls):
            ids = content_urls[index]['id']
            remarks = content_urls[index]['remarks']
            if type(url_container['url']) == list:
                for each_url in url_container["url"]:
                    print("gather server from " + each_url)

                    content_clash = subs_function.convert_sub(
                        each_url, 'clash', "http://0.0.0.0:25500", False, extra_options="&udp=false")

                    if content_clash == 'Err: No nodes found' or content_clash == 'Err: failed to parse sub':
                        print("host convertor was unable to find any nodes. just continue & ignore...\n")
                    elif content_clash is not None and content_clash != '':
                        single_url_gather_quantity = len(list(filter(lambda x: x != '', content_clash.split('\n')))) - 1
                        print(f"added content of current url : {single_url_gather_quantity}")

                        clash_content = list(filter(lambda x: x != '', content_clash.split('\n')[1:]))
                        if len(clash_content) > 0:
                            safe_clash = []
                            for (idx, cl) in enumerate(clash_content):
                                try:
                                    if re.search(ipv6, str(cl)) is None or re.search(ipv4, str(cl)) is not None:
                                        if re.search("path: /(.*?)\?(.*?)=(.*?)}", str(cl)) is None:
                                            cl_res = yaml.safe_load(cl)
                                            if cl_res is not None:
                                                try:
                                                    cl_temp = cl_res[0]
                                                    bad_uuid_format = False
                                                    if 'uuid' in cl_temp and len(cl_temp['uuid']) != 36:
                                                        bad_uuid_format = True
                                                        bad_lines += 1
                                                    if not bad_uuid_format:
                                                        if cl_temp['type'] == "ss" or cl_temp['type'] == "ssr":
                                                            if cl_temp["cipher"] in valid_ss_cipher_methods:
                                                                if cl_temp['type'] == "ss":
                                                                    if 'plugin' in cl_temp:
                                                                        if cl_temp['plugin'] in valid_ss_plugins:
                                                                            if cl_temp['plugin'] == 'obfs':
                                                                                if 'plugin-opts' in cl_temp:
                                                                                    if cl_temp['plugin-opts']['mode'] in ('http', 'tls'):
                                                                                        safe_clash.append(cl_res)
                                                                                    else: bad_lines += 1
                                                                                else: safe_clash.append(cl_res)
                                                                            elif cl_temp['plugin'] == 'v2ray-plugin':
                                                                                if 'plugin-opts' in cl_temp and cl_temp['plugin-opts']['mode'] == 'websocket':
                                                                                    safe_clash.append(cl_res)
                                                                                else: bad_lines += 1
                                                                            else: safe_clash.append(cl_res)
                                                                        else: bad_lines += 1
                                                                    else: safe_clash.append(cl_res)
                                                                else: safe_clash.append(cl_res)
                                                            else: bad_lines += 1
                                                        elif cl_temp['type'] == "vmess":
                                                            if cl_temp["network"] in ("h2", "grpc"):
                                                                if "tls" in cl_temp and cl_temp['tls'] is False:
                                                                    bad_lines += 1
                                                                else: safe_clash.append(cl_res)
                                                            else: safe_clash.append(cl_res)
                                                        else: safe_clash.append(cl_res)
                                                except Exception:
                                                    bad_lines += 1
                                except Exception:
                                    bad_lines += 1

                            if len(safe_clash) > 0:
                                content_list.append("\n".join(clash_content) + "\n")
                                with open(f'{sub_list_path}{ids:0>2d}.txt', 'a+', encoding='utf-8') as file:
                                    file.write("\n".join(clash_content) + "\n")
                                print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                                print("Check Points Passed 👍\n")
                                for each_clash_proxy in safe_clash:
                                    corresponding_list.append({"id": corresponding_id, "c_clash": each_clash_proxy})
                                    corresponding_id += 1
                            else:
                                print(f'there is no clash lines {each_url}')
                                print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')

        print(f"already gathered {len(list(filter(lambda x: x != '', ''.join(content_list).split('\n'))))}")
        print('\n----------------------------------------------\n')
        print('Merging nodes...\n')

        content_list = list(filter(lambda x: x != '', ''.join(content_list).split('\n')))
        print(f"{len(content_list)} lines - {bad_lines} bad lines => total is {len(content_list) - bad_lines}")

        corresponding_list = subs_function.fix_proxies_name(corresponding_proxies=corresponding_list)
        corresponding_list = subs_function.fix_proxies_duplication(corresponding_proxies=corresponding_list)
        print(f"\nfinal sub length => {len(corresponding_list)}")

        clash = list(map(lambda x: f"  - {x['c_clash']}", corresponding_list))
        content_yaml = 'proxies:\n' + "\n".join(clash)

        def content_write(file, output_type):
            with open(file, 'w+', encoding='utf-8') as f:
                f.write(output_type if output_type else '')

        content_write(f'{sub_merge_path}/{output_path}.yml', content_yaml)
        print('Done!\n')


if __name__ == "__main__":
    subs.get_subs([])
