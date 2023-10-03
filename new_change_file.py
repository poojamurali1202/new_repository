import imaplib
import email
import html2text
import mysql.connector

# status pending(halted),closed,completed
# update through sql
# without description add buisness unit code

mydb = mysql.connector.connect(host='localhost', user='root', password='vrdella!6', database="mine_baxster")
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



                        formatted_result = {}
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


                        if "Description" in plain_text:
                            value = plain_text.split("Description")[1]
                            value = value.strip().split('\n')
                            st = '\n'.join(value).rstrip()
                            su = "Requisition Start Date"
                            re = st.split(su)

                            res = re[0]

                        for k in ["Site", "Business Unit Code", "Site Code", "Coordinator"]:
                            site_value = plain_text.split(k)[1].strip('\n')
                            site_value = site_value.strip().split('\n')[0]
                            res += k + ":" + site_value + "\n"

                        formatted_result['Description'] = res.replace("\r", "")
                        my_list.append(res.replace("\r", ""))
                        print(len(my_list))
                        my_tuple = tuple(my_list)
                        print(formatted_result)

                        li.append(my_tuple)
    print(li)
    stmt = "INSERT INTO client_baxster (clientjobid, job_title, job_start_date, job_end_date, business_Unit,location, Pay_Rate,Description) VALUES (%s, %s, %s,%s, %s, %s,%s,%s )"
    mycursor.executemany(stmt, li)
    mydb.commit()


email_details = fetch_email_details(user='pooja@vrdella.com', password='fqsp cnki xzas tnsq')

client_details(email_details)


mydb.close()
print("Data Inserted Successfully")

