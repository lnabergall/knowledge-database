"""
User authentication information requirement settings.
"""

import re


PASS_REGEX = re.compile(
    r"(?!.*[\\\"])((?=.*[a-zA-Z])(?=.*[0-9!#$%&?]).{8,160})")
USER_NAME_REGEX = re.compile(r"(?!.*[\\\"])(?:\S{2,}\s{1}\S{2,})+")
