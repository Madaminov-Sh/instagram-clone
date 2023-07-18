from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('login/refresh/', views.LoginRefreshView.as_view()), 
    path('logout/',views.LogoutView.as_view()),
    path('signup/', views.SignUpApiView.as_view()),
    path('verify/', views.VerifyApi.as_view()),
    path('get/verify/', views.GetNewVerification.as_view()),
    path('change/information/',views. ChangeUserInformationView.as_view()),
    path('update/photo/', views.ChangeUserPhotoView.as_view()),
    path('forgot/password/', views.ForgotPasswordView.as_view()),
    path('reset/password/', views.ResetPasswordView.as_view())
]
