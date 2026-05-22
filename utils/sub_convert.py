#!/usr/bin/env python3

import re
import yaml
import json
import base64
import requests
import socket
import urllib.parse
from requests.adapters import HTTPAdapter
import geoip2.database


def main(raw_input, input_type='url', output_type='url', custom_set={'dup_rm_enabled': False, 'format_name_enabled': False}):
    if input_type == 'url':
        sub_content = ''
        if isinstance(raw_input, list):
            a_content = []
            for url in raw_input:
                s = requests.Session()
                s.mount('http://', HTTPAdapter(max_retries=5))
                s.mount('https://', HTTPAdapter(max_retries=5))
                try:
                    print('Downloading from:' + url)
                    resp = s.get(url, timeout=5)
                    s_content = yaml_decode(format(resp.content.decode('utf-8')))
                    a_content.append(s_content)
                except Exception as err:
                    print(err)
                    return 'Url 解析错误'
            sub_content = format(''.join(a_content))
        else:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=5))
            s.mount('https://', HTTPAdapter(max_retries=5))
            try:
                print('Downloading from:' + raw_input)
                resp = s.get(raw_input, timeout=5)
                sub_content = format(resp.content.decode('utf-8'))
            except Exception as err:
                print(err)
                return 'Url 解析错误'
    elif input_type == 'content':
        sub_content = format(raw_input)

    if sub_content != '订阅内容解析错误':
        dup_rm_enabled = custom_set['dup_rm_enabled']
        format_name_enabled = custom_set['format_name_enabled']
        final_content = makeup(sub_content, dup_rm_enabled, format_name_enabled)
        if output_type == 'YAML':
            return final_content
        elif output_type == 'Base64':
            return base64_encode(yaml_decode(final_content))
        elif output_type == 'url':
            return yaml_decode(final_content)
        elif output_type == 'content':
            return yaml_decode(final_content)
        else:
            print('Please define right output type.')
            return '订阅内容解析错误'
    else:
        return '订阅内容解析错误'


