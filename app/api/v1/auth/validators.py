from pydantic import BaseModel, EmailStr, validator
from ....models.user import User


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    password_confirmation: str
    name: str

    @validator('email')
    def validate_email(cls, email):
        if User.exists(User.email == email):
            raise ValueError('email already exists')
        return email

    @validator('username')
    def validate_username(cls, username):
        if not username.isalnum():
            raise ValueError('username must be alphanumeric')
        if User.exists(User.username == username):
            raise ValueError('username already exists')
        return username

    @validator('password_confirmation')
    def confirm_password(cls, password_confirmation, values, **kwargs):
        if 'password' in values and password_confirmation != values['password']:
            raise ValueError('passwords do not match')
        return password_confirmation
    
    @validator('password')
    def password_validation(cls, password):
        if len(password) < 8:
            raise ValueError('password must be at least 8 characters')
        if password.isalnum():
            raise ValueError('password must contain at least one special character')
        if not any(char.isnumeric() for char in password):
            raise ValueError('password should have at least one number')
        if not any(char.isalpha() for char in password):
            raise ValueError('password should have at least one letter')
        return password


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    user: User
    current_password: str
    new_password: str

    @validator('current_password')
    def validate_current_password(cls, current_password, values):
        if not bcrypt.check_password_hash(values['user'].password, current_password):
            raise ValueError('Invalid current password. Please try again.')
        return current_password

    class Config:
        arbitrary_types_allowed = True


class PasswordReset(BaseModel):
    token: str
    password: str


class PasswordRecovery(BaseModel):
    email: EmailStr