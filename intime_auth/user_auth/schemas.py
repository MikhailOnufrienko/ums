from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserLogin:
    email: str
    password: str


@dataclass
class UserRegistration(UserLogin):
    username: str


@dataclass
class UserProfile:
    username: str
    email: str
    full_name: str
    phone_number: str
    joined_dt: datetime
    last_modified: datetime


@dataclass
class EditProfile:
    first_name: str
    last_name: str
    phone_number: str
