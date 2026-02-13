
import smtplib
from email.mime.text import MIMEText

# Your Zoho Mail SMTP settings
SMTP_SERVER = "smtppro.zoho.eu"
SMTP_PORT = 587
SENDER_EMAIL = "admin@stakeeasy.net"
SENDER_PASSWORD = "D5gibChFbVAg"  # Be careful with hardcoding passwords

# The recipient's email address
RECIPIENT_EMAIL = "test@example.com"  # Change this to a real email address you can check

# Create the email message
msg = MIMEText("This is a test email from your Python script.")
msg["Subject"] = "Test Email"
msg["From"] = SENDER_EMAIL
msg["To"] = RECIPIENT_EMAIL

try:
    print(f"Connecting to {SMTP_SERVER} on port {SMTP_PORT}...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()  # Secure the connection
    print("Connection secured with TLS.")
    
    print(f"Logging in as {SENDER_EMAIL}...")
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    print("Login successful.")
    
    print(f"Sending email to {RECIPIENT_EMAIL}...")
    server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print("Email sent successfully!")

except smtplib.SMTPAuthenticationError as e:
    print(f"Authentication failed: {e}")
    print("Please check your email address and password.")

except smtplib.SMTPConnectError as e:
    print(f"Failed to connect to the server: {e}")
    print("Please check the SMTP server address and port.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if 'server' in locals() and server:
        server.quit()
        print("Connection closed.")
