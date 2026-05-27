from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home/home.html')


def game(request):
    return render(request, 'home/game.html')

def quiz(request):
    return render(request, 'home/quiz.html')

def matchdashboard(request):
    return render(request, 'home/matchdashboard.html')

def mousedashboard(request):
    return render(request, 'home/mousedashboard.html')

def snakedashboard(request):
    return render(request, 'home/snakedashboard.html')

def tttdashboard(request):
    return render(request, 'home/tttdashboard.html')

