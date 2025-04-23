import requests
import json
import time
import random

def KongfzSpider(isbn_list):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Referer": "https://search.kongfz.com/product/latest?sortType=0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Origin": "https://search.kongfz.com",
        "Host": "search.kongfz.com",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    cookies = {
        "shoppingCartSessionId": "ccb4f79c59c97ca01dc73ba3b42218cd",
        "reciever_area": "1001000000",
        "kfz_uuid": "b823309d-53d2-414d-83ac-64f4c05fa486",
        "_c_WBKFRo": "BF8PE7AgK0CJTRvK1OxlcGvw9BwdMoNKrMgWNHhd",
        "PHPSESSID": "d78f661531be37a441df2322bbd510252a448086",
        "kfz_trace": "b823309d-53d2-414d-83ac-64f4c05fa486|22667454|2856f83c9fb75f2e|-",
        "_c_WBKFRo": "BF8PE7AgK0CJTRvK1OxlcGvw9BwdMoNKrMgWNHhd",
        "acw_tc": "1a0c651417448088497707101e00d7481fa4a908c959f6729883c2f6b242ce"
    }
    user_agents = [
        # Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0",
        # Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        # 移动端
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    ]
    url = "https://search.kongfz.com/pc-gw/search-web/client/pc/product/keyword/list"
    
    def get_random_user_agent():return random.choice(user_agents)

    # 创建session对象
    session = requests.Session()
    session.headers.update({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    
    # 每次请求前更新 User-Agent
    session.headers["User-Agent"] = get_random_user_agent()
    session.cookies.update(cookies)
    
    # 定义翻页变量
    total_found = 0
    current_page = 1
    page_size = 50
    books_data = []  # 用于存储所有书籍信息的列表
    
    # 抓取书籍详情信息
    try:
        while True:
            params = {
                "keyword": f"{isbn_list}",
                "userArea": "1001000000",
                "_": int(time.time() * 1000),
                "currentPage": current_page,
                "pageSize": page_size,
                "rand": random.randint(1000, 9999)
            }
            
            response = session.get(url, params=params)
            response.raise_for_status()# 检查请求是否成功
            data = response.json()
            # 判断响应是否成功
            if data.get('status') != 1:
                print(f"请求第{current_page}页失败:", data.get('message'))
                break
            
            # 数据在嵌套json下的item_response中
            item_response = data.get('data', {}).get('itemResponse', {})
            # 详情书籍列表
            book_list = item_response.get('list', [])
            # 只在第一页获取总记录数
            if current_page == 1:
                total_found = item_response.get('total', 0)
                if (total_found % 50) == 0: pages = (total_found//50)
                else:pages = (total_found//50)+1   
                print(f"ISBN: {isbn_list} 共找到 {total_found} 条记录，需要抓取 {pages} 页")
            
            
            # 提取所需要的字段
            for item in book_list:
                if isinstance(item, dict):
                    book_info = {
                        # 书名
                        'title' : item.get('title'),
                        # 国际标准书号
                        'isbn' : item.get('isbn'),
                        # 作者
                        'author' : item.get('author'),
                        # 出版社
                        'publisher' : item.get('press'),
                        # 平台
                        'source' : '孔夫子',
                        # 成色
                        'quality' : item.get('qualityText'),
                        # 卖价
                        'current_price' : item.get('price'),
                        # 书籍链接
                        'book_url': item.get('link').get('pc')
                    }
                    books_data.append(book_info)
                else:
                    print(f"异常数据结构: {type(item)}")
            
            # 终止条件判断
            pages = 1# 测试
            if current_page == pages:
                # 最后一页的实际数据量 = 总记录数 - (页数-1)*每页数量
                actual_size = total_found - (pages - 1) * page_size
                book_list = book_list[:actual_size]  # 截取有效数据
                break
            
            print(f"正在处理第{current_page}/{pages}页，本页获取到{len(book_list)}条")
            current_page += 1
            
            # 添加随机延迟防止封禁
            time.sleep(60 + random.random()*10)

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP 请求错误: {http_err}')
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
    except Exception as e:
        print(f"发生其他错误: {e}")
    finally:response.close()
    
    return books_data


if __name__ == "__main__":
    isbn = [9787040599008,9787040599039]
    for idx, isbn in enumerate(isbn, 1):
        try:
            print(f"\n正在处理第 {idx}个ISBN: {isbn}")
            books_data = KongfzSpider([isbn])
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