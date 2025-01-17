import requests

import logging

def extract_verification_code(text):
    url = 'http://evc:5788/evc'  # 替换为您的 evc 应用程序的实际地址
    headers = {'Content-Type': 'application/json'}
    data = {'text': text}

    respones =  requests.post(url, headers=headers, json=data)
    logging.info(respones)


