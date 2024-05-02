import re
import string

from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template import loader


def validate_person_name(value):
    """
    For testing users' names.
    """
    disallowed_names = [
        "anon",
        "anonymous",
        "admin",
        "administrator",
        "guest",
        "help",
        "moderator",
        "owner",
        "postmaster",
        "root",
        "superuser",
        "support",
        "sysadmin",
        "systemadministrator",
        "systemsadministrator",
        "user",
        "webadmin",
        "samuelpepys",
        "pepys",
        "sampepys",
        "keithwright",
        "warrenkeithwright",
    ]

    # Remove all punctuation and space from the name before comparing it to the
    # disallowed names.
    exclude = list(string.punctuation)
    exclude.append(" ")
    test_value = "".join(ch for ch in value if ch not in exclude).lower()

    if test_value in disallowed_names:
        msg = f"{value} is not an available name"
        raise ValidationError(msg)

    # We allow one or more characters.
    # There can be one or more spaces after that sequence, with other
    # characters (including spaces) following.
    if re.match(r"^[\w.-_]+(?:\s+[\w\s.-_]+)?$", value) is None:
        msg = f"{value} contains invalid characters or formatting"
        raise ValidationError(msg)


def email_list(to_list, template_path, from_address, context_dict):
    """
    This and the following accessor methods from
    http://stackoverflow.com/questions/2051526/email-templating-in-django/2051610#2051610

    The template should have sections like this:
        {% block subject %}{% endblock %}
        {% block plain %}{% endblock %}
        {% block html %}{% endblock %}
    """
    from django.core.mail import EmailMessage, get_connection
    from django.template import Context, loader

    nodes = dict(
        (n.name, n)
        for n in loader.get_template(template_path).template.nodelist
        if n.__class__.__name__ == "BlockNode"
    )

    context = Context(context_dict)

    def render_node(node, con):
        return nodes[node].render(con)

    connection = get_connection(username=None, password=None, fail_silently=False)

    messages = [
        EmailMessage(
            render_node("subject", context),
            render_node("plain", context),
            from_address,
            recipient,
            connection=connection,
            headers={
                "X-Auto-Response-Suppress": "OOF",
                "Auto-Submitted": "auto-generated",
            },
        )
        for recipient in to_list
    ]

    return connection.send_messages(messages)


def send_email(
    to_address, from_address, subject_template_name, email_template_name, context
):
    """
    Send a plaintext transactional email.

    Args:
    to_address - The email address to send To
    from_address - Email address to send From
    subject_template_name - Path to a plaintext template for the email subject
    email_template_name - Path to a plaintext template for the email body
    context - Context dictionary passed to the template
    """

    subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = "".join(subject.splitlines())

    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMessage(
        subject,
        body,
        from_address,
        [to_address],
        headers={
            "X-Auto-Response-Suppress": "OOF",
            "Auto-Submitted": "auto-generated",
        },
    )

    email_message.send()
