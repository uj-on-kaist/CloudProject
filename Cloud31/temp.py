#send email
send_mail('Test', 'This is a test', 'hello<ujlikes@gmail.com>',['uijune.jeong@gmail.com'])


#email template

#TODO: NOT WORKING!!, CHECK THIS
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

htmly     = get_template('email_test.html')

d = Context({ 'user_name': 'ujlikes' })

subject, from_email, to = 'hello', '¡§¿«¡ÿ<ujlikes@gmail.com>', 'uijune.jeong@gmail.com'
html_content = htmly.render(d)
msg = EmailMultiAlternatives(subject, '', from_email, [to])
msg.attach_alternative(html_content, "text/html")
msg.send()


msg = EmailMessage('Test', html_content, 'hello<ujlikes@gmail.com>',['uijune.jeong@gmail.com'])
msg.content_subtype = "html"  # Main content is now text/html
msg.send()

"""