def format(sub_content, output=False):
    if '</b>' not in sub_content:
        if 'proxies:' not in sub_content:
            url_list = []
            try:
                if '://' not in sub_content:
                    sub_content = base64_decode(sub_content)
                raw_url_list = re.split(r'\r?\n+', sub_content)
                for url in raw_url_list:
                    while len(re.split('ss://|ssr://|vmess://|trojan://|vless://', url)) > 2:
                        try:
                            url_to_split = url[8:]
                            if 'ss://' in url_to_split and 'vmess://' not in url_to_split and 'vless://' not in url_to_split:
                                url_splited = url_to_split.replace('ss://', '\nss://', 1)
                            elif 'ssr://' in url_to_split:
                                url_splited = url_to_split.replace('ssr://', '\nssr://', 1)
                            elif 'vmess://' in url_to_split:
                                url_splited = url_to_split.replace('vmess://', '\nvmess://', 1)
                            elif 'trojan://' in url_to_split:
                                url_splited = url_to_split.replace('trojan://', '\ntrojan://', 1)
                            elif 'vless://' in url_to_split:
                                url_splited = url_to_split.replace('vless://', '\nvless://', 1)
                            url_split = url_splited.split('\n')
                            front_url = url[:8] + url_split[0]
                            url_list.append(front_url)
                            url = url_split[1]
                        except Exception as e:
                            print(f"failed to fix one line in formatting line: {url}")
                    url_list.append(url)
                    url_content = '\n'.join(url_list)
                    return yaml_encode(url_content, output=False)
            except:
                print('Sub_content 格式错误')
                return '订阅内容解析错误'
        elif 'proxies:' in sub_content:
            try:
                if '!<str> ' in sub_content:
                    sub_content = sub_content.replace('!<str> ', '').replace('!<str>', '')
                try_load = yaml.safe_load(sub_content)
                if output:
                    raise ValueError
                else:
                    content_yaml_dic = try_load
                    return content_yaml_dic
            except Exception:
                try:
                    sub_content = sub_content.replace('\'', '').replace('"', '')
                    url_list = []
                    il_chars = ['|', '?', '[', ']', '@', '!', '%', ':']
                    lines = re.split(r'\n+', sub_content)
                    line_fix_list = []
                    for line in lines:
                        value_list = re.split(r': |, ', line)
                        if len(value_list) > 6:
                            value_list_fix = []
                            for value in value_list:
                                for char in il_chars:
                                    value_il = False
                                    if char in value:
                                        value_il = True
                                        break
                                if value_il == True and ('{' not in value and '}' not in value):
                                    value = '"' + value + '"'
                                    value_list_fix.append(value)
                                elif value_il == True and '}' in value:
                                    if '}}}' in value:
                                        host_part = value.replace('}}}', '')
                                        host_value = '"'+host_part+'"}}}'
                                        value_list_fix.append(host_value)
                                    elif '}}' not in value:
                                        host_part = value.replace('}', '')
                                        host_value = '"'+host_part+'"}'
                                        value_list_fix.append(host_value)
                                else:
                                    value_list_fix.append(value)
                                line_fix = line
                            for index in range(len(value_list_fix)):
                                line_fix = line_fix.replace(value_list[index], value_list_fix[index])
                            line_fix_list.append(line_fix)
                        elif len(value_list) == 2:
                            value_list_fix = []
                            for value in value_list:
                                for char in il_chars:
                                    value_il = False
                                    if char in value:
                                        value_il = True
                                        break
                                if value_il == True:
                                    value = '"' + value + '"'
                                value_list_fix.append(value)
                            line_fix = line
                            for index in range(len(value_list_fix)):
                                line_fix = line_fix.replace(value_list[index], value_list_fix[index])
                            line_fix_list.append(line_fix)
                        elif len(value_list) == 1:
                            if ':' in line:
                                line_fix_list.append(line)
                        else:
                            line_fix_list.append(line)
                    sub_content = '\n'.join(line_fix_list).replace('False', 'false').replace('True', 'true')
                    if output:
                        return sub_content
                    else:
                        content_yaml_dic = yaml.safe_load(sub_content)
                        return content_yaml_dic
                except:
                    print('Sub_content 格式错误')
                    return '订阅内容解析错误'
        else:
            print('订阅内容解析错误')
            return '订阅内容解析错误'
    else:
        print('订阅内容解析错误')
        return '订阅内容解析错误'


