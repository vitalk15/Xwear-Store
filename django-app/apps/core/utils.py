from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


# Универсальный метод для отправки HTML-писем
def send_custom_email(subject, template_name, context, to_email):
    # template_name: путь к шаблону (напр. 'orders/emails/order_received.html')
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=f"XWEAR: {subject}",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email] if isinstance(to_email, str) else to_email,
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
