from dataclasses import dataclass


@dataclass
class UserLogin:
    email: str
    password: str


@dataclass
class UserRegistration(UserLogin):
    username: str
