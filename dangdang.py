import requests


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
cookies = {
    "__permanent_id": "20250412185859725127644401998218453",
    "ddscreen": "2",
    "__visit_id": "20250419222156354173096147350234471",
    "__out_refer": "",
    "dest_area": "country_id%3D9000%26province_id%3D111%26city_id%3D0%26district_id%3D0%26town_id%3D0",
    "__rpm": "s_112100...1745072540760%7Cmix_65152...1745072545256",
    "search_passback": "c9310953d79c7d1da0b10368fc010000a578650020b10368",
    "__trace_id": "20250419222225800646834355542894243",
    "pos_9_end": "1745072546093",
    "ad_ids": "5442774%2C88943820%2C88943806%7C%232%2C2%2C1"
}
url = "https://search.dangdang.com/"
params = {
    "key": "9787040599008",
    "act": "input"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)