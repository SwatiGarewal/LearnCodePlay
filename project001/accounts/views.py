import json
import random
import threading
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from .models import GameComment, Profile


# ---------------------------------------------------------
# 🚀 FAST ASYNC EMAIL THREADING SETUP
# ---------------------------------------------------------
class EmailThread(threading.Thread):

  def __init__(self, subject, message, recipient_list):
    self.subject = subject
    self.message = message
    self.recipient_list = recipient_list
    threading.Thread.__init__(self)

  def run(self):
    try:
        print("HOST =", settings.EMAIL_HOST)
        print("PORT =", settings.EMAIL_PORT)
        print("USER =", settings.EMAIL_HOST_USER)
        print("FROM =", settings.DEFAULT_FROM_EMAIL)
        print("TLS =", settings.EMAIL_USE_TLS)

        send_mail(
            self.subject,
            self.message,
            settings.DEFAULT_FROM_EMAIL,
            self.recipient_list,
            fail_silently=False,
        )

        print("OTP Email Sent Successfully")

    except Exception as e:
        print("EMAIL ERROR:", str(e))
        raise


from django.core.mail import send_mail
import traceback

def send_otp_fast(subject, message, recipient_email):
    try:
        print("HOST =", settings.EMAIL_HOST)
        print("PORT =", settings.EMAIL_PORT)
        print("USER =", settings.EMAIL_HOST_USER)
        print("FROM =", settings.DEFAULT_FROM_EMAIL)
        print("PASSWORD =", bool(settings.EMAIL_HOST_PASSWORD))

        sent = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )

        print("MAIL SENT =", sent)

    except Exception as e:
        print(traceback.format_exc())
        raise


# ---------------------------------------------------------
# 🔑 REGISTRATION & REGISTER OTP VIEWS
# ---------------------------------------------------------
def send_register_otp(request):
  if request.method != 'POST':
    return JsonResponse({'status': 'error', 'message': 'Invalid Request'})

  email = request.POST.get('email', '').strip()
  if not email:
    return JsonResponse(
        {'status': 'error', 'message': 'Email address is required.'}
    )

  # Check if email is already registered
  if User.objects.filter(email=email).exists():
    return JsonResponse({
        'status': 'error',
        'message': 'This email is already registered! 🛑',
    })

  # Generate 6-digit dynamic OTP
  otp = str(random.randint(100000, 999999))

  # Session storage setup
  request.session['reg_email'] = email
  request.session['reg_otp'] = otp
  request.session['reg_otp_time'] = time.time()
  request.session.modified = True

  subject = 'LearnCodePlay Signup Verification OTP'
  message = f"""Hello Gamer,

Welcome to LearnCodePlay! Your registration verification code is: {otp}

This key is valid for 5 minutes.

Thanks,
LearnCodePlay Team"""

  # ⚡ FAST BACKGROUND EMAIL SENDING
  send_otp_fast(subject, message, email)

  return JsonResponse(
      {'status': 'success', 'message': 'OTP sent successfully.'}
  )


def register_view(request):
  if request.method == 'POST':
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    user_otp = request.POST.get('otp', '').strip()

    session_otp = request.session.get('reg_otp')
    session_email = request.session.get('reg_email')
    otp_time = request.session.get('reg_otp_time')

    if not username or not email or not password or not user_otp:
      return JsonResponse({
          'status': 'error',
          'message': 'All database parameters are required! ❌',
      })

    if User.objects.filter(username=username).exists():
      return JsonResponse(
          {'status': 'error', 'message': 'Username already taken! 🛑'}
      )

    # OTP Expiry tracking (5 minutes = 300s)
    if not session_otp or time.time() - otp_time > 300:
      return JsonResponse({
          'status': 'error',
          'message': 'Verification key has expired. Please resend.',
      })

    if user_otp != session_otp or email != session_email:
      return JsonResponse(
          {'status': 'error', 'message': 'Invalid verification code sequence! ❌'}
      )

    try:
      user = User.objects.create_user(
          username=username, email=email, password=password
      )
      user.save()

      Profile.objects.get_or_create(user=user)
      login(request, user)

      # Cleanup session variables
      request.session.pop('reg_email', None)
      request.session.pop('reg_otp', None)
      request.session.pop('reg_otp_time', None)

      return JsonResponse(
          {'status': 'success', 'message': 'Registration successful!'}
      )
    except Exception as e:
      return JsonResponse({
          'status': 'error',
          'message': f'Server Error during instantiation: {str(e)}',
      })

  return render(request, 'home/home.html')


