![img](../logo/logo-title.png)

<div align="center">
  <a href="../README.md">中文</a> |
  <a href="./README_EN.md">English</a>
</div>
<br>


<div align="center">

![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white) [![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-4CAF50?style=flat-square)](https://github.com/Heavrnl/mail2telegram/blob/master/LICENSE) 




</div>

# Mail2Telegram

Mail2Telegram monitors email accounts and forwards new messages to Telegram chats in real-time. Extended features support extracting email verification codes and sending them to the clipboard.



## 📋 Table of Contents
- [Quick Start](#quick-start)
  - [Preparation](#preparation)
  - [Deployment Steps](#deployment-steps)
- [Extended Features](#extended-features)
  - [Extract Verification Code to Clipboard](#extract-verification-code-to-clipboard)
- [Acknowledgments](#acknowledgments)
- [Donate](#donate)

## Quick Start

### Preparation

Taking Gmail as an example:
1. Log in to Gmail and enable IMAP/SMTP service in settings
2. If 2FA is enabled, please refer to [this guide](https://support.google.com/accounts/answer/185833?hl=en) to obtain an application password
3. After obtaining the application password, fill it in the PASSWORD field in config.py

### Deployment Steps

1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Heavrnl/Mail2Telegram.git
cd ./mail2telegram
```

2. Configure `config.py`:
   - Copy `config-template.py` and rename it to `config.py`
   - Fill in the necessary configuration details
>**Note:** Due to Microsoft's changes to the Outlook connection method, users need to configure several settings, making the process quite cumbersome. As a result, Outlook email cannot be used in this project. You can set up email forwarding to another email address as an alternative.
```python
EMAILS = [
    {
        'EMAIL': 'example@gmail.com',
        'PASSWORD': 'password/application password',
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_SERVER_PORT': 993,
    },
    {
        'EMAIL': 'example@qq.com',
        'PASSWORD': 'password/application password',
        'IMAP_SERVER': 'imap.qq.com',
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

3. Start the service:

```bash
docker-compose up -d
```

4. The service is running successfully when you receive a "Successfully logged in" message from the Telegram bot.

## Extended Features

### Extract Verification Code to Clipboard
Supports local regex matching and AI ([GitHub Models](https://docs.github.com/en/github-models/prototyping-with-ai-models)/[Gemini](https://aistudio.google.com/apikey)) for extracting verification codes. Detailed configuration is explained in the `Heavrnl/ExtractVerificationCode` section below.

1. Deploy the clipboard sync service [Jeric-X/SyncClipboard](https://github.com/Jeric-X/SyncClipboard). Please visit their project page for deployment instructions.

2. Deploy the verification code extraction service [Heavrnl/ExtractVerificationCode](https://github.com/Heavrnl/ExtractVerificationCode)

```bash
git clone https://github.com/Heavrnl/ExtractVerificationCode
cd ExtractVerificationCode
```

Configure the `.env` file with the clipboard sync service settings you set up above:
```bash
cp .env.example .env
```
```ini
# Choose API type: azure or gemini
API_TYPE=gemini

# Enable local regex matching for verification code extraction (if enabled, local matching will be tried first, then API if it fails)
USE_LOCAL=false

# Prompt template
PROMPT_TEMPLATE=Extract the verification code from the following text. Output only the code, without any other text. If there is no verification code, output 'None'.\n\nText: {input_text}\n\nCode:

# Azure API configuration
AZURE_ENDPOINT=https://models.inference.ai.azure.com
AZURE_MODEL_NAME=gpt-4o-mini
# Azure API authentication Token (using GitHub Token for authentication)
GITHUB_TOKEN=

# Gemini API configuration
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash

# Clipboard sync configuration
SYNC_URL=your_sync_url
SYNC_USERNAME=your_username
SYNC_TOKEN=your_token

# Enable debug mode (true/false)
DEBUG_MODE=false
```

> **Note**: For the most accurate verification code extraction, use the AI model. Local regex matching may have some inaccuracies.

Start the service:
```bash
docker-compose up -d
```

3. Modify the `docker-compose.yml` file in our project, change `ENABLE_EVC=false` to `ENABLE_EVC=true`

Configure the `tools/send_code.py` file:
- If the verification code extraction service is deployed on the same server and uses the default port (5788), no modification is needed
- Otherwise, modify the service address and port

```python
# Replace with the actual address of your ExtractVerificationCode application
url = 'http://evc:5788/evc'
```

Start:
```bash
docker-compose up -d
```

## Privacy Considerations

The ExtractVerificationCode project implements the following security measures when processing email content:

1. Email text desensitization: Sensitive information is automatically removed before sending to AI models
2. Text filtering: Only text containing verification code-related content is sent to AI models, not entire emails

If you're still concerned about AI providers accessing your information, you can either deploy a large model locally or use only local regex matching for verification code extraction.

## Acknowledgments

- [Jeric-X/SyncClipboard](https://github.com/Jeric-X/SyncClipboard) - Cross-platform clipboard synchronization tool

## Donate

If you find this project helpful, please consider buying me a coffee:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/0heavrnl)

