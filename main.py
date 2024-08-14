import os
import re
import threading
from email.utils import parsedate_to_datetime
import imaplib2
import email
import logging
import time
from threading import Event
import asyncio
from email.header import decode_header
import pytz
from telegram.ext import ApplicationBuilder
from bs4 import BeautifulSoup
import html
import chardet

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# 要监听的文件夹
FOLDERS = ["INBOX", "Junk"]
LOGIN_SUCCESS = []


def load_config():
    import config
    return config

def decode_part(part):
    charset = part.get_content_charset()
    payload = part.get_payload(decode=True)

    if not charset:
        result = chardet.detect(payload)
        charset = result['encoding']

    try:
        return payload.decode(charset, errors='ignore')
    except Exception as e:
        logging.error(f"解码邮件部分内容时出错: {str(e)}")
        return ""

def get_forwarded_email_info(email_message, account_email):
    # 检查邮件头是否包含转发信息
    delivered_to = email_message.get('Delivered-To')
    original_to = email_message.get('X-Original-To')
    return_path = email_message.get('Return-Path')
    to = email_message.get('To')

    if (delivered_to and delivered_to != account_email) or \
            (original_to and original_to != account_email) or \
            (to and to != account_email):
        # 邮件是转发的，返回原始收件人和发件人信息
        original_recipient = delivered_to or original_to or to
        original_sender = email_message.get('From')
        return original_recipient, original_sender
    else:
        # 邮件不是转发的，返回None
        return None, None

def escape_html(text):
    return html.escape(text)

def clean_html_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # 删除不需要的标签
    for tag in soup(["script", "style", "meta", "noscript", "head", "title", "link", "iframe"]):
        tag.extract()

    # 删除空标签
    for tag in soup.find_all():
        if not tag.text.strip():
            tag.extract()

    # 获取清理后的文本
    text = soup.get_text(separator='\n')

    # 移除多余的换行和空白行
    text = re.sub(r'\n\s*\n', '\n\n', text).strip()

    return text

def html_to_text(part):
    try:
        html_content = part.get_payload(decode=True).decode(errors='ignore')
        cleaned_text = clean_html_content(html_content)
        return cleaned_text
    except Exception as e:
        logging.error(f"提取HTML内容时出错: {str(e)}")
        return ""

def get_email_content(email_message):
    content = ""

    if email_message.is_multipart():
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/html" and "attachment" not in content_disposition:
                content = html_to_text(part)
                if content:  # 成功解析HTML内容后跳出循环
                    break

        # 如果没有成功解析HTML内容，尝试解析纯文本内容
        if not content:
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    content = html.unescape(decode_part(part))
                    content = re.sub(r'\n\s*\n', '\n\n', content).strip()
                    break
    else:
        content = html.unescape(decode_part(email_message))
        content = re.sub(r'\n\s*\n', '\n\n', content).strip()

    # 设置最大消息长度（例如3000字符）
    max_length = 3000
    if len(content) > max_length:
        content = content[:max_length] + "..."

    return html.escape(content)


async def send_telegram_message(message):
    config = load_config()
    TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN  # 从配置文件中加载
    TELEGRAM_CHAT_ID = config.TELEGRAM_CHAT_ID  # 从配置文件中加载
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    await app.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')


def run_in_thread(loop, coro):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()

