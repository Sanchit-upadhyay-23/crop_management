def user_creation_validator(payload = None):
    null_vars = {key: value for key, value in payload.items() if value is None}
    return null_vars
