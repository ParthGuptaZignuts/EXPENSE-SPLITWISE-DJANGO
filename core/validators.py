from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class MinimumComplexityValidator:
    def __init__(self, min_uppercase=0, min_digit=0, min_special=0):
        self.min_uppercase = min_uppercase
        self.min_digit = min_digit
        self.min_special = min_special

    def validate(self, password, user=None):
        if sum(1 for c in password if c.isupper()) < self.min_uppercase:
            raise ValidationError(
                _("This password must contain at least %(min_uppercase)d uppercase letters.") % {'min_uppercase': self.min_uppercase},
                code='password_no_upper',
            )
        if sum(1 for c in password if c.isdigit()) < self.min_digit:
            raise ValidationError(
                _("This password must contain at least %(min_digit)d digits.") % {'min_digit': self.min_digit},
                code='password_no_digit',
            )
        if sum(1 for c in password if not c.isalnum()) < self.min_special:
            raise ValidationError(
                _("This password must contain at least %(min_special)d special characters.") % {'min_special': self.min_special},
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(min_uppercase)d uppercase letters, "
            "%(min_digit)d digits, and %(min_special)d special characters." % {
                'min_uppercase': self.min_uppercase,
                'min_digit': self.min_digit,
                'min_special': self.min_special,
            }
        )