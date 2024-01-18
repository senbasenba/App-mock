# ライブラリのインポート
from bs4 import BeautifulSoup
import re
import requests
from time import sleep
from tqdm import tqdm
import pandas as pd# ライブラリのインポート
import sqlite3
import pandas as pd
from tqdm import tqdm

# SUUMOから物件情報を取得する関数
def scrape_suumo(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    contents = soup.find_all('div', class_='cassetteitem')
    data_list = []

    for content in contents:
        detail = content.find('div', class_='cassetteitem-detail')
        table = content.find('table', class_='cassetteitem_other')

        title = detail.find('div', class_='cassetteitem_content-title').text
        address = detail.find('li', class_='cassetteitem_detail-col1').text
        access = detail.find('li', class_='cassetteitem_detail-col2').text
        age_text = detail.find('li', class_='cassetteitem_detail-col3').text
        age_match = re.search(r'\d+', age_text)
        age = int(age_match.group()) if age_match else None

        tr_tags = table.find_all('tr', class_='js-cassette_link')

        for tr_tag in tr_tags:
            floor_text = re.search(r'\d+', tr_tag.find_all("td")[2].text)
            floor = int(floor_text.group()) if floor_text else None

            price, first_fee, capacity = tr_tag.find_all("td")[3:6]
            fee, management_fee = price.find_all('li')
            deposit, qratuity = first_fee.find_all('li')
            madori, menseki = capacity.find_all('li')

            cost_text = re.search(r'\d+', fee.text)
            cost = int(cost_text.group()) if cost_text else None

            size_text = re.search(r'\d+', menseki.text)
            size = int(size_text.group()) if size_text else None

            d = {
                "title": title,
                "address": address,
                "acess": access,
                "age": age,
                "floor": floor,
                "cost": cost,
                "management_fee": management_fee.text,
                "deposit": deposit.text,
                "qratuity": qratuity.text,
                "rayout": madori.text,
                "size": size,
            }

            data_list.append(d)

    return data_list

# メインの処理
url_template = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&pc=30&smk=&po1=25&po2=99&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sc=13101&sc=13102&sc=13103&sc=13104&sc=13113&ta=13&cb=0.0&ct=30.0&md=06&md=07&md=09&md=10&md=11&md=13&md=14&ts=1&et=9999999&mb=0&mt=9999999&cn=9999999&fw2='
last_page = int(BeautifulSoup(requests.get(url_template.format(1)).text, 'html.parser').find('ol', class_='pagination-parts').find_all('li')[-1].text)

# 全ページのデータを取得
all_data = []
for i in tqdm(range(1, last_page+1)):
    target_url = url_template.format(i)
    data_list = scrape_suumo(target_url)
    all_data.extend(data_list)
    sleep(1)
# データをデータフレームに変換
df = pd.DataFrame(all_data)
# all_dataからDataFrameを作成
df_all_data = pd.DataFrame(all_data)

# address、age、floor、costが同じ場合に重複とみなし、重複を排除
df_no_duplicates = df_all_data.drop_duplicates(subset=['address', 'age', 'floor', 'cost'])

print(df_no_duplicates)