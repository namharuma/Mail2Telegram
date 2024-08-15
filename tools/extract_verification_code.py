import re


def extract_verification_code(text):
    keywords = {
        "验证码", "校验码", "检验码", "确认码", "激活码", "动态码", "安全码",
        "验证代码", "校验代码", "检验代码", "激活代码", "确认代码", "动态代码", "安全代码",
        "登入码", "认证码", "识别码", "短信口令", "动态密码", "交易码", "上网密码", "随机码", "动态口令",
        "驗證碼", "校驗碼", "檢驗碼", "確認碼", "激活碼", "動態碼",
        "驗證代碼", "校驗代碼", "檢驗代碼", "確認代碼", "激活代碼", "動態代碼",
        "登入碼", "認證碼", "識別碼",
        "Code", "code", "CODE", "verification"
    }

    # 构建正则表达式模式
    keyword_pattern = '|'.join(map(re.escape, keywords))
    patterns = [
        rf'(?:{keyword_pattern})\s*[:：]?\s*([A-Za-z0-9]{{4,8}})\b',  # 匹配关键词后的4-8位字母数字
        rf'(?:{keyword_pattern})\s*[:：]?\s*\n\s*([A-Za-z0-9]{{4,8}})\b',  # 匹配关键词后换行的4-8位字母数字
        r'\b([A-Za-z0-9]{4,8})\b'  # 匹配独立的4-8位字母数字
    ]

    # 尝试所有模式
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1)

    return None  # 如果没有找到验证码


# # 测试函数
# test_texts = [
#     """您好，你正在进行API.66D.EU邮箱验证。
#     您的验证码为:
#     0905ef
#     验证码 10 分钟内有效，如果不是本人操作，请忽略。""",
#
#     "Your verification code is: ABC123",
#
#     "请输入校验码 5678 完成注册",
#
#     "To complete your registration, please use the following code:\n9876ZX",
#
#     """验证码
#
# 311412""",
#
#     """Verification Code
#
#     XY9876""",
#
#     "您的動態密碼是：A8B9C0",
#
#     "安全代码：\n123456",
#
#     "Please enter the authentication CODE: 7890XY"
# ]
#
# for text in test_texts:
#     code = extract_verification_code(text)
#     print(f"文本: \n{text}\n提取的验证码: {code}\n")