import requests
import pprint

headers = {"Accept": "application/json",
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           "Accept-Encoding": "none",
           "Accept-Language": "en-US,en;q = 0.8",
           "Connection": "keep-alive",
           "Referer": "https://cssspritegenerator.com",
           "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML,like Gecko) Chrome / 23.0.1271.64Safari / 537.11"
}
r = requests.get('https://chart.stock-ai.com/history?symbol=%5ETWII&resolution=D&from=1564604150&to=1598818610', verify=False,headers=headers)
if r.status_code == requests.codes.ok:
    data = r.json()
    zipped = zip(data['t'], data['o'], data['h'], data['l'], data['o'], data['v'])
    pprint.pprint(list(zipped))