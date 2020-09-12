from twilio.twiml.messaging_response import MessagingResponse

def sms_http(request):
    number = request.form.get('From')
    message_body = request.form.get('Body')
    resp = MessagingResponse()
    resp.message('Hello {}, you said: {}'.format(number, message_body))
    return str(resp)
