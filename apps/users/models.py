from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator   

from rest_framework_simplejwt.tokens import RefreshToken

from datetime import datetime, timedelta
import uuid
import random

from apps.shared.models import BaseModel


ORDINARY_USER, MANAGER, ADMIN = ('ordinary_user', 'manager', 'admin')
VIA_PHONE, VIA_EMAIL = ('via_phone', 'via_email')   
NEW, CODE_VERIFIED, DONE, PHOTO_STEP = ('new','code_verified','done','photo_step')


class User(AbstractUser, BaseModel):
    '''User model in my users app'''
    USER_ROLE_CHOICE = (
    (ORDINARY_USER, ORDINARY_USER),
    (MANAGER, MANAGER),
    (ADMIN, ADMIN)
    )

    AUTH_TYPE_CHOICE = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )

    AUTH_STATUS = (
        (NEW, NEW),
       ( CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP)
    )

    user_rules = models.CharField(max_length=50, choices=USER_ROLE_CHOICE, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=50, choices=AUTH_TYPE_CHOICE)
    auth_status = models.CharField(max_length=50, choices=AUTH_STATUS, default=NEW)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=15, null=True, unique=True, blank=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['img', 'jpg', 'jpeg', 'heic', 'heif'])])

    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 100) % 10) for _ in range(4)])
        UserComfirmation.objects.create(
            user_id = self.id,
            verify_type = verify_type,
            code = code
        )
        return code
    
    def check_username(self):
        if not self.username:
            temp_username = f"instagram-{uuid.uuid4().__str__().split('-')[-1]}"
            while User.objects.filter(username = temp_username):
                temp_username = f"{temp_username}{random.randint(0,9)}"
            self.username = temp_username
    
    def check_email(self):
        if self.email:
            normalize_email = self.email.lower()
            self.email = normalize_email

    def check_pass(self):
        if not self.password:
            temp_password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh)
        }
    
    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs  )

    def clean(self):
        self.check_email()
        self.check_username()
        self.check_pass()
        self.hashing_password()


PHONE_EXPIRE = 5
EMAIL_EXPIRE = 2

      
class UserComfirmation(BaseModel):
    AUTH_TYPE_CHOICES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )
    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=50, choices=AUTH_TYPE_CHOICES)
    user = models.ForeignKey(User, models.CASCADE, related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)    

    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            print(f"this is verify type: {self.verify_type}")
            self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
            print(f"this is expiration time for email: {self.expiration_time}")
        else:
            print(f"this is verify type: {self.verify_type}")
            self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
            print(f"this is expiration time for phone: {self.expiration_time}")
        super(UserComfirmation, self).save(*args, **kwargs)

    def __str__(self) :
        return str(self.user.__str__())