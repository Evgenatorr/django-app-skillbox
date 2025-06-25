from django.core.exceptions import ValidationError


def starting_with_letter(value: str):
    if not value[0].isalpha():
        raise ValidationError(message="The product name must begin with the letter")
