import secrets
import string
from aiosmtplib import send # type: ignore
from email.message import EmailMessage
import os


SMTP_EMAIL = os.getenv("SMTP_EMAIL")
EMAIL_APP_PASS = os.getenv("EMAIL_PASS")

## function to generate password reset token 
def generate_reset_token(length=32): 
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))




# Function to render the template
# def render_template(template_name: str, context: dict) -> str:
#     # Load the template and render it with the given context
#     template = templates.get_template(template_name)
#     return template.render(context)

EMAIL_SUBJECTS = {
    "Welcome": "Welcome to the Todo App!",
    "Password_reset": "Reset Your Password",
    "Password_Changed" : "Password Changed!"
}

EMAIL_TEMPLATES = {
    "Welcome": "welcome_email.html",
    "Password_reset": "password_reset_email.html",
    "Password_Changed" : "password_changed_email.html"
}

# Function to send email
async def send_email(email_type, username, email: str, link:str = "http://localhost:8000/"):
    context = {
        "username": username,
        "link": link
    }

    # Render the HTML content using the Jinja2 template
    # html_content = render_template(EMAIL_TEMPLATES[email_type], context)

    # Construct the email message
    message = EmailMessage()
    message["From"] = SMTP_EMAIL  # Sender email
    message["To"] = email  # Recipient email
    message["Subject"] = EMAIL_SUBJECTS[email_type]

    # Set the email content as HTML
    message.set_content("test", subtype='html')

    # Send the email asynchronously using aiosmtplib
    await send(message, hostname="smtp.gmail.com", port=587, start_tls=True,
               username=SMTP_EMAIL, password=EMAIL_APP_PASS)
