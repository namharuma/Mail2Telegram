# Mail2Telegram

[中文](./README_zh.md) | English

Mail2Telegram is a Python-based project that monitors email accounts for new messages and forwards them to specified Telegram chats.

## Quick Start (using docker-compose)

1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Heavrnl/mail2telegram
cd ./mail2telegram
```

2. Configure `config.py`:
   - Copy `config-template.py` and rename it to `config.py`
   - Fill in the necessary configuration details (only Outlook and Gmail are supported; if your account has 2FA enabled, please obtain an application password from your account)

```bash
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
    # You can add more email configurations...
]
TELEGRAM_BOT_TOKEN = 'BOT_TOKEN'
TELEGRAM_CHAT_ID = 'CHAT_ID'  # The Telegram chat ID where you want to forward emails
TELEGRAM_JUNK_CHAT_ID = 'CHAT_ID' # Telegram chat ID where junk mail is sent
RETRY_LIMIT = 5  # Number of retry attempts after a failure
RETRY_DELAY = 5  # Time interval between retry attempts after a failure
RECONNECT_INTERVAL = 1800  # Interval for proactive disconnection and reconnection, in seconds
RETRY_PAUSE = 600  # Pause time after multiple failed retries, in seconds
```

3. Configure `docker-compose.yml`:
   - Open the `docker-compose.yml` file and change the following environment variables:

```yaml
version: '3.8'

services:
  email_checker:
    build: .
    restart: always
    environment:
      - CONFIG_FILE=/app/config.py
      - LANGUAGE=Chinese  # Chinese or English
      - TIMEZONE=Asia/Shanghai # Set your timezone
      - ENABLE_LOGGING=true  # Whether to enable logging
      - ENABLE_EVC=false # Extended feature, extract email verification code and send to clipboard, use with Jeric-X/SyncClipboard, configure in tools/send_code.py of the project
    volumes:
      - ./config.py:/app/config.py
      - ./log:/app/log
      - ./tools:/app/tools
    logging:
      driver: "json-file"
      options:
        max-size: "5m"  # Set the maximum size of log files to 5MB
        max-file: "5"   # Keep a maximum of 5 log files
```

4. Start the service:

```bash
docker-compose up -d
```

5. The service is running successfully when you receive a "Successfully logged in" message from the Telegram bot.


## Important Notes

- Only Outlook and Gmail are supported
- If your account has 2FA enabled, please obtain an application password from your account
- Set the correct language and timezone in `docker-compose.yml` for optimal usage
