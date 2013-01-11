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
        'sampepys', ]

    # Remove all punctuation and space from the name before comparing it to the
    # disallowed names.
    exclude = list(string.punctuation)
    exclude.append(' ')
    test_value = ''.join(ch for ch in value if ch not in exclude).lower()

    if test_value in disallowed_names:
        raise ValidationError(u'%s is not an available name' % value)
