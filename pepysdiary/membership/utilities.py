import re
import string

from django.core.exceptions import ValidationError


def validate_person_name(value):
    """
    For testing users' names.
    """
    disallowed_names = ['anon', 'anonymous', 'admin', 'administrator',
        'guest', 'help', 'moderator', 'owner', 'postmaster', 'root',
        'superuser', 'support', 'sysadmin', 'systemadministrator',
        'systemsadministrator', 'user', 'webadmin', 'samuelpepys', 'pepys',
        'sampepys', "keithwright", "warrenkeithwright", ]

    # Remove all punctuation and space from the name before comparing it to the
    # disallowed names.
    exclude = list(string.punctuation)
    exclude.append(' ')
    test_value = ''.join(ch for ch in value if ch not in exclude).lower()

    if test_value in disallowed_names:
        raise ValidationError('%s is not an available name' % value)

    # We allow one or more characters.
    # There can be one or more spaces after that sequence, with other
    # characters (including spaces) following.
    if re.match(r'^[\w.-_]+(?:\s+[\w\s.-_]+)?$', value) is None:
        raise ValidationError('%s contains invalid characters or formatting'
                                                                    % value)


def email_list(to_list, template_path, from_address, context_dict):
    """
    This and the following accessor methods from
    http://stackoverflow.com/questions/2051526/email-templating-in-django/2051610#2051610

    The template should have sections like this:
        {% block subject %}{% endblock %}
        {% block plain %}{% endblock %}
        {% block html %}{% endblock %}
    """
    from django.core.mail import send_mail
    from django.template import loader, Context

    nodes = dict((n.name, n) for n in loader.get_template(
                template_path).template if n.__class__.__name__ == 'BlockNode')
    con = Context(context_dict)
    r = lambda n: nodes[n].render(con)

    for address in to_list:
        send_mail(r('subject'), r('plain'), from_address, [address, ])


def email(to, template_path, from_address, context_dict):
    """
    Send an email to a specific email address.
    """
    return email_list([to, ], template_path, from_address, context_dict)


def email_user(user, template_path, from_address, context_dict):
    """
    Send an email to a specific User object.
    """
    return email_list([user.email, ], template_path, from_address,
                                                                context_dict)


def email_users(user_list, template_path, from_address, context_dict):
    """
    Send an email to a list of User objects.
    """
    return email_list([user.email for user in user_list], template_path,
                                                from_address, context_dict)

