import time
import requests
from bs4 import BeautifulSoup
import json
import asyncio

n=5

async def weibo_hot_search(num=n):
    def hot_search():
        url = 'https://weibo.com/ajax/side/hotSearch'
        response = requests.get(url)
        return response.json()['data'] if response.status_code == 200 else None

    result = {
        "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "data": {}
    }
    
    data = hot_search()
    if not data:
        return json.dumps({"error": "获取失败"}, ensure_ascii=False)

    result["data"] = {
        "top": data['hotgov']['word'].strip('#'),
        "hot_list": [
            {
                "rank": i,
                "title": rs['word'],
                "tag": rs.get('label_name', '') if rs.get('label_name') in ['新','爆','沸'] else ''
            } for i, rs in enumerate(data['realtime'][:num], 1)
        ]
    }
    return json.dumps(result, ensure_ascii=False)

async def baidu_hot_search(num=n):
    result = {
        "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "data": {}
    }
    
    url = 'http://top.baidu.com/buzz?b=1&fr=topindex'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...'}
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        titles = [t.get_text() for t in soup.find_all(attrs={'class':'c-single-text-ellipsis'})[:num]]
        hots = [h.get_text() for h in soup.find_all(attrs={'class':'hot-index_1Bl1a'})[:num]]
        
        result["data"] = {
            "hot_list": [
                {"rank": i+1, "title": title, "heat": heat} 
                for i, (title, heat) in enumerate(zip(titles, hots))
            ]
        }
    except Exception as e:
        result["error"] = str(e)
    
    return json.dumps(result, ensure_ascii=False)

async def zhihu_hot_search(num=n):
    result = {
        "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "data": {}
    }
    
    try:
        url = 'https://www.zhihu.com/billboard'
        html = requests.get(url, headers={'user-agent': 'Mozilla/5.0...'})
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all(attrs={'class': 'HotList-item'})[:num]
        
        result["data"] = {
            "hot_list": [
                {
                    "rank": i+1,
                    "title": item.find(attrs={'class': 'HotList-itemTitle'}).get_text(),
                    "metrics": item.find(attrs={'class': 'HotList-itemMetrics'}).get_text()
                } for i, item in enumerate(items)
            ]
        }
    except Exception as e:
        result["error"] = str(e)
    
    return json.dumps(result, ensure_ascii=False)

async def douyin_hot_search(num=n):
    result = {
        "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "data": {}
    }
    
    try:
        url = 'https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/'
        response = requests.get(url, headers={'user-agent': 'Mozilla/5.0...'})
        
        if response.status_code == 200:
            result["data"] = {
                "hot_list": [
                    {
                        "rank": i+1,
                        "title": rs['word'],
                        "heat": rs.get('hot_value', '')
                    } for i, rs in enumerate(response.json()['word_list'][:num])
                ]
            }
        else:
            result["error"] = f"HTTP {response.status_code}"
    except Exception as e:
        result["error"] = str(e)
    
    return json.dumps(result, ensure_ascii=False)
