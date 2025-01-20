EMAILS = [
    {
        'EMAIL': 'sokkenai24@gmail.com',
        'PASSWORD': 'vpoa oaou klwf cfdu',
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_SERVER_PORT': 993,
    },
    {
        'EMAIL': 'example@qq.com',
        'PASSWORD': 'password/application password',
        'IMAP_SERVER': 'imap.qq.com',
        'IMAP_SERVER_PORT': 993,
    },
    # 可以添加更多邮箱配置... 
]
TELEGRAM_BOT_TOKEN = 'vpoa oaou klwf cfdu'
TELEGRAM_CHAT_ID = '1129261670'  # 主要邮件转发到的chat_id，可以是自己的user_id
TELEGRAM_JUNK_CHAT_ID = '1129261670' # 垃圾邮件转发到的chat_id，可以是自己的user_id
RETRY_LIMIT = 5  # 失败后重试次数
RETRY_DELAY = 5  # 失败重试时间间隔 
RECONNECT_INTERVAL = 1800  # 主动断开重连时间，单位秒 
RETRY_PAUSE = 600  # 重试多次失败后，停止时间，单位秒 
docker-compose up -d
