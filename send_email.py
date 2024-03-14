# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders

# def send_email(subject, message, from_email, to_email, smtp_server, smtp_port, smtp_username, smtp_password, attachment_path=None):
#     # Create a MIMEMultipart object
#     email_message = MIMEMultipart()
#     email_message['From'] = from_email
#     email_message['To'] = to_email
#     email_message['Subject'] = subject

#     # Attach the message
#     email_message.attach(MIMEText(message, 'plain'))

#     # Attach the file
#     if attachment_path:
#         with open(attachment_path, "rb") as attachment_file:
#             attachment = MIMEBase("application", "octet-stream")
#             attachment.set_payload(attachment_file.read())
#         encoders.encode_base64(attachment)
#         attachment.add_header(
#             "Content-Disposition",
#             f"attachment; filename= {attachment_path.split('/')[-1]}",
#         )
#         email_message.attach(attachment)

#     # Connect to the SMTP server
#     with smtplib.SMTP(smtp_server, smtp_port) as server:
#         server.starttls()
#         server.login(smtp_username, smtp_password)
#         server.send_message(email_message)

# # Example usage
# subject = "Test Email with Attachment"
# message = "This is a test email with attachment sent from Python."
# from_email = "azmatali7ctech@gmail.com"
# to_email = "azmatali7ctech@gmail.com"
# smtp_server = "smtp.gmail.com"
# smtp_port = 587
# smtp_username = "testarbaz11@gmail.com"
# smtp_password = "Testing@12"
# attachment_path = "D:/fp4/fp-ai/ml_our_picks_for_you/Code/logs/app.log"

# send_email(subject, message, from_email, to_email, smtp_server, smtp_port, smtp_username, smtp_password, attachment_path)



import smtplib
# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)
# start TLS for security
s.starttls()
# Authentication
s.login("zmatali7ctech@gmail.com", "Azm123at@!901")
# message to be sent
message = "Message_you_need_to_send"
# sending the mail
s.sendmail("sender_email_id", "receiver_email_id", message)
# terminating the session
s.quit()