import re
import requests
import logging
from tools.send_code import upload
def extract_verification_code(text):

    url = "http://qwen:5000/process"
    prompt_template = "从以下文本中提取验证码。只输出验证码，不要有任何其他文字。如果没有验证码，只输出'None'。\n\n文本：{input_text}\n\n验证码："
    headers = {"Content-Type": "application/json"}
    data = {"text": text,"prompt_template":prompt_template}

    response = requests.post(url, json=data, headers=headers)
    # 获取响应的文本内容
    response_text = response.text
    print(response_text)  # 打印响应文本，帮助调试
    # 解析JSON响应
    response_json = response.json()
    verification_code = response_json.get("response", "").split('\n')[0].strip()
    logging.info(f"verification_code:{verification_code}")
    if verification_code.lower() == 'none':
        return None
    upload(verification_code)

# def extract_verification_code(text):
#     keywords = {
#         "验证码", "校验码", "检验码", "确认码", "激活码", "动态码", "安全码",
#         "验证代码", "校验代码", "检验代码", "激活代码", "确认代码", "动态代码", "安全代码",
#         "登入码", "认证码", "识别码", "短信口令", "动态密码", "交易码", "上网密码", "随机码", "动态口令",
#         "驗證碼", "校驗碼", "檢驗碼", "確認碼", "激活碼", "動態碼",
#         "驗證代碼", "校驗代碼", "檢驗代碼", "確認代碼", "激活代碼", "動態代碼",
#         "登入碼", "認證碼", "識別碼",
#         "Code", "code", "CODE", "verification"
#     }
#
#     # 构建正则表达式模式
#     keyword_pattern = '|'.join(map(re.escape, keywords))
#     patterns = [
#         rf'(?:{keyword_pattern})\s*[:：]?\s*([A-Za-z0-9]{{4,8}})\b',  # 匹配关键词后的4-8位字母数字
#         rf'(?:{keyword_pattern})\s*[:：]?\s*\n\s*([A-Za-z0-9]{{4,8}})\b',  # 匹配关键词后换行的4-8位字母数字
#     ]
#
#     # 尝试所有模式
#     for pattern in patterns:
#         match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
#         if match:
#             return match.group(1)
#
#     return None  # 如果没有找到验证码

# # 测试函数
# text = """Issue Date: 18 Aug 2024
#
#
# Update on your Multi-Currency Account interest rate
#
# iFAST Global Bank is here to notify you that we have made some changes to the interest rate for your Multi-Currency Account, with the following details:
#
# Currency:
#  GBP
#
# Interest Rate:
#  4.25% AER (4.17% gross) variable
# """
# code = extract_verification_code(text)
# print(f"文本: \n{text}\n提取的验证码: {code}\n")