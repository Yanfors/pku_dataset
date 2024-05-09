import threading

import datetime, time

from requests.adapters import HTTPAdapter, Retry
import openai


import requests, os


has_proxy = []
proxy_lock = threading.RLock()


# 获取代理
def get_proxy():
    """获取一个代理"""
    global has_proxy

    with proxy_lock:
        has_proxy = [x for x in has_proxy if x["t"] > time.time()]
        if len(has_proxy) > 0:
            return has_proxy.pop()
        else:
            req = requests.get(
                "http://http.tiqu.alibabaapi.com/getip?num=3&type=2&pack=135334&port=1&ts=1&lb=1&pb=4&regions=").json()
            for d in req["data"]:
                ts = datetime.datetime.strptime(d["expire_time"], "%Y-%m-%d %H:%M:%S").timestamp()
                has_proxy.append({"p": "http://" + d["ip"] + ":" + d["port"], "t": ts})
        return has_proxy.pop()


# 代理返回
def return_proxy(p):
    """归还代理"""
    if p["t"] > time.time():
        with proxy_lock:
            has_proxy.append(p)


def get_title_abstract(url):
    p = get_proxy()
    proxies = {
        "http": p["p"],
        "https": p["p"]
    }
    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries=Retry(total=3)))
    ret = s.get(url, proxies=proxies).text
    return_proxy(p)
    return ret


def get_title_abstract(url):
    from bs4 import BeautifulSoup
    your_url = url
    res = requests.get(your_url, allow_redirects=True, timeout=100000,
                       headers={'Content-Type': 'text/html;charset=utf-8',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.title.text
    engAbstract = soup.find(id='eng-abstract')
    text = 'None'
    if bool(engAbstract):
        text = engAbstract.text.replace("&amp;", " ").replace("<[^>]*>", "")

    return title, text

def gpt_ask_no_stream(text,
                      prompt="I want you to work as a professional pharmaceutical researcher. I will give you some texts and you are responsible for asking the professional questions mentioned. Make sure your answers are right."):
    # a component for the above function(gpt_ask_no_stream)
    def gpt_ask(message, stream=True, cb=None):

        openai.api_key = 'anything'
        openai.base_url = "https://freeapi.tudb.work/v1/"
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message,
            stream=stream
        )
        if stream:
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    cb(chunk.choices[0].delta.content)
        else:
            return completion.choices[0].message.content

    message = [
        {'role': 'system',
         'content': prompt},
        {'role': 'user', 'content': "hello"},
        {'role': 'assistant', 'content': "Hi there! How can I assist you today?"},
        {'role': 'user', 'content': text}
    ]
    try:
        res = gpt_ask(message, stream=False)
        print('get response')
        if len(res) <= 0 or res is None:
            print('response None')
            return gpt_ask_no_stream(text, prompt)
        print("response ok")
        if res is None:
            print(5)
            return gpt_ask_no_stream(text, prompt)
        return res
    except:
        print('Error')
        return gpt_ask_no_stream(text, prompt)

# 处理GPT返回数据，数据概率返回脏数据，所以处理的很杂乱
def split_respeonse1(text):

    print(1, text)
    d = {}
    text = str(text)
    d['answer'] = text[text.index('answer:') + 1:text.index(',')]
    text = text.split(',')[1]
    # print(text)
    d['shortest_context'] = text[text.index(':') + 1:len(text) - 1]
    return d

# 处理GPT返回数据，数据概率返回脏数据，所以处理的很杂乱
def split_respeonse2(text):
    print(2, text)
    d = {}
    text = str(text)
    d['Context_judge'] = text[text.index(':') + 1:text.index(',') if ',' in text else len(text) - 1]
    if len(text.split(',')) == 1:
        return d
    text = text.split(',')[1]
    # print(text)
    d['new_short_context'] = text[text.index(':') + 1:len(text) - 1]
    return d

# 处理GPT返回数据，数据概率返回脏数据，所以处理的很杂乱
def split_respeonse3(text):
    print(3, text)
    d = {}
    text = str(text)
    d['evaluation'] = text[text.index('evaluation:') + 12:text.index(',')]
    text = text.split(',')[1]
    # print(text)
    d['reason'] = text[text.index('reason:') + 8:len(text) - 1]
    return d


def show_dict(dict):
    for key, value in dict.items():
        print(f"Key: {key}, Value: {value}")