from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    MeView,
    VerifyEmailView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)
from .services.phone_auth import PhoneLoginView, VerifyOTPView
from .services.two_factor import Enable2FAView, Verify2FAView
from .services.google_auth import GoogleLoginView


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('login/refresh/', TokenRefreshView.as_view()),
    path('me/', MeView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('password-reset-request/', PasswordResetRequestView.as_view()),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('change-password/', ChangePasswordView.as_view()),
    path('phone-login/', PhoneLoginView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path('enable-2fa/', Enable2FAView.as_view()),
    path('verify-2fa/', Verify2FAView.as_view()),
    path('google-login/', GoogleLoginView.as_view()),
]
