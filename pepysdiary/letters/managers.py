from django.db import models

from pepysdiary.common.managers import ReferredManagerMixin


class LetterManager(models.Manager, ReferredManagerMixin):
    pass
