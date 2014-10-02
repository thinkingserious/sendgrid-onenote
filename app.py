from flask import Flask, request
import sendgrid
import json
import requests
import os
app = Flask(__name__)

SENDGRID_USER = os.getenv('SENDGRID_USER')
SENDGRID_PASS = os.getenv('SENDGRID_PASS')
ONENOTE_TOKEN = os.getenv('ONENOTE_TOKEN')

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

sg = sendgrid.SendGridClient(SENDGRID_USER, SENDGRID_PASS)

# Receive a POST from the SendGrid Event Webhook
@app.route('/event', methods = ['POST'])
def event():
    message = sendgrid.Mail()
    message.add_to('Elmer Thomas <elmer@sendgrid.com>')
    message.set_subject('Bounce Alert')
    data = request.stream.read().decode("utf-8")
    data = json.loads(data)

    for i in range(len(data)):
        # For a list of all event types see: https://sendgrid.com/docs/API_Reference/Webhooks/event.html
        event = data[i]['event']
        if event == "bounce":
            # Create and post the OneNote message
            url = "https://www.onenote.com/api/v1.0/pages"
            auth = 'Bearer ' + ONENOTE_TOKEN
            body = "An email from " + data[i]['email'] + " bounced. You might want to do something about that :)"
            payload = "<!DOCTYPE HTML><html><head><title>Bounced Email Alert</title></head>"
            payload += "<body>" + body + "</body></html>"
            headers = {'Authorization':auth,'Content-type':'text/html'}
            res = requests.post(url, headers=headers, data=payload)
            
            # Send an email alert
            mail = "An email sent to " + data[i]['email'] + " bounced. Return value from OneNote is: " + res.text
            message.set_html(mail)
            message.set_text(mail)
            message.set_from('Elmer Thomas <elmer.thomas@sendgrid.com>')
            status, msg = sg.send(message)

    return "HTTP/1.1 200 OK"

@app.route('/', methods = ['GET'])
def hello():
    """Renders a sample page."""
    return "Hello Universe!"

@app.route('/tos', methods = ['GET'])
def tos():
    return "Terms of Service Placeholder."

@app.route('/privacy', methods = ['GET'])
def privacy():
    return "Privacy Policy Placeholder."

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