def makeup(input, dup_rm_enabled=False, format_name_enabled=False):
    if isinstance(input, dict):
        sub_content = input
    else:
        sub_content = format(input)
    proxies_list = sub_content['proxies']
    if dup_rm_enabled:
        print("\nBefore was " + str(proxies_list.__len__()) + "\n")
        begin = 0
        raw_length = len(proxies_list)
        length = len(proxies_list)
        while begin < length:
            if (begin + 1) == 1:
                print(f'\n-----Restart-----\nStarting quantity {length}')
            elif (begin + 1) % 100 == 0:
                print(f'current benchmark {begin + 1}-----current quantity {length}')
            elif (begin + 1) == length and (begin + 1) % 100 != 0:
                repetition = raw_length - length
                print(f'current benchmark {begin + 1}-----current quantity {length}\nnumber of repetition {repetition}\n-----deduplication completed-----\n')
            proxy_compared = proxies_list[begin]
            begin_2 = begin + 1
            while begin_2 <= (length - 1):
                check = False
                if proxy_compared['server'] == proxies_list[begin_2]['server'] and proxy_compared['port'] == proxies_list[begin_2]['port']:
                    check = True
                    if 'net' in proxies_list[begin_2] and 'net' in proxy_compared:
                        if proxy_compared['net'] != proxies_list[begin_2]['net']:
                            check = False
                    if 'tls' in proxies_list[begin_2] and 'tls' in proxy_compared:
                        if proxy_compared['tls'] != proxies_list[begin_2]['tls']:
                            check = False
                    if 'id' in proxies_list[begin_2] and 'id' in proxy_compared:
                        if proxy_compared['id'] != proxies_list[begin_2]['id']:
                            check = False
                    if 'password' in proxies_list[begin_2] and 'password' in proxy_compared:
                        if proxy_compared['password'] != proxies_list[begin_2]['password']:
                            check = False
                    if 'cipher' in proxies_list[begin_2] and 'cipher' in proxy_compared:
                        if proxy_compared['cipher'] != proxies_list[begin_2]['cipher']:
                            check = False
                    if 'type' in proxies_list[begin_2] and 'type' in proxy_compared:
                        if proxy_compared['type'] != proxies_list[begin_2]['type']:
                            check = False
                    if check:
                        proxies_list.pop(begin_2)
                        length -= 1
                begin_2 += 1
            begin += 1
        print("\nNow is " + str(proxies_list.__len__()) + "\n")
    url_list = []
    for proxy in proxies_list:
        if format_name_enabled:
            emoji = {
                'AD': '🇦🇩', 'AE': '🇦🇪', 'AF': '🇦🇫', 'AG': '🇦🇬', 'AI': '🇦🇮', 'AL': '🇦🇱', 'AM': '🇦🇲', 'AO': '🇦🇴', 'AQ': '🇦🇶', 'AR': '🇦🇷', 'AS': '🇦🇸', 'AT': '🇦🇹',
                'AU': '🇦🇺', 'AW': '🇦🇼', 'AX': '🇦🇽', 'AZ': '🇦🇿', 'BA': '🇧🇦', 'BB': '🇧🇧', 'BD': '🇧🇩', 'BE': '🇧🇪', 'BF': '🇧🇫', 'BG': '🇧🇬', 'BH': '🇧🇭', 'BI': '🇧🇮',
                'BJ': '🇧🇯', 'BL': '🇧🇱', 'BM': '🇧🇲', 'BN': '🇧🇳', 'BO': '🇧🇴', 'BQ': '🇧🇶', 'BR': '🇧🇷', 'BS': '🇧🇸', 'BT': '🇧🇹', 'BV': '🇧🇻', 'BW': '🇧🇼', 'BY': '🇧🇾',
                'BZ': '🇧🇿', 'CA': '🇨🇦', 'CC': '🇨🇨', 'CD': '🇨🇩', 'CF': '🇨🇫', 'CG': '🇨🇬', 'CH': '🇨🇭', 'CI': '🇨🇮', 'CK': '🇨🇰', 'CL': '🇨🇱', 'CM': '🇨🇲', 'CN': '🇨🇳',
                'CO': '🇨🇴', 'CR': '🇨🇷', 'CU': '🇨🇺', 'CV': '🇨🇻', 'CW': '🇨🇼', 'CX': '🇨🇽', 'CY': '🇨🇾', 'CZ': '🇨🇿', 'DE': '🇩🇪', 'DJ': '🇩🇯', 'DK': '🇩🇰', 'DM': '🇩🇲',
                'DO': '🇩🇴', 'DZ': '🇩🇿', 'EC': '🇪🇨', 'EE': '🇪🇪', 'EG': '🇪🇬', 'EH': '🇪🇭', 'ER': '🇪🇷', 'ET': '🇪🇹', 'EU': '🇪🇺', 'FI': '🇫🇮', 'FJ': '🇫🇯', 'FK': '🇫🇰',
                'FM': '🇫🇲', 'FO': '🇫🇴', 'FR': '🇫🇷', 'GA': '🇬🇦', 'GB': '🇬🇧', 'GD': '🇬🇩', 'GE': '🇬🇪', 'GF': '🇬🇫', 'GG': '🇬🇬', 'GH': '🇬🇭', 'GI': '🇬🇮', 'GL': '🇬🇱',
                'GM': '🇬🇲', 'GN': '🇬🇳', 'GP': '🇬🇵', 'GQ': '🇬🇶', 'GR': '🇬🇷', 'GS': '🇬🇸', 'GT': '🇬🇹', 'GU': '🇬🇺', 'GW': '🇬🇼', 'GY': '🇬🇾', 'HK': '🇭🇰', 'HM': '🇭🇲',
                'HN': '🇭🇳', 'HR': '🇭🇷', 'HT': '🇭🇹', 'HU': '🇭🇺', 'ID': '🇮🇩', 'IE': '🇮🇪', 'IL': '🇮🇱', 'IM': '🇮🇲', 'IN': '🇮🇳', 'IO': '🇮🇴', 'IQ': '🇮🇶', 'IR': '🇮🇷',
                'IS': '🇮🇸', 'IT': '🇮🇹', 'JE': '🇯🇪', 'JM': '🇯🇲', 'JO': '🇯🇴', 'JP': '🇯🇵', 'KE': '🇰🇪', 'KG': '🇰🇬', 'KH': '🇰🇭', 'KI': '🇰🇮', 'KM': '🇰🇲', 'KN': '🇰🇳',
                'KP': '🇰🇵', 'KR': '🇰🇷', 'KW': '🇰🇼', 'KY': '🇰🇾', 'KZ': '🇰🇿', 'LA': '🇱🇦', 'LB': '🇱🇧', 'LC': '🇱🇨', 'LI': '🇱🇮', 'LK': '🇱🇰', 'LR': '🇱🇷', 'LS': '🇱🇸',
                'LT': '🇱🇹', 'LU': '🇱🇺', 'LV': '🇱🇻', 'LY': '🇱🇾', 'MA': '🇲🇦', 'MC': '🇲🇨', 'MD': '🇲🇩', 'ME': '🇲🇪', 'MF': '🇲🇫', 'MG': '🇲🇬', 'MH': '🇲🇭', 'MK': '🇲🇰',
                'ML': '🇲🇱', 'MM': '🇲🇲', 'MN': '🇲🇳', 'MO': '🇲🇴', 'MP': '🇲🇵', 'MQ': '🇲🇶', 'MR': '🇲🇷', 'MS': '🇲🇸', 'MT': '🇲🇹', 'MU': '🇲🇺', 'MV': '🇲🇻', 'MW': '🇲🇼',
                'MX': '🇲🇽', 'MY': '🇲🇾', 'MZ': '🇲🇿', 'NA': '🇳🇦', 'NC': '🇳🇨', 'NE': '🇳🇪', 'NF': '🇳🇫', 'NG': '🇳🇬', 'NI': '🇳🇮', 'NL': '🇳🇱', 'NO': '🇳🇴', 'NP': '🇳🇵',
                'NR': '🇳🇷', 'NU': '🇳🇺', 'NZ': '🇳🇿', 'OM': '🇴🇲', 'PA': '🇵🇦', 'PE': '🇵🇪', 'PF': '🇵🇫', 'PG': '🇵🇬', 'PH': '🇵🇭', 'PK': '🇵🇰', 'PL': '🇵🇱', 'PM': '🇵🇲',
                'PN': '🇵🇳', 'PR': '🇵🇷', 'PS': '🇵🇸', 'PT': '🇵🇹', 'PW': '🇵🇼', 'PY': '🇵🇾', 'QA': '🇶🇦', 'RE': '🇷🇪', 'RO': '🇷🇴', 'RS': '🇷🇸', 'RU': '🇷🇺', 'RW': '🇷🇼',
                'SA': '🇸🇦', 'SB': '🇸🇧', 'SC': '🇸🇨', 'SD': '🇸🇩', 'SE': '🇸🇪', 'SG': '🇸🇬', 'SH': '🇸🇭', 'SI': '🇸🇮', 'SJ': '🇸🇯', 'SK': '🇸🇰', 'SL': '🇸🇱', 'SM': '🇸🇲',
                'SN': '🇸🇳', 'SO': '🇸🇴', 'SR': '🇸🇷', 'SS': '🇸🇸', 'ST': '🇸🇹', 'SV': '🇸🇻', 'SX': '🇸🇽', 'SY': '🇸🇾', 'SZ': '🇸🇿', 'TC': '🇹🇨', 'TD': '🇹🇩', 'TF': '🇹🇫',
                'TG': '🇹🇬', 'TH': '🇹🇭', 'TJ': '🇹🇯', 'TK': '🇹🇰', 'TL': '🇹🇱', 'TM': '🇹🇲', 'TN': '🇹🇳', 'TO': '🇹🇴', 'TR': '🇹🇷', 'TT': '🇹🇹', 'TV': '🇹🇻', 'TW': '🇹🇼',
                'TZ': '🇹🇿', 'UA': '🇺🇦', 'UG': '🇺🇬', 'UM': '🇺🇲', 'US': '🇺🇸', 'UY': '🇺🇾', 'UZ': '🇺🇿', 'VA': '🇻🇦', 'VC': '🇻🇨', 'VE': '🇻🇪', 'VG': '🇻🇬', 'VI': '🇻🇮',
                'VN': '🇻🇳', 'VU': '🇻🇺', 'WF': '🇼🇫', 'WS': '🇼🇸', 'XK': '🇽🇰', 'YE': '🇾🇪', 'YT': '🇾🇹', 'ZA': '🇿🇦', 'ZM': '🇿🇲', 'ZW': '🇿🇼', 'RELAY': '🏁', 'NOWHERE': '🇦🇶',
            }
            server = proxy['server']
            if server.replace('.', '').isdigit():
                ip = server
            else:
                try:
                    ip = socket.gethostbyname(server)
                except Exception:
                    ip = server
            try:
                with geoip2.database.Reader('./utils/Country.mmdb') as ip_reader:
                    response = ip_reader.country(ip)
                    country_code = response.country.iso_code
            except Exception:
                ip = '0.0.0.0'
                country_code = 'NOWHERE'
            if country_code == 'CLOUDFLARE':
                country_code = 'RELAY'
            elif country_code == 'PRIVATE':
                country_code = 'RELAY'
            if country_code in emoji:
                name_emoji = emoji[country_code]
            else:
                name_emoji = emoji['NOWHERE']
            proxy_index = proxies_list.index(proxy)
            if len(proxies_list) >= 999:
                proxy['name'] = f'{name_emoji}{country_code}-{ip}-{proxy_index:0>4d}'
            elif len(proxies_list) <= 999 and len(proxies_list) > 99:
                proxy['name'] = f'{name_emoji}{country_code}-{ip}-{proxy_index:0>3d}'
            elif len(proxies_list) <= 99:
                proxy['name'] = f'{name_emoji}{country_code}-{ip}-{proxy_index:0>2d}'
            if proxy['server'] != '127.0.0.1':
                proxy_str = str(proxy)
                url_list.append(proxy_str)
        elif format_name_enabled == False:
            if proxy['server'] != '127.0.0.1':
                proxy_str = str(proxy)
                url_list.append(proxy_str)
    yaml_content_dic = {'proxies': url_list}
    yaml_content_raw = yaml.dump(yaml_content_dic, default_flow_style=False, sort_keys=False, allow_unicode=True, width=750, indent=2)
    yaml_content = format(yaml_content_raw, output=True)
    return yaml_content


