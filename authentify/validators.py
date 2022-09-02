from django.core import validators
from django.utils.translation import gettext_lazy as _

username_regex = validators.RegexValidator(
    regex=r"^(?!.*\.\.)(?!.*\.$)[^\W][\w.]{0,30}$",
    message=_(
        """
    Usernames can contain characters a-z, 0-9, underscores and periods. 
    The username cannot start with a period nor end with a period. 
    It must also not have more than one period sequentially. 
    Max length is 31 chars.
    """
    ),
)
