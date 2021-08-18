import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pprint import pprint


def get_data(date):
    r = requests.get(
        'https://www.taifex.com.tw/cht/3/futContractsDate?queryDate={}%2F{}%2F{}'
        .format(date.year, date.month,date.day))
    if r.status_code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
    else:
        print('connection error')      
    return soup



def crawl(date):
    soup=get_data(date)
    try:
        table = soup.find('table', class_='table_f')
        while table is None:
            date=date-timedelta(days=1)
            soup=get_data(date)
            table = soup.find('table', class_='table_f')
        trs = table.find_all('tr')
    except Exception:
        print('no data for', date.strftime('%Y/%m/%d'))
        return
    
    print('crawling', date.strftime('%Y/%m/%d'))

    rows = trs[3:-4]
    data = {}
    for row in rows:
        tds = row.find_all('td')
        cells = [td.text.strip() for td in tds]
        headers=row.select('th.left_tit')
        if len(headers)>1:
            products = [title.text.strip() for title in headers[1:]]
        else:
            products=[None]
            products += [title.text.strip() for title in headers]

        row_data = products + cells

        converted = [int(d.replace(',', '')) for d in row_data[2:]]
        row_data = row_data[:2] + converted

        headers = ['商品', '身份別', '交易多方口數', '交易多方金額', '交易空方口數', '交易空方金額', '交易多空淨口數', '交易多空淨額',
                    '未平倉多方口數', '未平倉多方金額', '未平倉空方口數', '未平倉空方金額', '未平倉淨口數', '未平倉多空淨額']

        # product -> who -> what 
        if row_data[0] is not None:
            product = row_data[0]
        who = row_data[1]
        contents = {headers[i]: row_data[i] for i in range(2, len(headers))}
        if product not in data :
            data[product] = {who: contents}
        else:
            data[product][who] = contents

    print(data['臺股期貨']['外資']['未平倉淨口數'])
    return data,date

def main():
    date = datetime.today()
    total_data={}
    while True:
        data,date = crawl(date)
        total_data[date.strftime('%Y/%m/%d')]=data
        date = date - timedelta(days=1)
        if date < datetime.today() - timedelta(days=30):
            break
    pprint(total_data)
if __name__ == "__main__":
    main()


# import pandas as pd
# import  os 
# df=pd.read_html('https://www.taifex.com.tw/cht/3/futContractsDate',
#                 encoding='utf-8',header=[0,1,2])[3]  
# #df.columns
# df_cols=df.columns.tolist()
# df_cols[0]=('','','序號')
# df_cols[1]=('','','商品名稱')
# df_cols[2]=('','','身分別')
# df.columns=pd.MultiIndex.from_tuples(df_cols)
# df.set_index(df.columns[:3].tolist(),inplace=True)
# df.index.names=['序號','商品名稱','身分別']
# os.chdir(r"C:\Users\rober\Desktop")
# #df.to_excel("future.xlsx")
# print(os.getcwd())
# print(df)