def yaml_encode(url_content, output=True):
    try:
        url_list = []
        lines = re.split(r'\n+', url_content)
        for line in lines:
            try:
                yaml_url = {}
                if 'vmess://' in line:
                    try:
                        vmess_json_config = json.loads(base64_decode(line.replace('vmess://', '')))
                        vmess_default_config = {
                            'v': 'Vmess Node', 'ps': 'Vmess Node', 'add': '0.0.0.0', 'port': 0, 'id': '',
                            'aid': 0, 'scy': 'auto', 'net': '', 'type': '', 'host': '', 'path': '/', 'tls': ''
                        }
                        vmess_default_config.update(vmess_json_config)
                        vmess_config = vmess_default_config
                        yaml_url.setdefault('name', urllib.parse.unquote(str(vmess_config['ps'])))
                        yaml_url.setdefault('server', vmess_config['add'])
                        yaml_url.setdefault('port', int(vmess_config['port']))
                        yaml_url.setdefault('type', 'vmess')
                        yaml_url.setdefault('uuid', vmess_config['id'])
                        yaml_url.setdefault('alterId', int(vmess_config['aid']))
                        yaml_url.setdefault('cipher', vmess_config['scy'])
                        yaml_url.setdefault('skip-cert-verify', True)
                        if vmess_config['net'] == '' or vmess_config['net'] is False or vmess_config['net'] is None:
                            yaml_url.setdefault('network', 'tcp')
                        else:
                            yaml_url.setdefault('network', vmess_config['net'])
                        if vmess_config['tls'] == 'tls' or vmess_config['net'] == 'h2' or vmess_config['net'] == 'grpc':
                            yaml_url.setdefault('tls', True)
                        yaml_url.setdefault('ws-opts', {})
                        if vmess_config['path'] == '' or vmess_config['path'] is False or vmess_config['path'] is None:
                            pass
                        else:
                            yaml_url['ws-opts'].setdefault('path', vmess_config['path'])
                        if vmess_config['host'] == '':
                            pass
                        else:
                            yaml_url['ws-opts'].setdefault('headers', {'Host': vmess_config['host']})
                        url_list.append(yaml_url)
                    except Exception as err:
                        print(f'yaml_encode 解析 vmess 节点发生错误: {err}')
                        pass
                if 'ss://' in line and 'vless://' not in line and 'vmess://' not in line:
                    if '#' not in line:
                        line = line + '#SS%20Node'
                    try:
                        ss_content = line.replace('ss://', '')
                        part_list = ss_content.split('#', 1)
                        yaml_url.setdefault('name', urllib.parse.unquote(part_list[1]))
                        if '@' in part_list[0]:
                            mix_part = part_list[0].split('@', 1)
                            method_part = base64_decode(mix_part[0])
                            server_part = f'{method_part}@{mix_part[1]}'
                        else:
                            server_part = base64_decode(part_list[0])
                        server_part_list = server_part.split(':', 1)
                        method_part = server_part_list[0]
                        server_part_list = server_part_list[1].rsplit('@', 1)
                        password_part = server_part_list[0]
                        server_part_list = server_part_list[1].split(':', 1)
                        yaml_url.setdefault('server', server_part_list[0])
                        yaml_url.setdefault('port', server_part_list[1])
                        yaml_url.setdefault('type', 'ss')
                        yaml_url.setdefault('cipher', method_part)
                        yaml_url.setdefault('password', password_part)
                        url_list.append(yaml_url)
                    except Exception as err:
                        print(f'yaml_encode 解析 ss 节点发生错误: {err}')
                        pass
                if 'ssr://' in line:
                    try:
                        ssr_content = base64_decode(line.replace('ssr://', ''))
                        parts = re.split(':', ssr_content)
                        if len(parts) != 6:
                            print('SSR 格式错误: %s' % ssr_content)
                        password_and_params = parts[5]
                        password_and_params = re.split('/\?', password_and_params)
                        password_encode_str = password_and_params[0]
                        params = password_and_params[1]
                        param_parts = re.split('\&', params)
                        param_dic = {'remarks': 'U1NSIE5vZGU=', 'obfsparam': '', 'protoparam': '', 'group': ''}
                        for part in param_parts:
                            key_and_value = re.split('\=', part)
                            param_dic.update({key_and_value[0]: key_and_value[1]})
                        yaml_url.setdefault('name', base64_decode(param_dic['remarks']))
                        yaml_url.setdefault('server', parts[0])
                        yaml_url.setdefault('port', parts[1])
                        yaml_url.setdefault('type', 'ssr')
                        yaml_url.setdefault('cipher', parts[3])
                        yaml_url.setdefault('password', base64_decode(password_encode_str))
                        yaml_url.setdefault('obfs', parts[4])
                        yaml_url.setdefault('protocol', parts[2])
                        yaml_url.setdefault('obfsparam', base64_decode(param_dic['obfsparam']))
                        yaml_url.setdefault('protoparam', base64_decode(param_dic['protoparam']))
                        yaml_url.setdefault('group', base64_decode(param_dic['group']))
                        url_list.append(yaml_url)
                    except Exception as err:
                        print(f'yaml_encode 解析 ssr 节点发生错误: {err}')
                        pass
                if 'trojan://' in line:
                    try:
                        url_content = line.replace('trojan://', '')
                        part_list = re.split('#', url_content, maxsplit=1)
                        yaml_url.setdefault('name', urllib.parse.unquote(part_list[1]))
                        server_part = part_list[0].replace('trojan://', '')
                        server_part_list = re.split(':|@|\?|&', server_part)
                        yaml_url.setdefault('server', server_part_list[1])
                        yaml_url.setdefault('port', server_part_list[2])
                        yaml_url.setdefault('type', 'trojan')
                        yaml_url.setdefault('password', server_part_list[0])
                        server_part_list = server_part_list[3:]
                        for config in server_part_list:
                            if 'sni=' in config:
                                yaml_url.setdefault('sni', config[4:])
                            elif 'allowInsecure=' in config or 'tls=' in config:
                                if config[-1] == 0:
                                    yaml_url.setdefault('tls', False)
                            elif 'type=' in config:
                                if config[5:] != 'tcp':
                                    yaml_url.setdefault('network', config[5:])
                            elif 'path=' in config:
                                yaml_url.setdefault('ws-path', config[5:])
                            elif 'security=' in config:
                                if config[9:] != 'tls':
                                    yaml_url.setdefault('tls', False)
                        yaml_url.setdefault('skip-cert-verify', True)
                        url_list.append(yaml_url)
                    except Exception as err:
                        print(f'yaml_encode 解析 trojan 节点发生错误: {err}')
                        pass
            except Exception as e:
                print(f'failed to proccess yaml encoding the raw line: {line} & error: {e}')
        yaml_content_dic = {'proxies': url_list}
        if output:
            yaml_content = yaml.dump(yaml_content_dic, default_flow_style=False, sort_keys=False, allow_unicode=True, width=750, indent=2)
        else:
            yaml_content = yaml_content_dic
        return yaml_content
    except Exception as err:
        print(f'yaml encode error: {err}')


