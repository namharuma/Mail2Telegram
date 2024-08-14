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

3. Configure `docker-compose.yml`:
   - Open the `docker-compose.yml` file and add the following environment variables:

```yaml
services:
  mail2telegram:
    # ... other configurations ...
    environment:
      - LANGUAGE=English  # or Chinese
      - TIMEZONE=Asia/Shanghai  # set your preferred timezone
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
