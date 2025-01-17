# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, LoginForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Hobby, CustomUser, FriendRequest
import json
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.db.models import F, ExpressionWrapper, IntegerField, DateField, Q
from datetime import date
from django.views.decorators.http import require_http_methods

@csrf_exempt
def hobbies_view(request):
    if request.method == 'GET':
        hobbies = list(Hobby.objects.values('id', 'name'))
        return JsonResponse({'hobbies': hobbies}, safe=False)
    elif request.method == 'POST':
        new_hobby = Hobby()
        new_hobby.name = json.loads(request.body)["hobby"]
        new_hobby.save()
        if request.user.is_authenticated:
            user = request.user
            user.hobbies.add(new_hobby)
            user.save()
        return JsonResponse({'message': 'Hobby Added Succesfully!'}, status=200)
    return JsonResponse({'error': 'Method not allowed.'}, status=405)

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
    try:
        # Get min_age and max_age from query parameters
        min_age = request.GET.get('min_age')
        max_age = request.GET.get('max_age')

        # Get a random user as reference if not authenticated
        if not request.user.is_authenticated:
            reference_user = CustomUser.objects.order_by('?').first()
        else:
            reference_user = request.user

        reference_user_hobbies = set(reference_user.hobbies.all())

        # Annotate users with their exact age by considering month and day
        today = date.today()
        all_users = CustomUser.objects.annotate(
            age=ExpressionWrapper(
                (today.year - F('date_of_birth__year')) - (
                    Q(date_of_birth__month__gt=today.month) |
                    (Q(date_of_birth__month=today.month) & Q(date_of_birth__day__gt=today.day))
                ),
                output_field=IntegerField()
            )
        )

        # Filter by age range if provided
        if min_age:
            all_users = all_users.filter(age__gte=int(min_age))
        if max_age:
            all_users = all_users.filter(age__lte=int(max_age))

        # Exclude the reference user
        all_users = all_users.exclude(id=reference_user.id)

        user_similarities = []

        for user in all_users:
            user_hobbies = set(user.hobbies.all())
            common_hobbies = reference_user_hobbies.intersection(user_hobbies)
            is_friend = FriendRequest.objects.filter(
                Q(sender=request.user, receiver=user, status='accepted') |
                Q(sender=user, receiver=request.user, status='accepted')
            ).exists()
            request_sent = FriendRequest.objects.filter(
                sender=request.user, receiver=user, status='pending'
            ).exists()

            if len(common_hobbies) > 0:
                user_similarities.append({
                    'id': user.id,  # Add user ID here
                    'name': user.name,
                    'common_hobbies': [{'id': hobby.id, 'name': hobby.name} for hobby in common_hobbies],
                    'similarity_score': len(common_hobbies),
                    'is_friend': is_friend,
                    'request_sent': request_sent
                })

        # Sort by similarity score in descending order
        user_similarities.sort(key=lambda x: x['similarity_score'], reverse=True)

        return JsonResponse({
            'similar_users': user_similarities,
            'reference_user': reference_user.name if not request.user.is_authenticated else None
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def auth_status(request):
    if request.user.is_authenticated:
        hobbies = [{'id': hobby.id, 'name': hobby.name} for hobby in request.user.hobbies.all()]
        return JsonResponse({
            'isAuthenticated': True,
            'username': request.user.username,
            'profile': {
                'name': request.user.name,
                'email': request.user.email,
                'date_of_birth': request.user.date_of_birth,
                'hobbies': hobbies
            }
        })
    return JsonResponse({
        'isAuthenticated': False,
        'username': None
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

@csrf_exempt
@login_required  # Make sure the user is authenticated
def update_user_profile(request):
    if request.method == 'PUT':
        try:
            # Load JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))

            # Get the current user
            user = request.user

            # Update fields if they are provided in the request
            if 'name' in data:
                user.name = data['name']
            if 'email' in data:
                user.email = data['email']
            if 'date_of_birth' in data:
                user.date_of_birth = data['date_of_birth']

            # Update hobbies if they are provided
            if 'hobbies' in data:
                user.hobbies.clear()  # Remove current hobbies
                for hobby_id in data['hobbies']:
                    try:
                        hobby = Hobby.objects.get(id=hobby_id)
                        user.hobbies.add(hobby)  # Add new hobbies
                    except ObjectDoesNotExist:
                        return JsonResponse({'error': f'Hobby with id {hobby_id} does not exist.'}, status=400)

            # Save the updated user profile
            user.save()

            # Return the updated profile as response
            updated_profile_data = {
                'name': user.name,
                'email': user.email,
                'date_of_birth': user.date_of_birth,
                'hobbies': [{'id': hobby.id, 'name': hobby.name} for hobby in user.hobbies.all()],
            }

            return JsonResponse(updated_profile_data, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def change_password(request):
    if request.method == 'POST':
        try:
            # Parse request body
            data = json.loads(request.body.decode('utf-8'))
            current_password = data.get('current_password')
            new_password = data.get('new_password')

            # Validate inputs
            if not current_password or not new_password:
                return JsonResponse({'error': 'Both current_password and new_password are required.'}, status=400)

            # Check if the current password is correct
            user = request.user
            if not user.check_password(current_password):
                return JsonResponse({'error': 'Current password is incorrect.'}, status=400)

            # Set the new password
            user.set_password(new_password)
            user.save()

            # Keep the user logged in after password change
            update_session_auth_hash(request, user)

            return JsonResponse({'message': 'Password updated successfully.'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def send_friend_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            receiver_id = data.get('to_user_id')  # Adjusted key name
            receiver = CustomUser.objects.get(id=receiver_id)

            if FriendRequest.objects.filter(sender=request.user, receiver=receiver, status='pending').exists():
                return JsonResponse({'error': 'Friend request already sent.'}, status=400)

            FriendRequest.objects.create(sender=request.user, receiver=receiver)
            return JsonResponse({'message': 'Friend request sent successfully!'}, status=200)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method.'}, status=405)



@csrf_exempt
@login_required
def respond_friend_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            request_id = data.get('request_id')
            action = data.get('action')  # 'accept' or 'reject'

            friend_request = FriendRequest.objects.get(id=request_id, receiver=request.user)

            if action == 'accept':
                friend_request.status = 'accepted'
                friend_request.save()
                # You can add mutual friendship logic here if needed

            elif action == 'reject':
                friend_request.delete()

            return JsonResponse({'message': f'Friend request {action}ed successfully!'}, status=200)
        except FriendRequest.DoesNotExist:
            return JsonResponse({'error': 'Friend request not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method.'}, status=405)



@login_required
def list_friend_requests(request):
    if request.method == 'GET':
        friend_requests = FriendRequest.objects.filter(receiver=request.user, status='pending')
        requests_data = [
            {
                'id': fr.id,
                'sender': {
                    'id': fr.sender.id,
                    'username': fr.sender.username,
                },
                'status': fr.status,
            }
            for fr in friend_requests
        ]
        return JsonResponse({'friend_requests': requests_data}, safe=False)
    return JsonResponse({'error': 'Invalid method.'}, status=405)
