import os
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

def html_to_text(part):
    try:
        html_content = part.get_payload(decode=True).decode(errors='ignore')
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text()
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
                try:
                    html_content = part.get_payload(decode=True).decode(errors='ignore')
                    soup = BeautifulSoup(html_content, "html.parser")
                    content += soup.get_text(separator='\n')  # 获取文本内容，保留换行符
                    break  # 优先使用HTML内容，解析成功后跳出循环
                except Exception as e:
                    logging.error(f"提取HTML内容时出错: {str(e)}")

        # 如果没有成功解析HTML内容，尝试解析纯文本内容
        if not content:
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    content += html.unescape(decode_part(part))  # 处理转义字符
                    break
    else:
        content = html.unescape(decode_part(email_message))  # 处理非多部分邮件

    return html.escape(content[:3000]) + "..." if len(content) > 3000 else html.escape(content)



async def send_telegram_message(message):
    config = load_config()
    TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN  # 从配置文件中加载
    TELEGRAM_CHAT_ID = config.TELEGRAM_CHAT_ID  # 从配置文件中加载
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    await app.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')

# 原有 main2.py 中的 fetch_email 函数增强为发送 Telegram 消息

def fetch_email(server, msg_num):
    logger.debug(f"Fetching email with message number: {msg_num}")
    try:
        config = load_config()
        _, data = server.fetch(msg_num, "(RFC822)")
        _, bytes_data = data[0]

        email_message = email.message_from_bytes(bytes_data)
        email_date = parsedate_to_datetime(email_message['Date'])

        timezone_str = os.environ.get('TIMEZONE', 'Asia/Shanghai')  # Default to 'Asia/Shanghai'
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

        # 检查是否是转发邮件
        original_recipient, original_sender = get_forwarded_email_info(email_message, config.EMAIL)

        if original_recipient and original_sender:
            # 如果是转发邮件，使用原始收件人
            account_email = original_recipient
            from_ = original_sender
        else:
            # 如果不是转发邮件，使用当前账户邮箱
            account_email = config.EMAIL

        content = get_email_content(email_message)

        # 获取语言设置
        language = os.environ.get('LANGUAGE', 'Chinese')  # 默认中文

        # 定义语言映射
        language_map = {}
        if language == 'English':
            language_map['new_email'] = 'New email from '
            language_map['sender'] = 'Sender: '
            language_map['subject'] = 'Subject: '
            language_map['date'] = 'Date: '
            language_map['content'] = 'Content:\n'
        else:  # Chinese
            language_map['new_email'] = '新邮件来自 '
            language_map['sender'] = '发件人: '
            language_map['subject'] = '主题: '
            language_map['date'] = '日期: '
            language_map['content'] = '内容:\n'

        # 使用语言映射构建消息
        message = (f"<b>{language_map['new_email']}{escape_html(account_email)}:</b>\n"
                   f"<b>{language_map['sender']}</b> {escape_html(from_)}\n"
                   f"<b>{language_map['subject']}</b> {escape_html(subject)}\n"
                   f"<b>{language_map['date']}</b> {formatted_time}\n\n"
                   f"<b>{language_map['content']}</b>\n{content}")

        # 发送 Telegram 消息
        asyncio.run(send_telegram_message(message))

    except Exception as e:
        logger.error(f"Error fetching email: {e}")

# 监听新邮件的逻辑保持不变
# 修改后的 idle_mail_listener，接收并创建独立的IMAP连接
# 修改后的 idle_mail_listener，接收单个参数 folder
def idle_mail_listener(folder):
    config = load_config()
    server = imaplib2.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_SERVER_PORT)

    try:
        server.login(config.EMAIL, config.PASSWORD)
        logger.info(f"Successfully logged in for folder: {folder}")
        logger.info(f"Starting IDLE listener for folder: {folder}")
        server.select(folder)

        # 获取当前邮件数量,用于跳过现有邮件
        _, msgnums = server.search(None, "ALL")
        last_email_count = len(msgnums[0].split())
        logger.debug(f"Initial email count in {folder}: {last_email_count}")

        def callback(args):
            if args[2]:
                logger.debug(f"Server notified of changes in {folder}")
                return True
            return False

        stop_event = Event()

        while not stop_event.is_set():
            try:
                server.idle(callback=callback, timeout=60)

                # 检查新邮件
                _, msgnums = server.search(None, "ALL")
                email_count = len(msgnums[0].split())

                if email_count > last_email_count:
                    new_emails = range(last_email_count + 1, email_count + 1)
                    for num in new_emails:
                        fetch_email(server, str(num))
                    last_email_count = email_count

            except Exception as e:
                logger.error(f"Error in IDLE loop for folder {folder}: {e}")
                time.sleep(5)  # 出错时等待一段时间再重试

    except Exception as e:
        logger.error(f"Error in idle_mail_listener for folder {folder}: {e}")
    finally:
        try:
            server.logout()
            logger.info(f"Logged out from server for folder: {folder}")
        except:
            pass

# 主函数保持不变
# 主函数，增加线程支持
def main():
    config = load_config()
    logger.info("Starting mail listener")
    server = imaplib2.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_SERVER_PORT)

    try:
        server.login(config.EMAIL, config.PASSWORD)
        logger.info("Successfully logged in")
        # 发送 Telegram 消息
        # 获取语言设置
        language = os.environ.get('LANGUAGE', 'Chinese')  # 默认中文

        # 定义语言映射
        language_map = {}
        if language == 'English':
            language_map['sm'] = 'Successfully logged in'
        else:  # Chinese
            language_map['sm'] = '登录成功'

        # 使用语言映射构建消息
        message = language_map['sm']
        asyncio.run(send_telegram_message(message))

        # 为每个文件夹创建一个线程
        threads = []
        for folder in FOLDERS:
            thread = threading.Thread(target=idle_mail_listener, args=(folder,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

    except Exception as e:
        logger.error(f"Error in main function: {e}")
    finally:
        try:
            server.logout()
            logger.info("Logged out from server")
        except:
            pass

if __name__ == "__main__":
    main()
