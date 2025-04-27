import requests
from bs4 import BeautifulSoup
import pymysql
import sqlite3
import time
import random
from Kongfz import KongfzSpider
from dangdang import DangdangSpider


# 读取专业表的ISBN
def readisbn():
    import pymysql

    # 连接数据库
    try:
        conn = pymysql.connect(**conf)
        cursor = conn.cursor()
        # 执行SQL查询语句
        sql = "select major.ISBN FROM major WHERE major != '思想政治教育类'"
        # "select major.ISBN FROM major WHERE NOT EXISTS( SELECT books.ISBN from books WHERE major.ISBN = books.ISBN group by ISBN);"
        cursor.execute(sql)

        # 获取查询结果
        results = cursor.fetchall()
        return results

    except Exception as e:
        conn.rollback()
        print("读取失败:", e)
    
    # 关闭游标和连接
    cursor.close()
    conn.close()


# 数据入库函数
def save_to_db(books_data):
    try:
        conn = pymysql.connect(**conf)
        cursor = conn.cursor()
        
        # 数据预处理
        for book in books_data:
            # 字段映射与转换
            book['title'] = book.get('title')
            book['ISBN'] = book.get('isbn')
            book['author'] = book.get('author') or '未知作者'
            book['publisher'] = book.get('publisher') or '未知出版社'
            book['source'] = book.get('source')
            book['quality'] = book.get('quality')
            book['current_price'] = book.get('current_price')
            book['book_url'] = book.get('book_url')
        
        
        books_data_transformed = []
        for book in books_data:
            # 确保字段顺序和 SQL 语句里占位符的顺序一致
            book_tuple = (
                book['title'],
                book['ISBN'],
                book['author'],
                book['publisher'],
                book['source'],
                book['quality'],
                book['current_price'],
                book['book_url']
            )
            books_data_transformed.append(book_tuple)
        # print(books_data_transformed)
        
        # 使用UPSERT语法实现去重更新
        insert_sql = """
        INSERT INTO books (
            title, ISBN, author, publisher, source, quality, current_price, book_url
        ) VALUES (
            %s, %s, %s, %s, %s, %s,%s, %s
        )
        ON DUPLICATE KEY UPDATE
            current_price = VALUES(current_price),
            update_time = CURRENT_TIMESTAMP,
            use_flag = 0
        """

        # 批量执行
        cursor.executemany(insert_sql, books_data_transformed)
        conn.commit()
        print(f"成功入库/更新 {len(books_data)} 条数据")

    except sqlite3.Error as e:  # 根据实际数据库调整异常类型
        print(f"数据库错误: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    conf = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root123",
    "database": "graduation_project"
    }
    
    ISBN_tuple = readisbn()
    # 将ISBN填入到一个列表当中
    if ISBN_tuple:ISBN_list = [item[0] for item in ISBN_tuple]
    
    test_isbn_list =[9787040599008]#test
    
    
    # 遍历每个ISBN进行爬取
    for idx, isbn in enumerate(ISBN_list, 1):
        try:
            print(f"\n正在处理第 {idx}/{len(ISBN_list)} 个ISBN:{isbn}")
            
            # 调用孔夫子爬虫
            # books_data = KongfzSpider([isbn])
            
            # # 调用当当爬虫
            books_data = DangdangSpider(str(isbn))
            
            if books_data:
                print(f"成功获取 {len(books_data)} 条数据")
                save_to_db(books_data)
                print(f"已入库 {idx}/{len(ISBN_list)} 个ISBN的数据")
            
            # 添加延迟
            time.sleep(2 + random.random()*4)
            
        except Exception as e:
            print(f"处理ISBN {isbn} 时发生异常：{str(e)}")
            # 记录失败ISBN到日志文件
            with open("failed_isbns.log", "a") as f:
                f.write(f"{isbn}\n")
            continue
    
    
    print("所有ISBN处理完成!")


# 定价规则