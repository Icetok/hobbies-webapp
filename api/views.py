# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, LoginForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Hobby, CustomUser
import json
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            if data.get('password1') != data.get('password2'):
                return JsonResponse({'errors': {'password': ['Passwords do not match']}}, status=400)
            
            form = CustomUserCreationForm(data)
            if form.is_valid():
                user = form.save()
                hobbies = data.get('hobbies', [])
                user.hobbies.set(hobbies)
                login(request, user)
                return JsonResponse({'message': 'Signup successful!'}, status=200)
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Server error'}, status=500)
    return JsonResponse({'error': 'GET method not allowed'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                request.session.save()
                
                # Include user profile data in login response
                hobbies = user.hobbies.all()
                profile_data = {
                    'name': user.name,
                    'email': user.email,
                    'date_of_birth': user.date_of_birth,
                    'hobbies': [{'id': hobby.id, 'name': hobby.name} for hobby in hobbies],
                }
                
                response = JsonResponse({
                    'message': 'Login successful',
                    'username': user.username,
                    'isAuthenticated': True,
                    'sessionid': request.session.session_key,
                    'profile': profile_data
                })
                
                response.set_cookie(
                    'sessionid',
                    request.session.session_key,
                    domain=None,
                    max_age=86400,
                    path='/',
                    secure=False,
                    httponly=True,
                    samesite='Lax'
                )
                return response
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Successfully logged out'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_hobbies(request):
    if request.method == 'GET':
        hobbies = list(Hobby.objects.values('id', 'name'))
        return JsonResponse({'hobbies': hobbies}, safe=False)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def auth_status_view(request):
    return JsonResponse({'isAuthenticated': True})

@require_http_methods(["GET"])
def get_user_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'error': 'User not authenticated'
        }, status=401)
        
    try:
        user = request.user
        hobbies = user.hobbies.all()
        profile_data = {
            'name': user.name,
            'email': user.email,
            'date_of_birth': user.date_of_birth,
            'hobbies': [{'id': hobby.id, 'name': hobby.name} for hobby in hobbies],
        }
        return JsonResponse(profile_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_similar_users(request):
    print(f"Session ID: {request.session.session_key}")
    print(f"User: {request.user}")
    print(f"Authenticated: {request.user.is_authenticated}")
    print(f"Cookies: {request.COOKIES}")
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'error': 'User not authenticated',
            'debug': {
                'session_id': request.session.session_key,
                'cookies': request.COOKIES,
            }
        }, status=401)
    
    try:
        current_user = request.user
        current_user_hobbies = set(current_user.hobbies.all())
        all_users = CustomUser.objects.exclude(id=current_user.id)
        user_similarities = []
        
        for user in all_users:
            user_hobbies = set(user.hobbies.all())
            common_hobbies = current_user_hobbies.intersection(user_hobbies)
            
            if len(common_hobbies) > 0:
                user_similarities.append({
                    'name': user.name,
                    'common_hobbies': [{'id': hobby.id, 'name': hobby.name} for hobby in common_hobbies],
                    'similarity_score': len(common_hobbies)
                })
        
        return JsonResponse({'similar_users': user_similarities})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def auth_status(request):
    return JsonResponse({
        'isAuthenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None
    })

@require_http_methods(["GET"])
def check_session(request):
    return JsonResponse({
        'isAuthenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None,
        'sessionid': request.session.session_key,
        'debug': {
            'session_data': dict(request.session),
            'cookies': request.COOKIES
        }
    })
