from django.urls import path
from home import views as home_views
from accounts import views as accounts_views

urlpatterns = [
    

    # Home Views
    path('', home_views.home, name='home'),
    path('game/', home_views.game, name='game'),
    path('quiz/', home_views.quiz, name='quiz'),
    path('matchdashboard/', home_views.matchdashboard, name='matchdashboard'),
    path('mousedashboard/', home_views.mousedashboard, name='mousedashboard'),
    path('tttdashboard/', home_views.tttdashboard, name='tttdashboard'),
    path('snakedashboard/', home_views.snakedashboard, name='snakedashboard'),
]
