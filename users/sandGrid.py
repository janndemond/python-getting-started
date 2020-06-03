# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError
def sentEmail ():
    message = Mail(
        from_email='info@theweather.software',
        to_emails='janndemond@gmail.com',
        subject='Sending with Twilio SendGrid is Fun',

        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.to_dict)
