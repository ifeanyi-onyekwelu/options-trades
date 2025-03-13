from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_email(subject, template_name, context, recipient_list):
    """
    Helper function to send an email with a template.

    :param subject: Email subject
    :param template_name: Name of the template file (HTML)
    :param context: Context variables to be used in the template
    :param recipient_list: List of recipients
    """
    # Render the HTML content from the template and context
    message = render_to_string(template_name, context)

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
        html_message=message,  # Adding the HTML version of the message
    )
