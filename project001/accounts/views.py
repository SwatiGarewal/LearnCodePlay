from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from .models import Profile
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == "POST":
        next_url = request.POST.get("next") 
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists ❌")
            return redirect(next_url if next_url else 'home')
            

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()

        messages.success(request, "Registered successfully ✅")
        return redirect(f"{next_url}?showLogin=true")

    return render(request, 'home/home.html')


def login_view(request):
    if request.method == 'POST':
        next_url = request.POST.get("next") 
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Yahan pehle 'game' tha, ise badal kar 'home' kar dein
            return redirect(next_url if next_url else 'home')   
        else:
            messages.error(request, 'Invalid credentials ❌')
            # Yahan aapka 'hom' likha tha, ise bhi 'home' karein
            return redirect(next_url if next_url else 'home')       

    return redirect('home')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def get_profile(request):
    # User ki profile lo, agar nahi hai toh create karo
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    return JsonResponse({
        "name": request.user.username,
        "email": request.user.email,
        "mobile": profile.mobile or "",
        "gender": profile.gender or "",
        "dob": str(profile.dob) if profile.dob else "",
        "profession": profile.profession or "",
        "image_url": profile.image.url if profile.image else "/static/home/image/default.png"
    })

@login_required
def save_profile(request):
    if request.method == "POST":
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # Text data handle karein
        profile.mobile = request.POST.get('mobile')
        profile.gender = request.POST.get('gender')
        profile.dob = request.POST.get('dob') if request.POST.get('dob') else None
        profile.profession = request.POST.get('profession')
        
        # Image handle karein
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
            
        profile.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)