from django.core.validators import EmailValidator
from django.db import models

from .validators import validate_phone_number


class User(models.Model):
    username = models.CharField(max_length=50, unique=True, db_index=True, null=False)
    password_hash = models.CharField(null=False)
    email = models.EmailField(
        unique=True, null=False,
        validators=[EmailValidator(message='Enter a valid email')]
    )
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50,  null=True, blank=True)
    phone_number = models.CharField(
        max_length=15, null=True, blank=True, validators=[validate_phone_number])
    joined_dt = models.DateTimeField(
        verbose_name='Date and time of registration', auto_now_add=True
    )
    last_modified_dt = models.DateTimeField(
        verbose_name='Date and time of last profile updating', auto_now=True
    )

    class Meta:
        db_table = "auth\".\"user"
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
