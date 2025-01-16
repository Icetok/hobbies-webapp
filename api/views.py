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

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            # Parse JSON body
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Create the form with parsed data
        form = CustomUserCreationForm(data)
        if form.is_valid():
            user = form.save()

            # Set hobbies
            hobbies = data.get('hobbies', [])
            user.hobbies.set(hobbies)
            user.save()

            login(request, user)
            return JsonResponse({'message': 'Signup successful!'}, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'error': 'GET method not allowed'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            # Parse JSON body
            data = json.loads(request.body.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful!'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    return JsonResponse({'error': 'GET method not allowed'}, status=405)

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Successfully logged out'}, status=200)
    return JsonResponse({'error': 'GET method not allowed'}, status=405)

def get_hobbies(request):
    if request.method == 'GET':
        hobbies = list(Hobby.objects.values('id', 'name'))
        return JsonResponse({'hobbies': hobbies}, safe=False)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def auth_status_view(request):
    return JsonResponse({'isAuthenticated': True})

@login_required
def get_user_profile(request):
    user = request.user
    hobbies = user.hobbies.all()  # Get user's hobbies

    profile_data = {
        'name': user.name,
        'email': user.email,
        'date_of_birth': user.date_of_birth,
        'hobbies': [{'id': hobby.id, 'name': hobby.name} for hobby in hobbies],
    }
    
    return JsonResponse(profile_data)

@login_required
def get_similar_users(request):
    current_user = request.user
    current_user_hobbies = set(current_user.hobbies.all())
    print(f"Current user: {current_user.username}")
    print(f"Current user hobbies: {[h.name for h in current_user_hobbies]}")
    
    # Get all users except the current user
    all_users = CustomUser.objects.exclude(id=current_user.id)
    print(f"Found {all_users.count()} other users")
    
    # Calculate similarity scores
    user_similarities = []
    for user in all_users:
        user_hobbies = set(user.hobbies.all())
        print(f"Checking user {user.username} with hobbies: {[h.name for h in user_hobbies]}")
        common_hobbies = current_user_hobbies.intersection(user_hobbies)
        similarity_score = len(common_hobbies)
        print(f"Common hobbies: {[h.name for h in common_hobbies]}")
        
        if similarity_score > 0:
            user_similarities.append({
                'name': user.name,
                'common_hobbies': [{'id': hobby.id, 'name': hobby.name} for hobby in common_hobbies],
                'similarity_score': similarity_score
            })
    
    print(f"Final similar users: {user_similarities}")
    return JsonResponse({'similar_users': user_similarities})
