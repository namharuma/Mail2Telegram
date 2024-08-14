# Mail2Telegram

中文 | [English](./README.md)

Mail2Telegram 是一个基于 Python 的项目，用于监控电子邮件的新消息，并将其转发到指定的 Telegram 聊天中。

## 快速启动 (基于 docker-compose)

1. 克隆仓库并进入项目目录：

```bash
git clone https://github.com/Heavrnl/mail2telegram
cd ./mail2telegram
```

2. 配置 `config.py`：
   - 复制 `config-template.py` 并重命名为 `config.py`
   - 填写必要的配置信息（仅支持 Outlook 和 Gmail 邮箱，如账号开启2FA，请自行前往账户获取应用密码）

3. 配置 `docker-compose.yml`：
   - 打开 `docker-compose.yml` 文件并添加以下环境变量：

```yaml
services:
  mail2telegram:
    # ... 其他配置 ...
    environment:
      - LANGUAGE=Chinese  # 或 English
      - TIMEZONE=Asia/Shanghai  # 设置您的首选时区
```

4. 启动服务：

```bash
docker-compose up -d
```

5. 当您收到 Telegram 机器人发送的"登录成功"消息时，表示服务已成功运行。


## 注意事项

- 仅支持 Outlook 和 Gmail 邮箱
- 如账号开启2FA，请自行前往账户获取应用密码
- 在 `docker-compose.yml` 中设置正确的语言和时区以获得最佳使用体验
