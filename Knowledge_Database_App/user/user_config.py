"""
User authentication information requirement settings.
"""

PASS_REGEX = r"(?!.*[\\\"])(?=.{8,160})(?=.*[a-zA-Z])(?:(?=.*[0-9])|(?=.*[!#$%&?])+)"
USER_NAME = r"(?!.*[\\\"])(?:\S{2,}\s{1}\S{2,})+"
