from dataclasses import dataclass


@dataclass
class UserRegistration:
    username: str
    password: str
    email: str