def fetch_email(server, msg_num, email_config):
    logger.debug(f"Fetching email with message number: {msg_num}")
    try:
        _, data = server.fetch(msg_num, "(RFC822)")
        _, bytes_data = data[0]

        email_message = email.message_from_bytes(bytes_data)
        email_date = parsedate_to_datetime(email_message['Date'])

        timezone_str = os.environ.get('TIMEZONE', 'Asia/Shanghai')
        try:
            email_timezone = pytz.timezone(timezone_str)
        except pytz.UnknownTimeZoneError:
            logger.error(f"Invalid timezone specified: {timezone_str}. Using 'Asia/Shanghai' instead.")
            email_timezone = pytz.timezone('Asia/Shanghai')

        email_time = email_date.astimezone(email_timezone)
        formatted_time = email_time.strftime('%Y-%m-%d %H:%M:%S')

        logging.info(f"处理邮件，日期: {formatted_time}")

        subject, encoding = decode_header(email_message["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8', errors='ignore')

        from_ = email_message["From"]

        original_recipient, original_sender = get_forwarded_email_info(email_message, email_config['EMAIL'])

        if original_recipient and original_sender:
            account_email = original_recipient
            from_ = original_sender
        else:
            account_email = email_config['EMAIL']

        content = get_email_content(email_message)

        language = os.environ.get('LANGUAGE', 'Chinese')

        subject = escape_html(subject)
        if 'Fwd: ' in subject:
            subject = subject.replace('Fwd: ', '')

        language_map = {}
        if language == 'English':
            language_map['new_email'] = 'New email from '
            language_map['sender'] = 'Sender: '
            language_map['subject'] = 'Subject: '
            language_map['date'] = 'Date: '
            language_map['content'] = 'Content:\n'
        else:
            language_map['new_email'] = '新邮件来自 '
            language_map['sender'] = '发件人: '
            language_map['subject'] = '主题: '
            language_map['date'] = '日期: '
            language_map['content'] = '内容:\n'

        message = (f"<b>{language_map['subject']}</b> {subject}\n"
                   f"<b>{language_map['new_email']}{escape_html(account_email)}:</b>\n"
                   f"<b>{language_map['sender']}</b> {escape_html(from_)}\n"
                   f"<b>{language_map['date']}</b> {formatted_time}\n\n"
                   f"<b>{language_map['content']}</b>\n{content}")

        # 创建一个新的事件循环
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=run_in_thread, args=(loop, send_telegram_message(message)))
        t.start()
        t.join()

    except Exception as e:
        logger.error(f"Error fetching email: {e}")


def monitor_email(email_config):
    threads = []
    for folder in FOLDERS:
        thread = threading.Thread(target=idle_mail_listener, args=(email_config, folder))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def get_folder_name(folders, folder_type, email_provider):
    if email_provider == 'gmail':
        for f in folders:
            decoded = f.decode()
            if f'\\{folder_type}' in decoded:
                match = re.search(r'"([^"]*)"$', decoded)
                if match:
                    return match.group(1)
    else:
        # For other providers, we'll use the folder_type directly
        return folder_type
    return None


def idle_mail_listener(email_config, folder):
    config = load_config()
    RETRY_LIMIT = config.RETRY_LIMIT
    RECONNECT_INTERVAL = config.RECONNECT_INTERVAL
    RETRY_DELAY = config.RETRY_DELAY
    RETRY_PAUSE = config.RETRY_PAUSE  # 新增：重试暂停时间
    retry_count = 0

    # 确定邮件提供商
    email_provider = 'gmail' if 'gmail.com' in email_config['EMAIL'] else 'other'

    while retry_count < RETRY_LIMIT:
        server = imaplib2.IMAP4_SSL(email_config['IMAP_SERVER'], email_config['IMAP_SERVER_PORT'])
        last_reconnect_time = time.time()

        try:
            server.login(email_config['EMAIL'], email_config['PASSWORD'])
            logger.info(f"成功登录邮箱 {email_config['EMAIL']}")

            # 列出可用的文件夹
            _, folders = server.list()

            # 获取实际的文件夹名称
            if folder == "INBOX":
                actual_folder = "INBOX"
            else:
                actual_folder = get_folder_name(folders, folder, email_provider)

            if not actual_folder:
                raise Exception(f"找不到对应的文件夹: {folder}")

            # 选择文件夹
            status, messages = server.select(actual_folder)
            if status != "OK":
                raise Exception(f"无法选择文件夹 {actual_folder}: {messages}")

            logger.info(f"成功选择文件夹: {actual_folder}")


            # 获取语言设置
            language = os.environ.get('LANGUAGE', 'Chinese')  # 默认中文

            # 定义语言映射
            if email_config['EMAIL'] not in LOGIN_SUCCESS:
                language_map = {}
                if language == 'English':
                    language_map['sm'] = 'Successfully logged into mailbox ' + email_config['EMAIL']
                else:  # Chinese
                    if 'gmail' in actual_folder.lower():
                        actual_folder = 'Junk'
                    language_map['sm'] = '成功登录邮箱 '+ email_config['EMAIL']

                LOGIN_SUCCESS.append(email_config['EMAIL'])
                # 使用语言映射构建消息
                message = language_map['sm']
                asyncio.run(send_telegram_message(message))



            # 初始化邮件数量
            _, msgnums = server.search(None, "ALL")
            last_email_count = len(msgnums[0].split())
            logger.debug(f"{email_config['EMAIL']} 的 {actual_folder} 中的初始邮件数量: {last_email_count}")

            def callback(args):
                if args[2]:
                    logger.debug(f"服务器通知 {email_config['EMAIL']} 的 {actual_folder} 中有变化")
                    return True
                return False

            stop_event = Event()

            while not stop_event.is_set():
                try:
                    # 每半小时主动断开并重新连接
                    current_time = time.time()
                    if current_time - last_reconnect_time > RECONNECT_INTERVAL:
                        logger.info(f"{email_config['EMAIL']} 的 {actual_folder} 文件夹重新连接中...")
                        break  # 跳出内层循环，进行重新连接

                    server.idle(callback=callback, timeout=60)

                    # 检查新邮件
                    _, msgnums = server.search(None, "ALL")
                    email_count = len(msgnums[0].split())

                    if email_count > last_email_count:
                        new_emails = range(last_email_count + 1, email_count + 1)
                        for num in new_emails:
                            fetch_email(server, str(num), email_config)
                        last_email_count = email_count

                    # 成功运行后重置重试计数
                    retry_count = 0

                except Exception as e:
                    error_message = f"{email_config['EMAIL']} 的 {actual_folder} 文件夹IDLE循环中出错: {e}"
                    logger.error(error_message)
                    retry_count += 1

                    # 发送报错信息到Telegram
                    asyncio.run(send_telegram_message(
                        f"Error in IDLE loop for {email_config['EMAIL']} - {actual_folder}: {str(e)}"))

                    time.sleep(RETRY_DELAY)  # 等待一段时间后再重试



        except Exception as e:
            logger.error(f"{email_config['EMAIL']} 的 {folder} 文件夹idle_mail_listener中出错: {e}")
            retry_count += 1
            if retry_count >= RETRY_LIMIT:
                final_message = f"{email_config['EMAIL']} 的 {folder} 文件夹重试次数达到上限。等待 {RETRY_PAUSE // 60} 分钟后重试。"
                logger.error(final_message)
                asyncio.run(send_telegram_message(final_message))
                time.sleep(RETRY_PAUSE)  # 等待指定时间后重试
                retry_count = 0  # 重置重试计数以继续重试
            else:
                time.sleep(RETRY_DELAY)  # 等待一段时间后再重试
        finally:
            try:
                server.logout()
                logger.debug(f"登出 {email_config['EMAIL']} 的文件夹: {folder}")
            except:
                pass
        last_reconnect_time = time.time()  # 重新记录连接时间

def main():
    config = load_config()
    logger.info("开始监听多个邮箱账户")

    email_threads = []
    for email_config in config.EMAILS:
        thread = threading.Thread(target=monitor_email, args=(email_config,))
        email_threads.append(thread)
        thread.start()

    while any(thread.is_alive() for thread in email_threads):
        time.sleep(60)  # 每分钟检查一次

    logger.info("所有邮件监控线程已停止。程序退出。")
if __name__ == "__main__":
    main()
