
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from setting import  msg_from, msg_to, SMTP_server

from datetime import date


# Open the plain text file whose name is in textfile for reading.
# Create a text/plain message
def send_mail(file_name):
    send_year = date.today().strftime('%Y')
    send_month = date.today().strftime('%m')

    email_text = """
    Dear :
    
    附件為 {} 年 {} 月的資料，謝謝。
    * 此信件為系統自動發送，有任何問題請洽

            """.format(send_year, send_month)

    msg = MIMEMultipart()
    msg['Subject'] = ' {}年 {}月資料'.format(send_year, send_month)  # 主題
    msg['From'] = msg_from  # 發件人
    msg['To'] = msg_to

    main_text = MIMEText(email_text)
    msg.attach(main_text)

    attach_file = file_name

    part_attach1 = MIMEApplication(open(attach_file, 'rb').read())
    part_attach1.add_header('Content-Disposition', 'attachment',
                            filename='{}_Report'.format(send_year + '-' + send_month) + str(date.today()) + '.xlsx')  # 為附件命名

    msg.attach(part_attach1)


    s = smtplib.SMTP(SMTP_server)
    s.send_message(msg)
    s.quit()


if __name__ == '__main__':
    send_mail('')
