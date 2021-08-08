# -*- coding: utf-8 -*-
"""
@author: rober
"""
import pandas as pd
import numpy as np
from string import ascii_uppercase


def get_tidy_data(cities): 
        xls_df = pd.read_excel(file_path, skiprows=[0, 1, 2, 3])
        column_names = ["district", "village", "office"] +["(1)\n宋楚瑜\n余湘","(2)\n韓國瑜\n張善政","(3)\n蔡英文\n賴清德"]+ list(ascii_uppercase[:8])
        xls_df.columns = column_names
        xls_df["district"]=xls_df["district"].str.replace("\u3000","").str.strip()
        xls_df.drop(list(ascii_uppercase[:8]),axis="columns",inplace=True)
        xls_df["district"].fillna(method="ffill",inplace=True)
        xls_df.dropna(how="any",inplace=True)
        candidate_infos = list(xls_df.columns[3:])
        xls_df = xls_df.melt(id_vars=['district', 'village', 'office'], value_vars=candidate_infos, var_name="candidate_info", value_name='votes')
        return xls_df


admin_areas = ["臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "基隆市", "新竹市", "嘉義市", "金門縣", "連江縣"]
file_paths = ["C:\\Users\\rober\\Desktop\\udemy-郭耀仁講師\\總統-各投票所得票明細及概況(Excel檔)\\總統-A05-4-候選人得票數一覽表-各投開票所({}).xls".format(city) for city in admin_areas]        
df_dict = {}
for file_path, admin_area in zip(file_paths, admin_areas):
    tidy_df = get_tidy_data(file_path)
    tidy_df.insert(0,"city",admin_area)
    df_dict[admin_area] = tidy_df
    print("現在正在處理{}的資料...".format(admin_area))
    print("資料外觀為：", tidy_df.shape)

total=pd.DataFrame()    
for values in df_dict.values():
    total=total.append(values,ignore_index=True)


# split_candidate_info = presidential_votes["candidate_info"].str.split("\n", expand=True)
# presidential_votes["number"] = split_candidate_info[0].str.replace('\(', '').str.replace('\)', '')
# presidential_votes["candidates"] = split_candidate_info[1].str.cat(split_candidate_info[2], '/')
total["candidate_info"]=total["candidate_info"].str.split("\n")#,expand=True)
total.insert(3,"candidate_num",total["candidate_info"].str.get(0).str.replace("(","").str.replace(")",""))
total.insert(4,"candidate",total["candidate_info"].str.get(1))
total.insert(5,"v_candidate",total["candidate_info"].str.get(2))
total["candidate"]=total["candidate"].str.cat(total["v_candidate"].values,sep="\\")
total.drop(["candidate_info","v_candidate"],axis="columns",inplace=True)

total["candidate_num"]=total["candidate_num"].astype(int)

def party(x):
    if x==1:
        return "親民黨"
    elif x==2:
        return "中國國民黨"
    else:
        return "民主進步黨"

total["party"]=total["candidate_num"].apply(party)
total.columns=["縣市","鄉(鎮、市、區)別","村里別","candidate_number","candidate","投票所別","votes","party"]
total['投票所別'] =total['投票所別'].astype(int)
total['votes'] = total['votes'].astype(str)
total['votes'] = total['votes'].str.replace(',', '').astype(int)
total.to_csv("president_vote.csv",index=False,encoding="utf_8_sig")

