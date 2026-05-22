import requests
import urllib.parse
import yaml
import json
import base64
import socket
import geoip2.database


class subs_function:
    def convert_sub(url: str, output: str, convertor_host="http://0.0.0.0:25500", show_url=False, extra_options=""):
        url = urllib.parse.quote(url, safe='')
        try:
            convert_url = f'{convertor_host}/sub?target={output}&url={url}&insert=false&emoji=true&list=true&tfo=false&scv=false&fdn=false&sort=false{extra_options}'
            result = requests.get(convert_url, timeout=240).text
            if show_url:
                print(f"url to host for {output} : {convert_url}")
            if result == "No nodes were found!":
                return "Err: No nodes found"
            return result

        except Exception as e:
            print(e)
            return "Err: failed to parse sub"

    def is_line_valid(line, support_vless=False):
        if (line.startswith("ssr://") or line.startswith("ss://")
                or line.startswith("trojan://") or line.startswith("vmess://")):
            return line

        if(support_vless and line.startswith("vless://")):
            return line

        return ''

    def fix_proxies_name(corresponding_proxies: []):
        emoji = {
            'AD': '🇦🇩', 'AE': '🇦🇪', 'AF': '🇦🇫', 'AG': '🇦🇬',
            'AI': '🇦🇮', 'AL': '🇦🇱', 'AM': '🇦🇲', 'AO': '🇦🇴',
            'AQ': '🇦🇶', 'AR': '🇦🇷', 'AS': '🇦🇸', 'AT': '🇦🇹',
            'AU': '🇦🇺', 'AW': '🇦🇼', 'AX': '🇦🇽', 'AZ': '🇦🇿',
            'BA': '🇧🇦', 'BB': '🇧🇧', 'BD': '🇧🇩', 'BE': '🇧🇪',
            'BF': '🇧🇫', 'BG': '🇧🇬', 'BH': '🇧🇭', 'BI': '🇧🇮',
            'BJ': '🇧🇯', 'BL': '🇧🇱', 'BM': '🇧🇲', 'BN': '🇧🇳',
            'BO': '🇧🇴', 'BQ': '🇧🇶', 'BR': '🇧🇷', 'BS': '🇧🇸',
            'BT': '🇧🇹', 'BV': '🇧🇻', 'BW': '🇧🇼', 'BY': '🇧🇾',
            'BZ': '🇧🇿', 'CA': '🇨🇦', 'CC': '🇨🇨', 'CD': '🇨🇩',
            'CF': '🇨🇫', 'CG': '🇨🇬', 'CH': '🇨🇭', 'CI': '🇨🇮',
            'CK': '🇨🇰', 'CL': '🇨🇱', 'CM': '🇨🇲', 'CN': '🇨🇳',
            'CO': '🇨🇴', 'CR': '🇨🇷', 'CU': '🇨🇺', 'CV': '🇨🇻',
            'CW': '🇨🇼', 'CX': '🇨🇽', 'CY': '🇨🇾', 'CZ': '🇨🇿',
            'DE': '🇩🇪', 'DJ': '🇩🇯', 'DK': '🇩🇰', 'DM': '🇩🇲',
            'DO': '🇩🇴', 'DZ': '🇩🇿', 'EC': '🇪🇨', 'EE': '🇪🇪',
            'EG': '🇪🇬', 'EH': '🇪🇭', 'ER': '🇪🇷', 'ES': '🇪🇸',
            'ET': '🇪🇹', 'EU': '🇪🇺', 'FI': '🇫🇮', 'FJ': '🇫🇯',
            'FK': '🇫🇰', 'FM': '🇫🇲', 'FO': '🇫🇴', 'FR': '🇫🇷',
            'GA': '🇬🇦', 'GB': '🇬🇧', 'GD': '🇬🇩', 'GE': '🇬🇪',
            'GF': '🇬🇫', 'GG': '🇬🇬', 'GH': '🇬🇭', 'GI': '🇬🇮',
            'GL': '🇬🇱', 'GM': '🇬🇲', 'GN': '🇬🇳', 'GP': '🇬🇵',
            'GQ': '🇬🇶', 'GR': '🇬🇷', 'GS': '🇬🇸', 'GT': '🇬🇹',
            'GU': '🇬🇺', 'GW': '🇬🇼', 'GY': '🇬🇾', 'HK': '🇭🇰',
            'HM': '🇭🇲', 'HN': '🇭🇳', 'HR': '🇭🇷', 'HT': '🇭🇹',
            'HU': '🇭🇺', 'ID': '🇮🇩', 'IE': '🇮🇪', 'IL': '🇮🇱',
            'IM': '🇮🇲', 'IN': '🇮🇳', 'IO': '🇮🇴', 'IQ': '🇮🇶',
            'IR': '🇮🇷', 'IS': '🇮🇸', 'IT': '🇮🇹', 'JE': '🇯🇪',
            'JM': '🇯🇲', 'JO': '🇯🇴', 'JP': '🇯🇵', 'KE': '🇰🇪',
            'KG': '🇰🇬', 'KH': '🇰🇭', 'KI': '🇰🇮', 'KM': '🇰🇲',
            'KN': '🇰🇳', 'KP': '🇰🇵', 'KR': '🇰🇷', 'KW': '🇰🇼',
            'KY': '🇰🇾', 'KZ': '🇰🇿', 'LA': '🇱🇦', 'LB': '🇱🇧',
            'LC': '🇱🇨', 'LI': '🇱🇮', 'LK': '🇱🇰', 'LR': '🇱🇷',
            'LS': '🇱🇸', 'LT': '🇱🇹', 'LU': '🇱🇺', 'LV': '🇱🇻',
            'LY': '🇱🇾', 'MA': '🇲🇦', 'MC': '🇲🇨', 'MD': '🇲🇩',
            'ME': '🇲🇪', 'MF': '🇲🇫', 'MG': '🇲🇬', 'MH': '🇲🇭',
            'MK': '🇲🇰', 'ML': '🇲🇱', 'MM': '🇲🇲', 'MN': '🇲🇳',
            'MO': '🇲🇴', 'MP': '🇲🇵', 'MQ': '🇲🇶', 'MR': '🇲🇷',
            'MS': '🇲🇸', 'MT': '🇲🇹', 'MU': '🇲🇺', 'MV': '🇲🇻',
            'MW': '🇲🇼', 'MX': '🇲🇽', 'MY': '🇲🇾', 'MZ': '🇲🇿',
            'NA': '🇳🇦', 'NC': '🇳🇨', 'NE': '🇳🇪', 'NF': '🇳🇫',
            'NG': '🇳🇬', 'NI': '🇳🇮', 'NL': '🇳🇱', 'NO': '🇳🇴',
            'NP': '🇳🇵', 'NR': '🇳🇷', 'NU': '🇳🇺', 'NZ': '🇳🇿',
            'OM': '🇴🇲', 'PA': '🇵🇦', 'PE': '🇵🇪', 'PF': '🇵🇫',
            'PG': '🇵🇬', 'PH': '🇵🇭', 'PK': '🇵🇰', 'PL': '🇵🇱',
            'PM': '🇵🇲', 'PN': '🇵🇳', 'PR': '🇵🇷', 'PS': '🇵🇸',
            'PT': '🇵🇹', 'PW': '🇵🇼', 'PY': '🇵🇾', 'QA': '🇶🇦',
            'RE': '🇷🇪', 'RO': '🇷🇴', 'RS': '🇷🇸', 'RU': '🇷🇺',
            'RW': '🇷🇼', 'SA': '🇸🇦', 'SB': '🇸🇧', 'SC': '🇸🇨',
            'SD': '🇸🇩', 'SE': '🇸🇪', 'SG': '🇸🇬', 'SH': '🇸🇭',
            'SI': '🇸🇮', 'SJ': '🇸🇯', 'SK': '🇸🇰', 'SL': '🇸🇱',
            'SM': '🇸🇲', 'SN': '🇸🇳', 'SO': '🇸🇴', 'SR': '🇸🇷',
            'SS': '🇸🇸', 'ST': '🇸🇹', 'SV': '🇸🇻', 'SX': '🇸🇽',
            'SY': '🇸🇾', 'SZ': '🇸🇿', 'TC': '🇹🇨', 'TD': '🇹🇩',
            'TF': '🇹🇫', 'TG': '🇹🇬', 'TH': '🇹🇭', 'TJ': '🇹🇯',
            'TK': '🇹🇰', 'TL': '🇹🇱', 'TM': '🇹🇲', 'TN': '🇹🇳',
            'TO': '🇹🇴', 'TR': '🇹🇷', 'TT': '🇹🇹', 'TV': '🇹🇻',
            'TW': '🇹🇼', 'TZ': '🇹🇿', 'UA': '🇺🇦', 'UG': '🇺🇬',
            'UM': '🇺🇲', 'US': '🇺🇸', 'UY': '🇺🇾', 'UZ': '🇺🇿',
            'VA': '🇻🇦', 'VC': '🇻🇨', 'VE': '🇻🇪', 'VG': '🇻🇬',
            'VI': '🇻🇮', 'VN': '🇻🇳', 'VU': '🇻🇺', 'WF': '🇼🇫',
            'WS': '🇼🇸', 'XK': '🇽🇰', 'YE': '🇾🇪', 'YT': '🇾🇹',
            'ZA': '🇿🇦', 'ZM': '🇿🇲', 'ZW': '🇿🇼',
            'RELAY': '🏁',
            'NOWHERE': '🇦🇶',
        }
        
        exclude_list_of_countries = ['IL']
        excluded_proxies = []

        for (index, c_proxy) in enumerate(corresponding_proxies):
            try:
                proxy = c_proxy['c_clash']
                if type(proxy) == list and len(proxy) > 0:
                    proxy = proxy[0]

                server = str(proxy.get('server', ''))
                if not server:
                    continue

                if server.replace('.', '').isdigit():
                    ip = server
                else:
                    try:
                        # https://cloud.tencent.com/developer/article/1569841
                        ip = socket.gethostbyname(server)
                    except Exception:
                        ip = server

                country_code = 'NOWHERE'
                try:
                    with geoip2.database.Reader('./utils/Country.mmdb') as ip_reader:
                        response = ip_reader.country(ip)
                        country_code = response.country.iso_code or 'NOWHERE'
                except Exception:
                    pass

                if country_code == 'CLOUDFLARE':
                    country_code = 'RELAY'
                elif country_code == 'PRIVATE':
                    country_code = 'RELAY'
                    
                name_emoji = emoji.get(country_code, emoji['NOWHERE'])

                if len(corresponding_proxies) >= 999:
                    proxy['name'] = f'{name_emoji}{country_code}-{ip}-{index:0>4d}'
                elif len(corresponding_proxies) <= 999 and len(corresponding_proxies) > 99:
                    proxy['name'] = f'{name_emoji}{country_code}-{ip}-{index:0>3d}'
                else:
                    proxy['name'] = f'{name_emoji}{country_code}-{ip}-{index:0>2d}'

                corresponding_proxies[index]["c_clash"] = proxy
                
                if country_code in exclude_list_of_countries or name_emoji == emoji['NOWHERE']:
                    excluded_proxies.append(c_proxy)

            except Exception as e:
                print(f"Error processing proxy at index {index}: {e}")
                continue

        return list(filter(lambda c: c not in excluded_proxies, corresponding_proxies))

    def fix_proxies_duplication(corresponding_proxies: []):
        print("\nBefore was " + str(len(corresponding_proxies)) + "\n")
        begin = 0
        raw_length = len(corresponding_proxies)
        length = len(corresponding_proxies)
        
        while begin < length:
            if (begin + 1) == 1:
                print(f'\n-----Restart-----\nStarting Quantity {length}')
            elif (begin + 1) % 100 == 0:
                print(f'Current Benchmark {begin + 1}-----Current Quantity {length}')
            elif (begin + 1) == length and (begin + 1) % 100 != 0:
                repetition = raw_length - length
                print(f'Current Benchmark {begin + 1}-----Current Quantity {length}\nNumber of Repetition {repetition}\n-----Deduplication Completed-----\n')

            try:
                proxy_compared = corresponding_proxies[begin]["c_clash"]
                if type(proxy_compared) == list and len(proxy_compared) > 0:
                    proxy_compared = proxy_compared[0]
                if not isinstance(proxy_compared, dict):
                    begin += 1
                    continue

                begin_2 = begin + 1
                while begin_2 < length:
                    check = False
                    try:
                        correspond_next_proxy = corresponding_proxies[begin_2]["c_clash"]
                        if type(correspond_next_proxy) == list and len(correspond_next_proxy) > 0:
                            correspond_next_proxy = correspond_next_proxy[0]
                        if not isinstance(correspond_next_proxy, dict):
                            begin_2 += 1
                            continue

                        if proxy_compared.get('server') == correspond_next_proxy.get('server') and proxy_compared.get('port') == correspond_next_proxy.get('port'):
                            check = True
                            if 'net' in correspond_next_proxy and 'net' in proxy_compared:
                                if proxy_compared['net'] != correspond_next_proxy['net']:
                                    check = False

                            if 'tls' in correspond_next_proxy and 'tls' in proxy_compared:
                                if proxy_compared['tls'] != correspond_next_proxy['tls']:
                                    check = False

                            if 'ws-opts' in correspond_next_proxy and 'ws-opts' in proxy_compared:
                                if str(proxy_compared['ws-opts']) != str(correspond_next_proxy['ws-opts']):
                                    check = False

                            if 'cipher' in correspond_next_proxy and 'cipher' in proxy_compared:
                                if proxy_compared['cipher'] != correspond_next_proxy['cipher']:
                                    check = False

                            if 'type' in correspond_next_proxy and 'type' in proxy_compared:
                                if proxy_compared['type'] != correspond_next_proxy['type']:
                                    check = False

                            if 'network' in correspond_next_proxy and 'network' in proxy_compared:
                                if proxy_compared['network'] != correspond_next_proxy['network']:
                                    check = False

                            if 'obfs' in correspond_next_proxy and 'obfs' in proxy_compared:
                                if proxy_compared['obfs'] != correspond_next_proxy['obfs']:
                                    check = False

                        if check:
                            corresponding_proxies.pop(begin_2)
                            length -= 1
                        else:
                            begin_2 += 1

                    except Exception as e:
                        print(f"Error comparing proxies at {begin_2}: {e}")
                        begin_2 += 1

            except Exception as e:
                print(f"Error processing proxy at {begin}: {e}")

            begin += 1

        print("\nNow is " + str(len(corresponding_proxies)) + "\n")
        return corresponding_proxies
