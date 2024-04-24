import smtplib
import ssl
from email.message import EmailMessage
port = 465
smtp_server = "smtp.zeptomail.com"
username = "emailapikey"
password = "wSsVR61+8kTyBq54yDL8J79ukF5VAF6nEE8pjFqi7SOpH/vA8sc8kEbLDQSjFKQcEDZvF2RA8LgtzBwGh2UPjNsqzF9SXCiF9mqRe1U4J3x17qnvhDzKWmhelheOLIwOxQVvnGNhFc0g+g=="
message = "Test email sent successfully."
msg = EmailMessage()
msg['Subject'] = "Test Email"
msg['From'] = "noreply@homely.com.ng"
msg['To'] = "tessychidubem@gmail.com"
msg.set_content(message)
try:
    if port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(username, password)
            server.send_message(msg)
    elif port == 587:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
    else:
        print("use 465 / 587 as port value")
        exit()
    print("successfully sent")
except Exception as e:
    print(e)
