import imaplib
import email
import html2text
import mysql.connector
from datetime import datetime

# status pending(halted),closed,completed
# update through sql
# without description add buisness unit code

mydb = mysql.connector.connect(host='localhost', user='root', password='vrdella!6', database="new_status")
mycursor = mydb.cursor()

def fetch_email_details(user, password):
    imap_url = 'imap.gmail.com'

    my_mail = imaplib.IMAP4_SSL(imap_url)

    my_mail.login(user, password)

    my_mail.select('Baxster')

    _, data = my_mail.search(None, 'UNSEEN')

    mail_id_list = data[0].split()  # IDs of all emails that we want to fetch

    msgs = []

    for num in mail_id_list:
        typ, data = my_mail.fetch(num, '(RFC822)')  # RFC822 returns the whole message (BODY fetches just body)
        msgs.append(data)

    return msgs


def client_details(msgs):
    global start, end, Value, val
    html_converter = html2text.HTML2Text()

    li = []

    for msg in msgs:
        for response_part in msg:
            if type(response_part) is tuple:
                my_msg = email.message_from_bytes(response_part[1])
                my_list = []
                my_tuple = tuple()

                for part in my_msg.walk():
                    # print(part.get_content_type())
                    if part.get_content_type() == 'text/plain':
                        pri = part.get_payload()

                    elif part.get_content_type() == 'text/html':
                        # Convert HTML to plain text using html2text
                        html_content = part.get_payload(decode=True).decode()
                        plain_text = html_converter.handle(html_content)

                        #id, Value, val, start, end, res = '', '', '', '', '', ''

                        if "Requisition ID" in plain_text:
                            value = plain_text.split("Requisition ID")[1].strip('\n')
                            value = value.strip().split('\n')[0]
                            id = value.replace("\r", "")
                            bool_value = "SELECT EXISTS(SELECT * FROM new_baxster WHERE clientjobid = %s )"
                            mycursor.execute(bool_value,(id,))
                            result = mycursor.fetchone()[0]
                            if "Reason" in plain_text:
                                Value = plain_text.split("Reason")[1].strip('\n')
                                Value = value.strip().split('\n')[0]
                                Value = value.replace("\r", "")
                            if "halted" in my_msg['subject']:
                                val = "halted"
                            if "closed" in my_msg['subject']:
                                val = "closed"

                            if result == 1:
                                if "Reason" in plain_text:
                                    Value = plain_text.split("Reason")[1].strip('\n')
                                    Value = value.strip().split('\n')[0]
                                    Value = value.replace("\r", "")
                                if "halted" in my_msg['subject']:
                                    val = "halted"
                                if "closed" in my_msg['subject']:
                                    val = "closed"

                                update = "UPDATE new_baxster SET Comment = %s  WHERE clientjobid = %s"
                                mycursor.execute(update, ("closed","BXTRJP00023757"))
                                print("already existing record")
                            elif result == 0:
                                formatted_result = {}
                                res = ""
                                formatted_result['client'] = "baxster"
                                formatted_result['Comment'] = "NOne"
                                my_list.append(formatted_result['client'])
                                my_list.append(formatted_result['Comment'])
                                data_s = ["Requisition ID", "Requisition Title", "Requisition Start Date","Requisition End Date", "Business Unit", "Location"]
                                keys = ["clientjobid", "job_title", "job_start_date", "job_end_date", "business_Unit","location"]

                                for i, j in zip(data_s, keys):
                                    if i in plain_text:
                                        value = plain_text.split(i)[1].strip('\n')
                                        value = value.strip().split('\n')[0]
                                        formatted_result[j] = value.replace("\r", "")
                                        my_list.append(value.replace("\r", ""))

                                if "Pay Rate:" in plain_text:
                                    value = plain_text.split("Pay Rate:")[1].strip('\n')
                                    value = value.strip().split('\n')[0]
                                    formatted_result["Pay_Rate"] = value.replace("\r", "")
                                    my_list.append(value.replace("\r", ""))

                                if "Pay rate:" in plain_text:
                                    value = plain_text.split("Pay rate:")[1].strip('\n')
                                    value = value.strip().split('\n')[0]
                                    formatted_result["Pay_Rate"] = value.replace("\r", "")
                                    my_list.append(value.replace("\r", ""))

                                if "Requisition Start Date" in plain_text:
                                    start = plain_text.split("Requisition Start Date")[1].strip('\n')
                                    start = start.strip().split('\n')[0].rstrip()
                                    start = datetime.strptime(start, "%Y-%m-%d").date()
                                if "Requisition End Date" in plain_text:
                                    end = plain_text.split("Requisition End Date")[1].strip('\n')
                                    end = end.strip().split('\n')[0].rstrip()
                                    end = datetime.strptime(end, "%Y-%m-%d").date()



                                b = datetime.now().date()
                                if start <= b and end >= b:
                                   formatted_result['Status'] = 'Pending'
                                   my_list.append(formatted_result['Status'])
                                else:
                                    formatted_result['Status'] = 'Completed'
                                    my_list.append(formatted_result['Status'])

                                if "Description" in plain_text:
                                    value = plain_text.split("Description")[1]
                                    value = value.strip().split('\n')
                                    st = '\n'.join(value).rstrip()
                                    su = "Requisition Start Date"
                                    re = st.split(su)

                                    res += re[0]

                                for k in ["Site", "Business Unit Code", "Site Code", "Coordinator"]:
                                    site_value = plain_text.split(k)[1].strip('\n')
                                    site_value = site_value.strip().split('\n')[0]
                                    res += k + ":" + site_value + "\n"

                                formatted_result['Description'] = res.replace("\r", "")
                                my_list.append(res.replace("\r", ""))
                                #print(len(my_list))
                                my_tuple = tuple(my_list)
                                print(formatted_result)
                                print(li)

                                li.append(my_tuple)
    print(li)
    stmt = "INSERT INTO new_baxster (client,Comment,clientjobid, job_title, job_start_date, job_end_date, business_Unit,location, Pay_Rate,Status,Description) VALUES (%s, %s, %s,%s, %s, %s,%s,%s,%s,%s,%s )"
    mycursor.executemany(stmt, li)
    mydb.commit()


email_details = fetch_email_details(user='pooja@vrdella.com', password='fqsp cnki xzas tnsq')

client_details(email_details)


mydb.close()
print("Data Inserted Successfully")

