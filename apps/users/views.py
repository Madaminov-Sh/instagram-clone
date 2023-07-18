import datetime

from .import serializers
from .models import User, DONE, CODE_VERIFIED, NEW, VIA_EMAIL, VIA_PHONE
from apps.shared.utility import send_email, check_email_or_phone

from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import exceptions

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.core.exceptions import ObjectDoesNotExist


class SignUpApiView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = serializers.SignUpSerializer


class VerifyApi(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user, code)
        return Response(
            data={
                "success": True,
                "auth_status": user.auth_status,
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token']
            }
        )

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.datetime.now(), code=code, is_confirmed=False)
        print(f'this is verifies: {verifies}')
        user.refresh_from_db() 
        if not verifies.exists():
            print('not verifies, sharti bajarildi')
            data = {
                'message': "Tasdiqlash kodi xato"
            }
            raise exceptions.ValidationError(data)
        
            # Tasdiqlangan kodlarni yangilash
        update_code = verifies.update(is_confirmed=True)
        print(f"Updated verification codes: {update_code}")
        
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True


class GetNewVerification(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)

        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)

        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.email, code)

        # else:
        #     data = {
        #         "message": "xatolik bo'lishi mumkin, tekshirib ko'ring!"
        #     }
        #     raise exceptions.ValidationError(data)

        return Response(
            {
                "success": True,
                "message": f"tasdiqlash ko'di {user.auth_type}ga qaytadan yuborildi"
            }
        )                     


    @staticmethod
    def check_verification(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.datetime.now(), is_confirmed=False)
        if verifies.exists():
            data = {
                "message": "sizga yuborilgan tasdiqlash ko'di xozirda faol",
            }
            raise exceptions.ValidationError(data)
                    

class ChangeUserInformationView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = serializers.ChangeUserInformationSerializer

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        
        data = {
            "success": True,
            "message": "Muvafaqqiyatli yangilandi",
            "auth_status": self.request.user.auth_status,
        }
        return Response(data, status=200)
    

class ChangeUserPhotoView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def put(self, request, *args, **kwargs):
        serializer = serializers.ChangeUserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user, serializer.validated_data)
            return Response(
                {
                    "success": True,
                    "message": "foto muvaffaqitatli o'rnatildi",
                    "auth_status": user.auth_status
                }, status=200
            )
        return Response(serializer.errors, status=400)
    

class LoginView(TokenObtainPairView):
    serializer_class = serializers.LoginSerializer


class LoginRefreshView(TokenRefreshView):
    serializer_class = serializers.LoginRefreshSerializer


class LogoutView(APIView):
    serializer_class = serializers.LogoutSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            data = {
                "success": True,
                "message": "You are logout"
            }
            return Response(data, status=205)
        except TokenError:
            return Response(status=400)
        
    
class ForgotPasswordView(APIView):
    serializer_class = serializers.ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny, ]

    

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data.get('email_or_phone')
        user = serializer.validated_data.get('user')
        if check_email_or_phone(email_or_phone) == 'phone':
            code = user.create_verify_code(VIA_PHONE)
            send_email(email_or_phone, code)
        elif check_email_or_phone(email_or_phone) == 'email':
            code = user.create_verify_code(VIA_EMAIL)
            send_email(email_or_phone, code)

        return Response(
            {
                "success": True,
                'message': "Tasdiqlash kodi muvaffaqiyatli yuborildi",
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token'],
                "user_status": user.auth_status,
            }, status=200
        )

    
class ResetPasswordView(UpdateAPIView):
    serializer_class = serializers.ResetPasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        return self.request.user
    

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response({
    #         "success": True,
    #         "message": "Parol muvafaqiyatli o'rnatildi",
    #         "access": instance.token()["access"],
    #         "refresh": instance.token()["refresh_token"],
    #         "auth_status": instance.auth_status,
    #         "user_full_name": instance.full_name
    #     })

    # def perform_update(self, serializer):
    #     serializer.save()
    
    
    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordView, self).update(request, *args, **kwargs)
        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise exceptions.NotFound(detail="user not found")
        return Response(
            {
                "success": True,
                "message": "Parol muvafaqiyatli o'rnatildi",
                "access": user.token()["access"],
                "refresh": user.token()["refresh_token"],
                "auth_status": user.auth_status,
                "user_full_name": user.full_name
            }
        )