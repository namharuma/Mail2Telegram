![img](../logo/logo-title.png)


<div align="center">
  <a href="../README.md">中文</a> |
  <a href="./README_EN.md">English</a>
</div>
<br>


<div align="center">

[![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)][docker-url] [![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-4CAF50?style=flat-square)](https://github.com/Heavrnl/UniversalForumBlock/blob/main/LICENSE) 

[docker-url]: https://hub.docker.com/r/heavrnl/universalforumblock


</div>

# Mail2Telegram

Mail2Telegram monitors email accounts and forwards new messages to Telegram chats. Extended features support extracting email verification codes and sending them to the clipboard.

>**Note:** Due to Microsoft's changes to the Outlook connection method, users need to configure several settings, making the process quite cumbersome. As a result, Outlook email cannot be used in this project. You can set up email forwarding to another email address as an alternative.

## Quick Start

### Preparation

Taking Gmail as an example:
1. Log in to Gmail and enable IMAP/SMTP service in settings
2. If 2FA is enabled, please refer to [this guide](https://support.google.com/accounts/answer/185833?hl=en) to obtain an application password
3. After obtaining the application password, fill it in the PASSWORD field in config.py

### Deployment Steps

1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Heavrnl/mail2telegram
cd ./mail2telegram
```

2. Configure `config.py`:
   - Copy `config-template.py` and rename it to `config.py`
   - Fill in the necessary configuration details

```bash
EMAILS = [
    {
        'EMAIL': 'example@gmail.com',
        'PASSWORD': 'password/application password',
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_SERVER_PORT': 993,
    },
    # You can add more email configurations...
]
TELEGRAM_BOT_TOKEN = 'BOT_TOKEN'
TELEGRAM_CHAT_ID = 'CHAT_ID'  # The main Telegram chat ID where you want to forward emails, can be your USER_ID
TELEGRAM_JUNK_CHAT_ID = 'CHAT_ID' # Telegram chat ID where junk mail is sent, can be your USER_ID
RETRY_LIMIT = 5  # Number of retry attempts after a failure
RETRY_DELAY = 5  # Time interval between retry attempts after a failure
RECONNECT_INTERVAL = 1800  # Interval for proactive disconnection and reconnection, in seconds
RETRY_PAUSE = 600  # Pause time after multiple failed retries, in seconds
```

3. Configure `docker-compose.yml`:
   - Open the `docker-compose.yml` file and change the following environment variables:

```yaml
services:
  mail2telegram:
    build: .
    container_name: mail2telegram
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