# ---------------------------------------------------------
# 🔓 LOGIN & LOGOUT VIEWS
# ---------------------------------------------------------
def login_view(request):
  if request.method == 'POST':
    identifier = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    if not identifier or not password:
      return JsonResponse(
          {'status': 'error', 'message': 'All fields are required!'}
      )

    # Search by Username OR Email (Case Insensitive)
    user_obj = User.objects.filter(
        models.Q(username__iexact=identifier)
        | models.Q(email__iexact=identifier)
    ).first()

    if user_obj:
      user = authenticate(
          request, username=user_obj.username, password=password
      )
      if user is not None:
        login(request, user)
        # Frontend par is success status se modal close karwayen
        return JsonResponse({
            'status': 'success',
            'message': f'WELCOME BACK, {user.username}! 🎮',
        })

    # Error status: Isase modal khula rahega aur message display ho jayega
    return JsonResponse(
        {'status': 'error', 'message': 'Invalid Username/Email or Password ❌'}
    )

  # GET Request par page/home render hoga direct URL access ke waqt
  return render(request, 'home/home.html')


def logout_view(request):
  logout(request)
  return redirect('home')


# ---------------------------------------------------------
# 👤 PROFILE MANAGEMENT VIEWS
# ---------------------------------------------------------
@login_required
def save_profile(request):
  if request.method == 'POST':
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    username = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()

    # Unique Username Check
    if username and username != user.username:
      if User.objects.filter(username=username).exclude(id=user.id).exists():
        return JsonResponse(
            {'status': 'error', 'message': 'Username already taken! 🛑'}
        )
      user.username = username

    # Unique Email Check
    if email and email != user.email:
      if User.objects.filter(email=email).exclude(id=user.id).exists():
        return JsonResponse(
            {'status': 'error', 'message': 'Email already registered! 🛑'}
        )
      user.email = email

    user.save()

    profile.mobile = request.POST.get('mobile')
    profile.gender = request.POST.get('gender')

    dob_val = request.POST.get('dob')
    if dob_val:
      profile.dob = dob_val

    profile.profession = request.POST.get('profession')

    if 'image' in request.FILES:
      profile.image = request.FILES['image']

    profile.save()

    return JsonResponse(
        {'status': 'success', 'message': 'Profile updated successfully!'}
    )

  return render(request, 'home/home.html')


@login_required
def get_profile(request):
  user = request.user
  profile, created = Profile.objects.get_or_create(user=user)

  image_url = profile.image.url if profile.image else ''

  return JsonResponse({
      'status': 'success',
      'name': user.username,
      'email': user.email,
      'mobile': profile.mobile or '',
      'gender': profile.gender or '',
      'dob': str(profile.dob) if profile.dob else '',
      'profession': profile.profession or 'Gamer',
      'image_url': image_url,
  })


