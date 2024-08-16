EMAILS = [
    {
        'EMAIL': 'example@outlook.com',
        'PASSWORD': 'password/application password',
        'IMAP_SERVER': 'outlook.office365.com',
        'IMAP_SERVER_PORT': 993,
    },
    {
        'EMAIL': 'example@gmail.com',
        'PASSWORD': 'password/application password',
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_SERVER_PORT': 993,
    },
    # 可以添加更多邮箱配置... (You can add more email configurations...)
]
TELEGRAM_BOT_TOKEN = 'BOT_TOKEN'
TELEGRAM_CHAT_ID = 'CHAT_ID'  # 把邮件转发到的telegram chat id (The Telegram chat ID where you want to forward emails)
TELEGRAM_JUNK_CHAT_ID = 'CHAT_ID' # 把垃圾邮件发到的的telegram chat id
RETRY_LIMIT = 5  # 失败后重试次数 (Number of retry attempts after a failure)
RETRY_DELAY = 5  # 失败重试时间间隔 (Time interval between retry attempts after a failure)
RECONNECT_INTERVAL = 1800  # 主动断开重连时间，单位秒 (Interval for proactive disconnection and reconnection, in seconds)
RETRY_PAUSE = 600  # 重试多次失败后，停止时间，单位秒 (Pause time after multiple failed retries, in seconds)