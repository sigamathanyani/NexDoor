def password_validator(password: str) -> str | None:
    if len(password) < 8:
        return 'Password length must be at least 8 characters'
    
    if not any(char.isdigit() for char in password):
        return 'Password must contain at least one number'
    
    if not any(char.isupper() for char in password):
        return 'Password must contain at least one uppercase letter'
    
    if not any(char.islower() for char in password):
        return 'Password must contain at least one lower case'
    
    if not any(char in '~`!@#$%^&*()_+=-[/?.>,<]' for char in password):
        return 'Password must contain at least one special character'
    
    return None

def string_validator(name: str, field: str) -> str | None:
    if not isinstance(name, str):
        return f'{field} must be a string'

    if len(name.strip()) < 1:
        return f'{field} cannot be empty'
    
    return None
    