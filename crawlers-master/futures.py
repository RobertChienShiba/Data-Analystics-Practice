from datetime import datetime, timedelta
from pprint import pprint
import os
import json
from concurrent import futures
import time
import shutil

import requests
from bs4 import BeautifulSoup


def get_data(date):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'accept-encoding': 'gzip, deflate, br', 'Connection': 'keep-alive'}
    r = requests.get(
        'https://www.taifex.com.tw/cht/3/futContractsDate?queryDate={}%2F{}%2F{}'
            .format(date.year, date.month, date.day), headers=headers)
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
    else:
        print('connection error')
    return soup


def crawl(date):
    soup = get_data(date)
    print('crawling', date.strftime('%Y/%m/%d'))
    try:
        table = soup.find('table', class_='table_f')
        trs = table.find_all('tr')
    except Exception:
        print('no data for', date.strftime('%Y/%m/%d'))

    rows = trs[3:]
    data = {}
    for row in rows:
        ths = row.find_all('th')
        titles = [th.text.strip() for th in ths]

        if titles[0] == '期貨小計':
            break

        if len(titles) == 3:
            product = titles[1]
            who = titles[2]
        else:
            who = titles[0]
        tds = row.find_all('td')
        cells = [td.text.strip() for td in tds]

        row_data = [product, who] + cells

        converted = [int(d.replace(',', '')) for d in row_data[2:]]
        row_data = row_data[:2] + converted

        headers = ['商品', '身份別', '交易多方口數', '交易多方金額', '交易空方口數', '交易空方金額', '交易淨口數', '交易淨金額',
                   '未平倉多方口數', '未平倉多方金額', '未平倉空方口數', '未平倉空方金額', '未平倉淨口數', '未平倉淨金額']

        # product -> who -> what
        product = row_data[0]
        who = row_data[1]
        contents = {headers[i]: row_data[i] for i in range(2, len(headers))}

        if product not in data:
            data[product] = {who: contents}
        else:
            data[product][who] = contents

    write_to_file(data, date)


def write_to_file(data, date):
    date_str = date.strftime("%Y%m%d")
    path = os.path.join('futures', f'{date_str}.json')
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def process_with_thread(date):
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.submit(crawl, date)


def file_exist(date):
    date_str = date.strftime("%Y%m%d")
    path = os.path.join('futures', f'{date_str}.json')
    return os.path.exists(path) and os.path.getsize(path) > 0


###使用多進程(8個)+多線程(10)爬期貨資料
def main():
    date = datetime.today()
    os.makedirs('futures', exist_ok=True)
    start = time.time()
    with futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        while True:
            while file_exist(date):
                print(f'{date.strftime("%Y%m%d")} file has already existed')
                date = date - timedelta(days=1)
            executor.submit(process_with_thread, date)
            date = date - timedelta(days=1)
            if date < datetime.today() - timedelta(days=730):
                break
    end = time.time()
    print(f'下載資料共花費{end - start}秒')


if __name__ == "__main__":
    main()

###像這種表格類型的資料(table標籤)也可以使用pandas來獲得(以2021/8/12為例)
import pandas as pd
import  os
df=pd.read_html('https://www.taifex.com.tw/cht/3/futContractsDate',
                encoding='utf-8',header=[0,1,2])[3]
#df.columns
df_cols=df.columns.tolist()
df_cols[0]=('','','序號')
df_cols[1]=('','','商品名稱')
df_cols[2]=('','','身分別')
df.columns=pd.MultiIndex.from_tuples(df_cols)
df.set_index(df.columns[:3].tolist(),inplace=True)
df.index.names=['序號','商品名稱','身分別']
os.chdir(r"C:\Users\rober\Desktop")
#df.to_excel("future.xlsx")
print(os.getcwd())
print(df)


def crawl(date):
    soup = get_data(date)
    print('crawling', date.strftime('%Y/%m/%d'))
    try:
        table = soup.find('table', class_='table_f')
        trs = table.find_all('tr')
    except Exception:
        print('no data for', date.strftime('%Y/%m/%d'))
        return
    rows = trs[3:]
    data = {}
    for row in rows:
        ths = row.find_all('th')
        titles = [th.text.strip() for th in ths]

        if titles[0] == '期貨小計':
            break

        if len(titles) == 3:
            product = titles[1]
            who = titles[2]
        else:
            who = titles[0]
        tds = row.find_all('td')
        cells = [td.text.strip() for td in tds]

        row_data = [product, who] + cells

        converted = [int(d.replace(',', '')) for d in row_data[2:]]
        row_data = row_data[:2] + converted

        headers = ['商品', '身份別', '交易多方口數', '交易多方金額', '交易空方口數', '交易空方金額', '交易淨口數', '交易淨金額',
                   '未平倉多方口數', '未平倉多方金額', '未平倉空方口數', '未平倉空方金額', '未平倉淨口數', '未平倉淨金額']

        # product -> who -> what
        product = row_data[0]
        who = row_data[1]
        contents = {headers[i]: row_data[i] for i in range(2, len(headers))}

        if product not in data:
            data[product] = {who: contents}
        else:
            data[product][who] = contents

        write_to_file(data, date)

###使用一般方法爬期貨資料
def main():
    date = datetime.today()
    os.makedirs('futures', exist_ok=True)
    start = time.time()
    while True:
        while file_exist(date):
            print(f'{date.strftime("%Y%m%d")} file has already existed')
            date = date - timedelta(days=1)
        crawl(date)
        date = date - timedelta(days=1)
        if date < datetime.today() - timedelta(days=730):
            break
    end = time.time()
    print(f'下載資料共花費{end - start}秒')


if __name__ == "__main__":
    main()
