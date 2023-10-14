import re

from django.core.exceptions import ValidationError

SLUG_VALID = re.compile(r'^[\w.@+-]+')


def validate_slug(slug):
    if not SLUG_VALID.fullmatch(slug):
        raise ValidationError(
            'Можно использовать только буквы, цифры и "@.+-_".'
        )
