import datetime as dt

from django.core.exceptions import ValidationError


def year_validate(value):
    if value > dt.date.today().year:
        raise ValidationError(
            'Год выпуска не может быть больше текущего'
        )
    return value
