# -*- coding: utf-8 -*-
"""
@author: rober
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd



def search(search_name,headers):
    url="https://www.imdb.com/find"
    #headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"}
    QSP={"q": search_name,
    "ref_": "nv_sr_sm"}
    
    response=requests.get(url,headers=headers,params=QSP)
    soup=BeautifulSoup(response.text,"lxml")
    movie_url=soup.select("#findSubHeader+ .findSection .result_text a")[0].get("href")
    movie_url="https://www.imdb.com/"+movie_url
    return movie_url


def get_movie_data(search_name,headers):
    try:
        movie_url=search(search_name,headers)
        response=requests.get(movie_url,headers=headers)
        response_text=response.text   
        soup=BeautifulSoup(response_text,"lxml")
   
        movie_title=soup.select("h1")[0].text.strip().replace("\xa0","")
        movie_poster="https://www.imdb.com"+soup.find_all("a",class_="ipc-lockup-overlay ipc-focusable")[0].get("href")
        movie_rating=soup.find_all("span",class_="AggregateRatingButton__RatingScore-sc-1ll29m0-1 iTLWoV")[0].text.strip()
        movie_genre=[i.text.strip()for i in soup.find_all("span",class_="ipc-chip__text",limit=3)]
        movie_release_date=[i.text.strip()for i in soup.find_all("li",role="presentation",limit=3)][0][:4]
        length_of_movie=[i.text.strip()for i in soup.find_all("li",role="presentation",limit=3)][2]
        movie_character=[i.text.strip()for i in soup.find_all("a", class_="StyledComponents__ActorName-y9ygcu-1 eyqFnv")]
        movie_video= ["https://www.imdb.com"+i.get("href")for i in soup.find_all("a",class_="ipc-lockup-overlay ipc-focusable")if i.get("href").startswith("/video")]
        movie_info={
                 "片名":[movie_title]*len(movie_character),
                 "電影海報":[movie_poster]*len(movie_character),
                 "電影評分":[movie_rating]*len(movie_character),
                 "上映日期":[movie_release_date]*len(movie_character),
                 "電影類型":[movie_genre[0]]*len(movie_character),
                 "片長":[length_of_movie]*len(movie_character),
                 "演員名單":movie_character,
                 "預告片1":[movie_video[0]]*len(movie_character),
                 } 
        return movie_info
    except IndexError:
         print("在擷取電影發生錯誤!")


def main():
    url="https://www.fantasy-sky.com/ContentList.aspx"
    cookies={"COOKIE_LANGUAGE":"en"}
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"}
    movie_name=[]
    df_movie=pd.DataFrame()
    for i in range(1,5):
        QSP={"section": "002", 
             "category": "0020{}".format(i)}
        response=requests.get(url,cookies=cookies,headers=headers,params=QSP)
        data=response.text
        soup=BeautifulSoup(data,"lxml")
        movie_name+=[i.text for i in soup.select(".movies-name")]
    for name in movie_name:
        if get_movie_data(name,headers)is not None: 
            movie=get_movie_data(name,headers)
            print(f"正在擷取{movie['片名'][0]}")
            df_movie=pd.concat([df_movie,pd.DataFrame(movie)],ignore_index=True)
    df_movie.sort_values(by=["電影評分","上映日期"],ascending=[False,False],inplace=True)
    #print(df_movie.head(30))
    df_movie.to_csv("movie.csv",index=False,encoding="utf_8_sig")
    
if __name__ == "__main__":
    main()


