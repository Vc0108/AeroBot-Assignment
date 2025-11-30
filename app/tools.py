import smtplib
from email.mime.text import MIMEText
from langchain.tools import tool
from db.database import add_booking
import os

# --- EMAIL FUNCTION ---
def send_email(to_email, subject, body):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    
    if not sender_email or not sender_password:
        return "Email simulated (Credentials not set): " + body

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email

        # Connect to Gmail Server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {e}"

# --- BOOKING TOOL ---
@tool
def create_booking_tool(name: str, email: str, phone: str, service_type: str, date: str, time: str):
    """
    Use this tool ONLY when the user explicitly confirms they want to book.
    Inputs: name, email, phone, service_type, date (YYYY-MM-DD), time.
    """
    
    # 1. Save to Database
    booking_id = add_booking(name, email, phone, service_type, date, time)
    
    # 2. Prepare Email Content
    email_subject = f"Booking Confirmation - #{booking_id}"
    email_body = f"""
    Dear {name},
    
    Your booking for '{service_type}' has been confirmed!
    
    Booking ID: {booking_id}
    Date: {date}
    Time: {time}
    
    Thank you for choosing JetSet Aviation.
    """
    
    # 3. Send Email
    email_status = send_email(email, email_subject, email_body)
    
    return f"Booking ID {booking_id} created successfully. {email_status}"