def base64_encode(url_content):
    if url_content is None:
        url_content = ''
    base64_content = base64.b64encode(url_content.encode('utf-8')).decode('ascii')
    return base64_content


def yaml_decode(url_content):
    try:
        if isinstance(url_content, dict):
            sub_content = url_content
        else:
            sub_content = format(url_content)
        print("Formatting Completed!")
        proxies_list = sub_content['proxies']
        protocol_url = []
        for index in range(len(proxies_list)):
            try:
                proxy = proxies_list[index]
                if proxy['type'] == 'vmess':
                    yaml_default_config = {
                        'name': 'Vmess Node', 'server': '0.0.0.0', 'port': 0, 'uuid': '', 'alterId': 0,
                        'cipher': 'auto', 'network': 'ws',
                        'ws-opts': {'path': '', 'headers': {'Host': ''}},
                        'tls': '', 'sni': ''
                    }
                    yaml_default_config.update(proxy)
                    proxy_config = yaml_default_config
                    vmess_value = {
                        'v': 2, 'ps': proxy_config['name'], 'add': proxy_config['server'],
                        'port': proxy_config['port'], 'id': proxy_config['uuid'], 'aid': proxy_config['alterId'],
                        'scy': proxy_config['cipher'], 'net': proxy_config['network'], 'type': None, 'sni': proxy_config['sni']
                    }
                    if 'tls' in proxy:
                        if proxy['tls'] == 'true' or proxy['tls'] is True:
                            vmess_value['tls'] = 'tls'
                    if 'ws-opts' in proxy:
                        if proxy['ws-opts'] is not None and proxy['ws-opts'] != {} and proxy['ws-opts'] != '':
                            if 'headers' in proxy_config['ws-opts']:
                                if proxy_config['ws-opts']['headers']['Host'] != '':
                                    vmess_value['host'] = proxy_config['ws-opts']['headers']['Host']
                            if 'path' in proxy_config['ws-opts']:
                                if proxy_config['ws-opts']['path'] != '':
                                    vmess_value['path'] = proxy_config['ws-opts']['path']
                    vmess_raw_proxy = json.dumps(vmess_value, sort_keys=False, indent=2, ensure_ascii=False)
                    vmess_proxy = str('\nvmess://' + base64_encode(vmess_raw_proxy) + '\n')
                    protocol_url.append(vmess_proxy)
                elif proxy['type'] == 'ss':
                    ss_base64_decoded = str(proxy['cipher']) + ':' + str(proxy['password']) + '@' + str(proxy['server']) + ':' + str(proxy['port'])
                    ss_base64 = base64_encode(ss_base64_decoded)
                    ss_proxy = str('\nss://' + ss_base64 + '#' + str(urllib.parse.quote(proxy['name'])) + '\n')
                    protocol_url.append(ss_proxy)
                elif proxy['type'] == 'trojan':
                    if 'tls' in proxy.keys() and 'network' in proxy.keys():
                        if proxy['tls'] is True and proxy['network'] != 'tcp':
                            network_type = proxy['network']
                            trojan_go = f'?security=tls&type={network_type}&headerType=none'
                        elif proxy['tls'] is False and proxy['network'] != 'tcp':
                            trojan_go = f'??allowInsecure=0&type={network_type}&headerType=none'
                    else:
                        trojan_go = '?allowInsecure=1'
                    if 'sni' in proxy.keys():
                        trojan_go = trojan_go+'&sni='+proxy['sni']
                    trojan_proxy = str('\ntrojan://' + str(proxy['password']) + '@' + str(proxy['server']) + ':' + str(proxy['port']) + trojan_go + '#' + str(urllib.parse.quote(proxy['name'])) + '\n')
                    protocol_url.append(trojan_proxy)
                elif proxy['type'] == 'ssr':
                    remarks = base64_encode(proxy['name']).replace('+', '-')
                    server = proxy['server']
                    port = str(proxy['port'])
                    password = base64_encode(proxy['password'])
                    cipher = proxy['cipher']
                    protocol = proxy['protocol']
                    obfs = proxy['obfs']
                    param_dic = {'group': 'U1NSUHJvdmlkZXI', 'obfsparam': '', 'protoparam': ''}
                    for key in param_dic.keys():
                        try:
                            param_dic.update({key: base64_encode(proxy[key])})
                        except Exception:
                            pass
                    group, obfsparam, protoparam = param_dic['group'], param_dic['obfsparam'], param_dic['protoparam']
                    ssr_proxy = '\nssr://'+base64_encode(server+':'+port+':'+protocol+':'+cipher+':'+obfs+':'+password+'/?group='+group+'&remarks='+remarks+'&obfsparam='+obfsparam+'&protoparam='+protoparam+'\n')
                    protocol_url.append(ssr_proxy)
            except Exception as e:
                print(f'yaml decode Error in coverting servers {e} 错误')
        yaml_content = ''.join(protocol_url)
        yaml_content = list(filter(lambda x: x != '', yaml_content.split("\n")))
        yaml_content = "\n".join(yaml_content)
        return yaml_content
    except Exception as err:
        print(f'yaml decode 发生 {err} 错误')
        return '订阅内容解析错误'


