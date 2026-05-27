from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('game/', views.game, name='game'),
    path('quiz/', views.quiz, name='quiz'),
    path('matchdashboard/', views.matchdashboard, name='matchdashboard'),
    path('mousedashboard/', views.mousedashboard, name='mousedashboard'),
    path('tttdashboard/', views.tttdashboard, name='tttdashboard'),
    path('snakedashboard/', views.snakedashboard, name='snakedashboard'),
]