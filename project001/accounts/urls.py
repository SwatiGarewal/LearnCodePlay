from django.urls import path
from . import views

urlpatterns = [
    path('save_profile/', views.save_profile, name='save_profile'),
    path('get_profile/', views.get_profile, name='get_profile'),   
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]