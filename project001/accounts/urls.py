from django.urls import path
from . import views

urlpatterns = [
    path('save_profile/', views.save_profile, name='save_profile'),
    path('get_profile/', views.get_profile, name='get_profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path('send-register-otp/', views.send_register_otp, name='send_register_otp'),

]
