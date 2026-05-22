def update_airports(id, current_url):
    if id == 5:
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=2))
        s.mount('https://', HTTPAdapter(max_retries=2))
        urllist = []
        # Вот они — проверенные источники бесплатных узлов
        sources = [
            "https://raw.githubusercontent.com/RenaLio/Mux2sub/main/urllist",
            "https://raw.githubusercontent.com/RenaLio/Mux2sub/main/sub_list",
            "https://raw.githubusercontent.com/rxsweet/getAirport/main/config/sublist_free",
            "https://raw.githubusercontent.com/rxsweet/getAirport/main/config/sublist_mining",
            "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
            "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"
        ]
        for src in sources:
            try:
                res = s.get(src, timeout=5)
                if res.status_code == 200:
                    lines = [x.strip() for x in res.text.splitlines() if x.strip().startswith("http")]
                    urllist.extend(lines)
            except:
                continue
        if urllist:
            new_url = "|".join(list(set(urllist)))
            return new_url
    return current_url
