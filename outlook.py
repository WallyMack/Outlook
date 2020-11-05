import email
import logging
import datetime
import os
import imaplib
from setting import mailserver, account, password, mailbox ,path
import process_ShopBack_Report
import send_email
import slack_class as sc


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M')

class mail():
    def __init__(self,account,password,mailbox):
        self.mailserver = mailserver
        self.account = account
        self.password = password
        self.mailbox = mailbox

    def mail_connect(self, search_conditions):
        mail = imaplib.IMAP4_SSL(self.mailserver)
        mail.login(self.account , self.password)
        #mail.list()    # Out: list of "folders" aka labels in gmail.
        mail.select(mailbox) # connect to inbox.
        #result, data = mail.uid('search', 'from', 'ads-noreply@google.com')
        result, data = mail.uid('search', None, search_conditions)
        email_uids = data[0].split()
        # 判斷有沒有email存在
        if not email_uids:
            return None, None
        headers=[]
        for uids in email_uids:
            result, data = mail.uid('fetch', uids, '(RFC822)') # fetch the email body (RFC822) for the given ID
            raw_email = data[0][1] # here's the body, which is raw text of the whole email
            # email_message = email.message_from_bytes(raw_email)
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)
            headers.append(email_message)
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                fileName = part.get_filename()
                if bool(fileName):
                    filePath = os.path.join(path + '\\Process_file', fileName.replace(" ",""))
                    if not os.path.isfile(filePath):
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                        logging.info('{} files write finished.'.format(fileName))
                        return headers, filePath
                    return None, None


if __name__ == "__main__":

    today = datetime.datetime.today()

    # this week start day
    since_date = (today + datetime.timedelta(days=- 14)).strftime('%d-%h-%Y')
    # this week end day
    before_date = (today + datetime.timedelta(days=6 - today.weekday())).strftime('%d-%h-%Y')
    search_conditions = '(SINCE "%s" BEFORE "%s")' %  (since_date, before_date)
    # subject day
    subject_day = (today + datetime.timedelta(days=-today.weekday())).strftime('%Y-%m')
    body = mail(account,password,mailbox)
    try:
        context, filepath = body.mail_connect(search_conditions)
        if not context:
            logging.info('not file need Process.')
            exit(0)

        psr = process_ShopBack_Report.ETL()
        sb_file_date = datetime.datetime.today().strftime('%Y-%m')
        ShopBack_Report = psr.Load_csv(filepath, sb_file_date)
        logging.info(ShopBack_Report)
        driver = psr.erp_login()
        now = today.strftime('%Y%m%d')
        shopback_filepath = psr.upload_file_to_ERP(ShopBack_Report, driver, now)
        logging.info(shopback_filepath)
        merge_file_path = psr.trans_shopback_file(filepath, shopback_filepath, sb_file_date)
        send_email.send_mail(merge_file_path)
        logging.info('send_mail OK.')
    except Exception as e:
        logging.error(e)
        Exc = e
        icon = ':fire:'
        status = '自動化失敗'
        sc.slack_alert(Exc, icon, status)



