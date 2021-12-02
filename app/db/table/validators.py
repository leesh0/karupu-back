import validators
from validators.utils import ValidationFailure


def URL_VALIDATOR(v):
    if validators.url(v):
        return True
    else:
        raise ValidationFailure(validators.url, {"v": "invalid url"})