# ---------------------------------------------------------
# 🔑 FORGOT & RESET PASSWORD VIEWS
# ---------------------------------------------------------
def forgot_password(request):
  if request.method != 'POST':
    return JsonResponse({'status': 'error', 'message': 'Invalid Request'})

  email = request.POST.get('email', '').strip()
  try:
    user = User.objects.get(email=email)
  except User.DoesNotExist:
    return JsonResponse({'status': 'error', 'message': 'Email not registered.'})

  otp = str(random.randint(100000, 999999))
  request.session['reset_email'] = email
  request.session['reset_otp'] = otp
  request.session['otp_time'] = time.time()

  subject = 'LearnCodePlay Password Reset OTP'
  message = f"""Hello {user.username},

Your Password Reset OTP is: {otp}

This OTP is valid for 5 minutes.

Thanks,
LearnCodePlay Team"""

  # ⚡ FAST BACKGROUND EMAIL SENDING
  send_otp_fast(subject, message, email)

  return JsonResponse(
      {'status': 'success', 'message': 'OTP sent successfully.'}
  )


def verify_otp(request):
  if request.method != 'POST':
    return JsonResponse({'status': 'error', 'message': 'Invalid Request'})

  otp = request.POST.get('otp', '').strip()
  session_otp = request.session.get('reset_otp')
  otp_time = request.session.get('otp_time')

  if not session_otp or not otp_time:
    return JsonResponse({'status': 'error', 'message': 'OTP Expired'})

  if time.time() - otp_time > 300:
    request.session.pop('reset_otp', None)
    return JsonResponse({'status': 'error', 'message': 'OTP Expired'})

  if otp != session_otp:
    return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})

  request.session['otp_verified'] = True
  return JsonResponse({'status': 'success', 'message': 'OTP Verified'})


def reset_password(request):
  if request.method != 'POST':
    return JsonResponse({'status': 'error', 'message': 'Invalid Request'})

  if not request.session.get('otp_verified'):
    return JsonResponse(
        {'status': 'error', 'message': 'Please verify OTP first'}
    )

  password = request.POST.get('password')
  email = request.session.get('reset_email')

  if not email:
    return JsonResponse({'status': 'error', 'message': 'Session Expired'})

  try:
    user = User.objects.get(email=email)
  except User.DoesNotExist:
    return JsonResponse({'status': 'error', 'message': 'User not found'})

  user.set_password(password)
  user.save()

  # Session Cleanup
  request.session.pop('reset_email', None)
  request.session.pop('reset_otp', None)
  request.session.pop('otp_time', None)
  request.session.pop('otp_verified', None)

  return JsonResponse(
      {'status': 'success', 'message': 'Password Updated Successfully'}
  )


# ---------------------------------------------------------
# 💬 GAME COMMENTS MANAGEMENT VIEWS
# ---------------------------------------------------------
def get_comments(request, game_id):
  try:
    comments = GameComment.objects.filter(game_id=game_id).order_by(
        '-created_at'
    )
    data = []
    for c in comments:
      local_time = timezone.localtime(c.created_at)

      data.append({
          'id': c.id,
          'user': c.user.username if c.user else 'Guest Gamer',
          'text': c.comment_text,
          'time': local_time.strftime('%b %d, %H:%M'),
      })
    return JsonResponse({'status': 'success', 'comments': data})
  except Exception as e:
    return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def add_comment(request):
  if request.method == 'POST':
    try:
      data = json.loads(request.body)
      game_id = data.get('game_id')
      text = data.get('comment_text')

      user_obj = request.user if request.user.is_authenticated else None

      comment = GameComment.objects.create(
          game_id=game_id, user=user_obj, comment_text=text
      )

      return JsonResponse({'status': 'success', 'id': comment.id})

    except Exception as e:
      return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

  return JsonResponse({'status': 'error'}, status=400)


@login_required
def delete_comment(request, comment_id):
  """Admin ya author comment delete kar sakta hai"""
  comment = get_object_or_404(GameComment, id=comment_id)

  # Admin ya Comment creator hi delete kar sakega
  if request.user.is_superuser or request.user == comment.user:
    comment.delete()
    return JsonResponse(
        {'status': 'success', 'message': 'Comment deleted successfully'}
    )

  return JsonResponse(
      {'status': 'error', 'message': 'Unauthorized action!'}, status=403
  )