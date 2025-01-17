![img](./logo/logo-title.png)


<div align="center">
  <a href="./README.md">中文</a> |
  <a href="./readme/README_EN.md">English</a>
</div>
<br>


<div align="center">

[![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)][docker-url] [![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-4CAF50?style=flat-square)](https://github.com/Heavrnl/UniversalForumBlock/blob/main/LICENSE) 

[docker-url]: https://hub.docker.com/r/heavrnl/universalforumblock


</div>



# Mail2Telegram

Mail2Telegram 可以监控邮箱并将新邮件转发到 Telegram 聊天中。扩展内容支持提取邮件验证码后发送到剪贴板

>**注意**：由于微软修改了outlook的连接方法，需要用户到设置相当多东西，十分繁琐，所以现在outlook邮箱无法在此项目中使用

## 快速启动

1. 克隆仓库并进入项目目录：

```bash
git clone https://github.com/Heavrnl/mail2telegram
cd ./mail2telegram
```

2. 配置 `config.py`：
   - 复制 `config-template.py` 并重命名为 `config.py`
   - 填写必要的配置信息（**若账号开启2FA，请自行前往账号设置获取应用密码**）

```bash
EMAILS = [
    {
        'EMAIL': 'example@gmail.com',
        'PASSWORD': 'password/application password',
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_SERVER_PORT': 993,
    },
    # 可以添加更多邮箱配置... 
]
TELEGRAM_BOT_TOKEN = 'BOT_TOKEN'
TELEGRAM_CHAT_ID = 'CHAT_ID'  # 主要邮件转发到的chat id，可以是自己的USERID
TELEGRAM_JUNK_CHAT_ID = 'CHAT_ID' # 垃圾邮件转发到的chat id，可以是自己的USERID
RETRY_LIMIT = 5  # 失败后重试次数
RETRY_DELAY = 5  # 失败重试时间间隔 
RECONNECT_INTERVAL = 1800  # 主动断开重连时间，单位秒 
RETRY_PAUSE = 600  # 重试多次失败后，停止时间，单位秒 
```

3. 配置 `docker-compose.yml`：
   - 打开 `docker-compose.yml` 文件并修改以下环境变量：

```yaml
version: '3.8'

services:
  mail2telegram:
    build: .
    container_name: mail2telegram
    restart: always
    environment:
      - CONFIG_FILE=/app/config.py
      - LANGUAGE=Chinese  # Chinese 或 English
      - TIMEZONE=Asia/Shanghai # 设置你的时区
      - ENABLE_LOGGING=true  # 是否开启日志
      - ENABLE_EVC=false # 扩展功能，提取邮件验证码后发送到剪贴板，搭配 Jeric-X/SyncClipboard 使用, 在项目的tools/send_code.py配置
    volumes:
      - ./config.py:/app/config.py
      - ./log:/app/log
      - ./tools:/app/tools
    logging:
      driver: "json-file"
      options:
        max-size: "5m"  # 设置日志文件的最大大小为5MB
        max-file: "5"   # 保留最多5个日志文件
```

4. 启动服务：

```bash
docker-compose up -d
```

5. 当您收到 Telegram 机器人发送的"登录成功"消息时，表示服务已成功运行。

