# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 02:35:47 2021

@author: rober
"""
from pprint import pprint
import re
from collections import defaultdict
import time as t
import json
from concurrent import futures
import os


import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs


def crawl_post(url):
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        raise SystemExit  # 結束程式

    soup = bs(r.text, 'html.parser')

    script = soup.find('script', id='__NEXT_DATA__')
    d = json.loads(script.string)
    # pprint(d)

    post_id = url.split('/')[-1].strip()
    post_data = d['props']['initialState']['post']['data'][post_id]
    print('作者:', post_data['authorName']['message'])
    print('建立時間:', post_data['mediaMeta'][0]['createdAt'])
    article = post_data['content'].replace('\r', "").split('\n')
    article = "\n".join(article)
    print('文章內容:', article)
    print('心情數:', post_data['reactionCount'])
    print('文章關鍵字:', post_data['topics'])
    comment_count = post_data['commentCount']
    return comment_count


def comment123(com_url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'referer': 'https://www.dcard.tw/', 'accept-encoding': 'gzip, deflate, br'}
    com_resp = requests.get(com_url, headers=headers)
    if com_resp.status_code == 200:
        print('連線成功')
    else:
        print('連線失敗')
        return
    soup = bs(com_resp.text, 'html.parser')
    script = soup.select_one('script#__NEXT_DATA__')
    d = json.loads(script.string)
    comment_data = d['props']['initialState']['comment']['data']
    comment_data = comment_data[list(comment_data.keys())[0]]
    try:
        comment = comment_data['content']
        like_count = comment_data['likeCount']
        school = comment_data['school']
        if re.search('.{2,}(大學)$', school) is None:
            school = None
        time = soup.select("span.pi0hc4-2.eCtXmy span")[-1].text
    except:
        print('此則留言已被刪除')
        return
    t.sleep(1.5)
    return comment, like_count, school, time


def crawl_comment(url, comment_count):
    com_dict = {}
    com_url_list = []
    like_count_list = []
    qualified_post = 0
    start = t.time()
    for page in range(1, comment_count + 1):
        com_url = url + '/b/' + str(page)
        com_url_list.append(com_url)
    with futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(comment123, com_url_list)
        for result in results:
            if result:
                comment, like_count, school, time = result
                if school:
                    like_count_list.append(like_count)
                    if school not in com_dict:
                        com_dict[school] = {}
                        com_dict[school][time] = [comment]
                    else:
                        if time not in com_dict[school]:
                            com_dict[school][time] = [comment]
                        else:
                            com_dict[school][time].append(comment)
                    qualified_post += 1
            else:
                continue
    end = t.time()
    print(f'下載資料共花費{end - start}秒')
    print('擁有完整學校名稱共{}則留言'.format(qualified_post))
    ##pprint(com_dict) 
    return com_dict, like_count_list


def sorted_time_series(x):
    if '天' in x:
        x = int(x.replace('天前', ''))
        return x * 24 * 60
    elif '小時' in x:
        x = int(x.replace('小時前', ''))
        return x * 60
    elif '分鐘' in x:
        x = int(x.replace('分鐘前', ''))
        return x
    else:
        return 0


def make_dataframe(com_dict, like_count):
    d = []
    for school in com_dict:
        sum_ = 0
        for comm in com_dict[school].values():
            sum_ += len(comm)
        d.append([school, sum_])

    df_com = pd.DataFrame(d, columns=['學校', '留言總數'])
    # print(df_com)

    d_bar = defaultdict(int)
    for times in com_dict.values():
        for times, comm in times.items():
            d_bar[times] += len(comm)

    # pprint(dict(d_bar))
    d1 = list(zip(d_bar.keys(), d_bar.values()))

    df_time = pd.DataFrame(d1, columns=['留言時間', '留言數'])
    time_like_total = []
    com_list = df_time['留言數'].values.tolist()
    for i in com_list:
        time_like_total.append(sum(like_count[:i]))
        like_count = like_count[i:]

    df_time['按讚數'] = time_like_total

    df_time['時間排序'] = df_time['留言時間'].apply(sorted_time_series)
    df_time.sort_values(by='時間排序', ascending=False, inplace=True)

    return df_com, df_time


def visualization(df_com, df_time):
    pio.renderers.default = 'browser'
    pie = px.pie(df_com, names='學校', values='留言總數', hover_name='學校', color='學校')
    pie.update_traces(textposition='inside', textinfo='percent+label',
                      insidetextfont=dict(size=df_com['留言總數'].values * 10, color='white'),
                      insidetextorientation="radial",
                      marker=dict(line=dict(color='#000000', width=.4)),
                      pull=[0.2 if x == df_com['留言總數'].idxmax() else 0 for x in range(df_com['學校'].nunique())],
                      opacity=0.7, rotation=180)
    pie.update_layout(title={'font': {'family': 'Courier New', 'size': 40}, 'text': '學校留言百分佔比',
                             'x': 0.46, 'y': .95, 'xanchor': 'center', 'yanchor': 'top'},
                      uniformtext_minsize=8, uniformtext_mode='hide',
                      )
    pie.show()

    bar = px.bar(df_time,
                 x='留言時間', y=['留言數', '按讚數'],
                 barmode='group', opacity=0.9,
                 template='ggplot2', log_y=True,
                 hover_name='留言時間',
                 color_discrete_sequence=px.colors.sequential.Plasma,
                 labels={'value': '數量', 'variable': '數量'},
                 category_orders={'留言時間': df_time['留言時間'].values}
                 )

    bar.update_layout(title={'font': {'family': 'Courier New', 'size': 40}, 'text': '留言時間長條圖',
                             'x': 0.5, 'y': .98, 'xanchor': 'center', 'yanchor': 'top'},
                      )

    bar.show()

##使用多線程(4)爬取(約150秒)
def main():
    url = 'https://www.dcard.tw/f/mood/p/236759860'  ##you can change the dcard's url you want to crawl
    comment_count = crawl_post(url)
    # tmp=crawl_comment(url,comment_count)
    # print(tmp)
    com_dict, like_count = crawl_comment(url, comment_count)
    if com_dict and like_count:
        df_com, df_time = make_dataframe(com_dict, like_count)
        visualization(df_com, df_time)
    else:
        print('連接伺服器無法取得回應')


if __name__ == "__main__":
    main()
    
    
def crawl_post(url):  
    r = requests.get(url)
    if r.status_code != requests.codes.ok:
          raise SystemExit # 結束程式
        
    soup = bs(r.text, 'html.parser')
        
    script = soup.find('script', id='__NEXT_DATA__')
    d = json.loads(script.string) 
    #pprint(d) 
    
    post_id=url.split('/')[-1].strip()   
    post_data = d['props']['initialState']['post']['data'][post_id] 
    print('作者:',post_data['authorName']['message'])
    print('建立時間:',post_data['mediaMeta'][0]['createdAt']) 
    article=post_data['content'].replace('\r',"").split('\n') 
    article="\n".join(article)
    print('文章內容:',article)  
    print('心情數 :',post_data['reactionCount']) 
    print('文章關鍵字:',post_data['topics'])
    comment_count =post_data['commentCount']
    return comment_count
    

def crawl_comment(url,comment_count):
    com_dict={}
    like_count=[]
    headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
              'referer': 'https://www.dcard.tw/','accept-encoding': 'gzip, deflate, br'}
    qualified_post=0
    start=t.time()
    for page in range(1, comment_count+1):
        com_resp=requests.get('{}/b/{}'.format(url,page),headers=headers)
        if com_resp.status_code == 200:
            print('連線成功')
            print('正在爬第{}則留言'.format(page))
        else:
            print('連線失敗')
            break
            
        soup=bs(com_resp.text,'html.parser')
        script = soup.select_one('script#__NEXT_DATA__')
        d = json.loads(script.string)
        comment_data = d['props']['initialState']['comment']['data']
        comment_data=comment_data[list(comment_data.keys())[0]]
        try:
            comment = comment_data['content']
            like_count.append(comment_data['likeCount'])
            school=comment_data['school']
            if re.search('.{2,}(大學)$', school) is None:
                school=None
            time=soup.select("span.pi0hc4-2.eCtXmy span")[-1].text
        except:
            print('此則留言已被刪除')
            continue
        if school:
            if school not in com_dict:
                com_dict[school]={}
                com_dict[school][time]=[comment]
            else:
                if time not in com_dict[school]:
                    com_dict[school][time]=[comment]
                else:
                    com_dict[school][time].append(comment)
            qualified_post+=1 
    end=t.time()
    print(f'下載資料共花費{end - start}秒')                      
    print('擁有完整學校名稱共{}則留言'.format(qualified_post))  
    ##pprint(com_dict) 
    return com_dict , like_count


def sorted_time_series(x):
    if '天' in x:
        x=int(x.replace('天前',''))
        return x*24*60
    elif '小時' in x:
        x=int(x.replace('小時前',''))
        return x*60
    elif '分鐘' in x:
        x=int(x.replace('分鐘前',''))
        return x
    else:
        return 0

               
def make_dataframe(com_dict,like_count):
    d=[] 
    for school in com_dict:
        sum_=0
        for comm in com_dict[school].values():
            sum_+=len(comm)
        d.append([school,sum_])    
           
    
    df_com=pd.DataFrame(d,columns=['學校','留言總數'])
    #print(df_com)
    
    
    d_bar=defaultdict(int)
    for times in com_dict.values():
        for times,comm in times.items():
            d_bar[times]+=len(comm)
            
    #pprint(dict(d_bar))
    d1=list(zip(d_bar.keys(),d_bar.values()))
    
    df_time=pd.DataFrame(d1,columns=['留言時間','留言數'])
    time_like_total=[]
    com_list=df_time['留言數'].values.tolist()
    for i in com_list:
        time_like_total.append(sum(like_count[:i]))
        like_count=like_count[i:]
        
    df_time['按讚數']=time_like_total
    
    df_time['時間排序']=df_time['留言時間'].apply(sorted_time_series)
    df_time.sort_values(by='時間排序',ascending=False,inplace=True)
    
    return df_com,df_time


def visualization(df_com,df_time):
    pio.renderers.default = 'browser'
    pie=px.pie(df_com,names='學校',values='留言總數',hover_name='學校',color='學校')
    pie.update_traces(textposition='inside', textinfo='percent+label',insidetextfont=dict(size=df_com['留言總數'].values*10,color='white'),
                      insidetextorientation="radial",
                            marker=dict(line=dict(color='#000000', width=.4)),
                            pull=[0.2 if x == df_com['留言總數'].idxmax() else 0 for x in range(df_com['學校'].nunique())], 
                            opacity=0.7, rotation=180)
    pie.update_layout(title={'font':{'family':'Courier New','size':40},'text':'學校留言百分佔比',
                              'x':0.46,'y':.95,'xanchor':'center','yanchor':'top'},
                              uniformtext_minsize=10, uniformtext_mode='hide',
                              )
    pie.show()   
     
          
    bar=px.bar(df_time,
                x='留言時間',y=['留言數','按讚數'],
                barmode='group',opacity=0.9,
                template='ggplot2',log_y=True,
                hover_name='留言時間',
                color_discrete_sequence= px.colors.sequential.Plasma,
                labels={'value':'數量','variable':'數量'},
                category_orders={'留言時間':df_time['留言時間'].values}
                )
    
    bar.update_layout(title={'font':{'family':'Courier New','size':40},'text':'留言時間長條圖',
                              'x':0.5,'y':.98,'xanchor':'center','yanchor':'top'},
                              )
    
    bar.show()
    
##使用一般方法爬取(約250秒)
def main():
    url='https://www.dcard.tw/f/mood/p/236759860 ' ##you can change the dcard's url you want to crawl 
    comment_count=crawl_post(url)
    com_dict,like_count=crawl_comment(url,comment_count)
    if com_dict and like_count:
        df_com,df_time=make_dataframe(com_dict,like_count)
        visualization(df_com, df_time)
    else:
        print('連接伺服器無法取得回應')

if __name__ == "__main__":
    main()
