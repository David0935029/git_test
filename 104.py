#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''匯入套件'''
import json, os, pprint, time
from urllib import parse
import requests
from bs4 import BeautifulSoup

'''放置 金庸小說 metadata 的資訊'''
listData = []

'''小庸小說的網址'''
url = 'https://www.bookwormzz.com/zh/'

'''設定標頭'''
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}

# 取得小說的主要連結
def getMainLinks():
    response = requests.get(url, headers = headers)
    soup = BeautifulSoup(response.text, "lxml")
    a_elms = soup.select('a[data-ajax="false"]')
    for a in a_elms:
        listData.append({
            "title": a.text,
            "link": url + parse.unquote( a.get('href') ) + '#book_toc'
        })

# 取得所有小說的獨立連結
def getSubLinks():
    for i in range( len(listData) ):
        # 沒有 sub 屬性，則建立，為了放置各個章回小說的 metadata
        if "sub" not in listData[i]:
            listData[i]['sub'] = []
        
        response = requests.get(listData[i]['link'], headers = headers)
        soup = BeautifulSoup(response.text, "lxml")
        a_elms = soup.select('div[data-theme="b"][data-content-theme="c"] a[rel="external"]')
        
        # 若是走訪網頁時，選擇不到特定的元素，視為沒有資料，continue 到 for 的下一個 index 去
        if len(a_elms) > 0:
            for a in a_elms:
                listData[i]['sub'].append({
                    "sub_title": a.text,
                    "sub_link": url + parse.unquote( a.get('href') )
                })
        else:
            continue

# 建立 金庸小說 metadata 的 json 檔
def saveJson():
    fp = open("jinyong.json", "w", encoding="utf-8")
    fp.write( json.dumps(listData, ensure_ascii=False) )
    fp.close()

# 將金庸小說所有章回的內容，各自寫到 txt 與 json 中
def writeTxt():
    # 稍候建立 train.json 前的程式變數
    listContent = []

    # 開啟 金庸小說 metadata 的 json 檔
    fp = open("jinyong.json", "r", encoding="utf-8")
    strJson = fp.read()
    fp.close()

    # 沒有放置 txt 檔的資料夾，就建立起來
    folderPath = 'jinyong_txt'
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    # 走訪所有章回的小說文字內容
    listResult = json.loads(strJson)
    for i in range(len(listResult)):
        for j in range(len(listResult[i]['sub'])):
            response = requests.get(listResult[i]['sub'][j]['sub_link'], headers = headers)
            soup = BeautifulSoup(response.text, "lxml")
            div = soup.select_one('div#html > div')
            strContent = div.text
            
            # 資料清理
            strContent = strContent.replace(" ", "")
            strContent = strContent.replace("\r", "")
            strContent = strContent.replace("\n", "")
            strContent = strContent.replace("　", "")

            # 決定 txt 的檔案名稱
            fileName = f"{listResult[i]['title']}_{listResult[i]['sub'][j]['sub_title']}.txt"
            
            # 將小說內容存到 txt 中
            fp = open(f"{folderPath}/{fileName}", "w", encoding="utf-8")
            fp.write(strContent)
            fp.close()

            # 額外將小說內容放到 list 當中，建立 train.json
            listContent.append(strContent)

    # 延伸之後的教學，在此建立訓練資料
    fp = open("train.json", "w", encoding="utf-8")
    fp.write( json.dumps(listContent, ensure_ascii=False) )
    fp.close()

if __name__ == "__main__":
    time1 = time.time()
    getMainLinks()
    getSubLinks()
    saveJson()
    writeTxt()
    print(f"執行總花費時間: {time.time() - time1}")

print("I love you")

