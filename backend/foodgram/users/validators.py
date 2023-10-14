import re

from django.core.exceptions import ValidationError

NAME_VALID = re.compile(r'^[\w.@+-]+')


def validate_username(name):
    if name == 'me':
        raise ValidationError('Имя пользователя "me" использовать нельзя!')
    if not NAME_VALID.fullmatch(name):
        raise ValidationError(
            'Можно использовать только буквы, цифры и "@.+-_".'
        )
