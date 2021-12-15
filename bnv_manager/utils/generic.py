import re


def enforce_password_policy(password):
    return len(password) >= 12 and re.search(r"\W", password)
