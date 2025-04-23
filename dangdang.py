import requests
from lxml import etree
import time
import random

def DangdangSpider(isbn_list):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Referer": "https://search.dangdang.com/?key=9787040599008&act=input&page_index=2",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
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
        "__visit_id": "20250422153114847502035681658706764",
        "__out_refer": "",
        "dest_area": "country_id%3D9000%26province_id%3D111%26city_id%3D0%26district_id%3D0%26town_id%3D0",
        "search_passback": "c9310953d79c7d1d384c0768fc01000013d86400ab4b0768",
        "pos_9_end": "1745308731719",
        "ad_ids": "88943820%2C5442774%2C88943806%7C%233%2C3%2C2",
        "__rpm": "s_112100.155956512835%2C155956512836..1745308729665%7Cs_112100.155956512835%2C155956512836..1745308734643",
        "__trace_id": "20250422155854695343046658488955020"
    }
    url = "https://search.dangdang.com/"
    params = {
        "key": f"{isbn_list}",
        "act": "input",
        "page_index": "1"
    }
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    tree = etree.HTML(response.text)
    
    books_li = tree.xpath('//div[@id="search_nature_rg"]//ul/li')
    books_data = []
    
    for li in books_li:
        # 书名
        title = li.xpath('./a/@title')
        # 国际标准书号
        isbn = isbn_list
        # 作者
        author = li.xpath('./p[@class="search_book_author"]/span[1]/text()')
        # 出版社
        publisher = li.xpath('.//p[@class="search_book_author"]//text()')
        # 平台
        source = '当当'
        # 成色
        quality = '二手'
        if '全新' in title:quality = '全新'
        # 卖价
        current_price = tree.xpath('./p[@class="price"]/span[@class="search_now_price"]//text()')
        # 书籍链接
        book_url = li.xpath('.//a/@href')
        
        # 构建字典
        book_info = {
            'title': title,
            'ISBN': isbn,
            'author': author,
            'publisher': publisher,
            'source': source,
            'quality': quality,
            'current_price': current_price,
            'book_url': book_url
        }
        books_data.append(book_info)
    
    return books_data

if __name__ == "__main__":
    isbn = [9787040599008]
    for idx, isbn in enumerate(isbn, 1):
        try:
            print(f"\n正在处理第 {idx}个ISBN: {isbn}")
            books_data = DangdangSpider([isbn])
            if books_data:
                print(f"成功获取 {len(books_data)} 条数据")
                print(books_data[0])
            time.sleep(2 + random.random()*3)
        except Exception as e:
            print(f"处理ISBN {isbn} 时发生异常：{str(e)}")
            # 记录失败ISBN到日志文件
            with open("failed_isbns.log", "a") as f:
                f.write(f"{isbn}\n")
        continue
    print("所有ISBN处理完成")