def base64_decode(url_content):
    if '-' in url_content:
        url_content = url_content.replace('-', '+')
    if '_' in url_content:
        url_content = url_content.replace('_', '/')
    missing_padding = len(url_content) % 4
    if missing_padding != 0:
        url_content += '='*(4 - missing_padding)
    try:
        base64_content = base64.b64decode(url_content.encode('utf-8')).decode('utf-8', 'ignore')
        return base64_content
    except UnicodeDecodeError:
        base64_content = base64.b64decode(url_content)
        return str(base64_content)


def convert_remote(url='', output_type='clash', host='http://127.0.0.1:25500'):
    sever_host = host
    url = urllib.parse.quote(url, safe='')
    if output_type == 'clash':
        converted_url = sever_host+'/sub?target=clash&url=' + url+'&insert=false&emoji=true&list=true'
        try:
            resp = requests.get(converted_url)
        except Exception as err:
            print(err)
            return 'Url 解析错误'
        if resp.text == 'No nodes were found!':
            sub_content = 'Url 解析错误'
        else:
            sub_content = makeup(format(resp.text), dup_rm_enabled=False, format_name_enabled=True)
    elif output_type == 'base64':
        converted_url = sever_host+'/sub?target=mixed&url=' + url+'&insert=false&emoji=true&list=true'
        try:
            resp = requests.get(converted_url)
        except Exception as err:
            print(err)
            return 'Url 解析错误'
        if resp.text == 'No nodes were found!':
            sub_content = 'Url 解析错误'
        else:
            sub_content = base64_encode(resp.text)
    elif output_type == 'url':
        converted_url = sever_host+'/sub?target=mixed&url=' + url+'&insert=false&emoji=true&list=true'
        try:
            resp = requests.get(converted_url)
        except Exception as err:
            print(err)
            return 'Url 解析错误'
        if resp.text == 'No nodes were found!':
            sub_content = 'Url 解析错误'
        else:
            sub_content = resp.text
    return sub_content
