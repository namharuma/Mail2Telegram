![img](./logo/logo-title.png)

<div align="center">
  <a href="./README.md">中文</a> |
  <a href="./readme/README_EN.md">English</a>
</div>
<br>


<div align="center">

[![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)][docker-url] [![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-4CAF50?style=flat-square)](https://github.com/Heavrnl/mail2telegram/blob/master/LICENSE) 

[docker-url]: https://hub.docker.com/r/heavrnl/universalforumblock


</div>

# Mail2Telegram

Mail2Telegram 可以监控邮箱并将新邮件转发到 Telegram 聊天中。扩展内容支持提取邮件验证码后发送到剪贴板

>**注意**：由于微软修改了outlook的连接方法，需要用户到设置相当多东西，十分繁琐，所以现在outlook邮箱无法在此项目中使用，可以设置邮件转发到其他邮箱

## 📋 目录
- [快速启动](#快速启动)
  - [准备工作](#准备工作)
  - [部署步骤](#部署步骤)
- [扩展功能](#扩展功能)
  - [提取邮件验证码并发送至剪贴板](#提取邮件验证码并发送至剪贴板)
- [致谢](#致谢)
- [捐赠](#捐赠)

## 快速启动

### 准备工作

以Gmail为例：
1. 登录Gmail，在设置中开启IMAP/SMTP服务
2. 若开启2FA，请参考[这里](https://knowledge.workspace.google.com/kb/how-to-create-app-passwords-000009237?hl=zh-cn)获取应用密码
3. 获取到应用密码后，在config.py中的PASSWORD填写应用密码

### 部署步骤

1. 克隆仓库并进入项目目录：

```bash
git clone https://github.com/Heavrnl/mail2telegram
cd ./mail2telegram
```

2. 配置 `config.py`：
   - 复制 `config-template.py` 并重命名为 `config.py`
   - 填写必要的配置信息

```python
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

3. 启动服务：

```bash
docker-compose up -d
```

4. 当您收到 Telegram 机器人发送的"登录成功"消息时，表示服务已成功运行。

## 扩展功能

### 提取邮件验证码并发送至剪贴板

1. 部署剪贴板同步服务 [Jeric-X/SyncClipboard](https://github.com/Jeric-X/SyncClipboard)

2. 部署验证码提取服务 [Heavrnl/ExtractVerificationCode](https://github.com/Heavrnl/ExtractVerificationCode)

```bash
git clone https://github.com/Heavrnl/ExtractVerificationCode
```
```bash
cd ExtractVerificationCode
```

配置 `.env` 文件：
```bash
cp .env.example .env
```



> **注意**：若想要最精确的提取验证码，请使用ai模型，本地正则匹配可能会有误差

启动服务：
```bash
docker-compose up -d
```

3.修改我们本项目中的`docker-compose.yml`文件，重新复制以下内容使用:
```yaml
services:
  mail2telegram:
    build: .
    container_name: mail2telegram
    restart: always
    environment:
      - CONFIG_FILE=/app/config.py
      - LANGUAGE=Chinese  # Chinese or English
      - TIMEZONE=Asia/Shanghai # 设置你的时区
      - ENABLE_LOGGING=true  # 是否开启日志
      - ENABLE_EVC=true # 扩展功能，提取邮件验证码后发送到剪贴板，搭配 Jeric-X/SyncClipboard 使用
    volumes:
      - ./config.py:/app/config.py
      - ./log:/app/log
      - ./tools:/app/tools
    logging:
      driver: "json-file"
      options:
        max-size: "5m"
        max-file: "5"
    networks:
      - evc 
networks:
  evc:
    name: evc
    driver: bridge
    external: false
```

配置 `tools/send_code.py` 文件：
- 如果验证码提取服务与本项目部署在同一服务器且使用默认端口(5788)，则无需修改
- 否则需要修改服务地址和端口

```python
# 替换为您的 ExtractVerificationCode 应用程序的实际地址
url = 'http://evc:5788/evc'
```

启动
```bash
docker-compose up -d
```


## 致谢

- [Jeric-X/SyncClipboard](https://github.com/Jeric-X/SyncClipboard) - 跨平台剪贴板同步工具


## 捐赠

如果你觉得这个项目对你有帮助，欢迎通过以下方式请我喝杯咖啡：

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/0heavrnl)

