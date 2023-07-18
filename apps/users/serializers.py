from apps.shared.utility import check_email_or_phone, send_email, check_user_type
from .models import User, UserComfirmation, VIA_EMAIL, VIA_PHONE, NEW, DONE, CODE_VERIFIED, PHOTO_STEP

from rest_framework import exceptions
from rest_framework.authentication import authenticate
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from django.db.models import Q
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator   



class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id', 'auth_type', 'auth_status')

        extra_kwargs = {
            'auth_type': {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False}
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        print('user', user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            print('your code ',code)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
            """vaqtimcha ishlatilmaydi"""
            # send_phone(user.phone_number, code)
        user.save()
        print(f'this is save user: {user}')
        return user


    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        print('data is validated')
        return data
    

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number'))
        input_type = check_email_or_phone(user_input)

        if input_type == "email":
            data = {
                "email":user_input,
                'auth_type': VIA_EMAIL
            }
        elif input_type == "phone":
            data = {
                'phone_number':user_input,
                "auth_type":VIA_PHONE
            }
        else:
            data = {
                "success":False,
                "messages":"email yoki telefon raqamingizni kiriting!"
            }
            raise exceptions.ValidationError(data)
        return data 

    def validate_email_phone_number(self, value):
        value = value.lower()
        print(f'bu value: {value}')

        if value and User.objects.filter(email=value).exists():
            data = {
                'success': False,
                'message': 'bu email allaqachon mavjud',
            }    
            raise exceptions.ValidationError(data)
            
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                'success': False,
                'message': 'bu raqam allaqachon mavjud',
            }    
            raise exceptions.ValidationError(data)

        return value
    
    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data
    

class ChangeUserInformationSerializer(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    def validate(self, data):
        password = data.get("password", None)
        confirm_password = data.get("confirm_password", None)
        
        if confirm_password != password:
            raise exceptions.ValidationError(   
                {
                    "success": False,
                    "message": "parol bir xil emas"
                }
            )
        if password:
            validate_password(confirm_password)

        return data
    
    def validate_username(self, username):
        if len(username) < 5 or len(username) > 30:
            raise exceptions.ValidationError(
                {
                    "success": False,
                    "message": "Bu username'da 5 tadan kam, yoki 30 dan ko'p belgilardan foydalanilgan"
                }
            )
        
        elif username.isdigit():
            raise exceptions.ValidationError(
                {
                    "success": False,
                    "message": "username yaroqli emas, to'liq raqamlardan foydalanilgan"
                }
            )
        return username
    
    def first_amd_last_name_validator(self, data):
        first_name = data.get("first_name", None)
        last_name = data.get("last_name", None)

        if first_name > 15 and  last_name > 15:
            raise exceptions.ValidationError(
                {
                    "success": False,
                    "message": "etiborli bo'ling, first name yoki last name 15 ta belgidan ko'p bo'lmasligi kerak"
                }
            )
        return data
    
    def numeric_first_last_name_validator(self, data):
        first_name = data.get("first_name", None)
        last_name = data.get("last_name", None)
        if first_name.isdigit() and last_name.isdigit():
            raise exceptions.ValidationError(
                {
                    "success": False,
                    "message": "first name yoki last name raqamlardan iborat bo'lmasligi kerak"
                }
            )
        return data
    
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.username = validated_data.get("username", instance.username)
        instance.password = validated_data.get("password", instance.password)
        
        if validated_data.get("password"):
            instance.set_password(validated_data.get("password"))
        
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance
    

class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(
        allowed_extensions=["img", "jpg", "jpeg", "png", "heic", "heif"]
    )])

    def update(self, instance, validated_data):
        photo = validated_data.get("photo")

        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_STEP
            instance.save()
        return instance
    

    "login qism"
class LoginSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def auth_valedate(self, data):
        user_input = data.get("userinput")
        if check_user_type(user_input) == "username":
            username = user_input
        elif check_user_type(user_input) == "email":
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_type(user_input) == "phone":
            user = self.get_user(phone_number=user_input)
            username = user.username
            
        else:
            data = {
                "success": False, 
                "message": "siz email, phone yoki username kiritmadingiz"
            }
            raise exceptions.ValidationError(data)
        
        authentication_kwargs = {
            self.username_field: username,
            "password": data['password']
        }

        current_user = User.objects.filter(username__iexact=username).first()
        if current_user is not None and current_user.auth_status in [NEW, CODE_VERIFIED]:
            raise exceptions.ValidationError(
                {
                    "success": False,
                    "message": "ro'yxatdan to'liq o'tilmagan"
                }
            )
        user = authenticate(**authentication_kwargs )
        if user is not None:
            self.user = user
        else:
            raise exceptions.ValidationError(
                {
                    "success": False,
                    "message": "login yoki parol noto'g'ri kiritilgan. tehshirib qaytadan urinib ko'ring"
                }
            )
        
    def validate(self, data):
        self.auth_valedate(data)
        if self.user.auth_status not in [DONE, PHOTO_STEP]:
            raise exceptions.PermissionDenied("ro'xyatdan to'liq o'tilmagan")
        data = self.user.token()
        data["auth_status"] = self.user.auth_status
        data["fullname"] = self.user.full_name
        return data

    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise exceptions.ValidationError(
                {
                    "success": False,
                    "message": "bunday foydalanuvchi topilmadi"
                }
            )
        return users.first()
    

class LoginRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instace = AccessToken(data["access"])
        user_id = access_token_instace["user_id"]
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone', None)
        if email_or_phone is None:
            raise exceptions.ValidationError(
                {
                    "success": False,
                    "message": "email yoki telefon raqam kiritilishi shart"
                }
            )
        user = User.objects.filter(Q(phone_number=email_or_phone) | Q(email=email_or_phone))
        if not user.exists():
            raise exceptions.NotFound(detail="user not found")
        attrs['user'] = user.first()
        return attrs
    

class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ("id", "password", "confirm_password")

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('password', None)

        if confirm_password != password:
            raise exceptions.ValidationError(
                {
                    "success": False,
                    "message": "password va confirm password bir xil emas"
                }
            )
        if password:
            validate_password(password)
        return data
    

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        return super(ResetPasswordSerializer, self).update(instance, validated_data)
    

# {
#     "first_name": "shohjahon",
#     "last_name": "madaminov",
#     "username": "shohjahon1",
#     "password": "loptop123",
#     "confirm_password": "loptop123"
# }

# {
#   "email_phone_nummber": "+998945545585"
# }

# {
#   "code": ""
# }