from .models import (
    User,
    OTP,
    PasswordResetToken,
    PasswordHistory,
    Admin,
    Course,
    Quiz,
    Question,
    QuizAttempt,
    UserAnswer,
    UserActivity,
    Material,
    UserProgress
)
from django.conf import settings as django_settings 
from django.template.defaultfilters import timesince
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count, Case, When, F, Value, IntegerField
from django.db.models.functions import TruncMonth
import datetime
import requests
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils import timezone
from functools import wraps
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
import random
import json
import uuid
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from django.conf import settings

# Create your views here.


def send_password_reset_email(email, reset_link):
    """Send password reset link to user's email"""
    subject = "Password Reset Request"
    message = f"Click the following link to reset your password:\n{reset_link}\n\nThis link will expire in 15 minutes."
    from_email = "Career Guidance System"  # Replace with your email
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def forgot_password(request):
    """Handle forgot password request"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            try:
                user = User.objects.get(email=email)

                # Generate unique reset token
                token = str(uuid.uuid4())

                # Create or update password reset token
                reset_token, created = PasswordResetToken.objects.get_or_create(
                    user=user, defaults={"token": token, "created_at": timezone.now()}
                )

                if not created:
                    reset_token.token = token
                    reset_token.created_at = timezone.now()
                    reset_token.save()

                # Generate reset link
                reset_link = request.build_absolute_uri(
                    reverse("reset_password") + f"?token={token}"
                )

                # Send reset email
                if send_password_reset_email(email, reset_link):
                    return JsonResponse(
                        {"message": "Password reset link sent to your email"}
                    )
                else:
                    return JsonResponse(
                        {"error": "Failed to send reset link"}, status=500
                    )

            except User.DoesNotExist:
                return JsonResponse({"error": "Email not registered"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "forgot_password.html")


def validate_password_strength(password):
    """Comprehensive password strength validation"""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")

    return errors


def reset_password(request):
    """Handle password reset functionality"""
    if request.method == "GET":
        token = request.GET.get("token")
        try:
            # Validate token exists and is within 15-minute window
            reset_token = PasswordResetToken.objects.get(
                token=token,
                created_at__gt=timezone.now() - timezone.timedelta(minutes=15),
            )
            return render(request, "reset_password.html", {"token": token})
        except PasswordResetToken.DoesNotExist:
            return render(
                request,
                "reset_password.html",
                {
                    "error": "Invalid or expired reset link. Please request a new password reset."
                },
            )

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data.get("token")
            new_password = data.get("new_password")
            confirm_password = data.get("confirm_password")

            # Basic validation
            if not new_password or not confirm_password:
                return JsonResponse(
                    {"error": "Password fields cannot be empty"}, status=400
                )

            if new_password != confirm_password:
                return JsonResponse(
                    {"error": "New password and confirm password do not match"},
                    status=400,
                )

            # Password strength validation
            password_errors = validate_password_strength(new_password)
            if password_errors:
                return JsonResponse({"error": password_errors[0]}, status=400)

            try:
                # Validate reset token
                reset_token = PasswordResetToken.objects.get(
                    token=token,
                    created_at__gt=timezone.now() - timezone.timedelta(minutes=15),
                )

                user = reset_token.user

                # First check against current password
                if check_password(new_password, user.password):
                    return JsonResponse(
                        {
                            "error": "New password cannot be the same as current password"
                        },
                        status=400,
                    )

                # Then check against password history
                previous_passwords = PasswordHistory.objects.filter(user=user)
                for past_password in previous_passwords:
                    if check_password(new_password, past_password.password):
                        return JsonResponse(
                            {"error": "Cannot reuse previously used passwords"},
                            status=400,
                        )

                # Create password history entry with current password before updating
                PasswordHistory.objects.create(
                    user=user,
                    password=user.password,  # Save the current hashed password
                )

                # Update user's password
                user.set_password(
                    new_password
                )  # Use set_password instead of direct assignment
                user.save()

                # Delete used token
                reset_token.delete()

                return JsonResponse(
                    {
                        "message": "Password reset successful. You can now log in with your new password."
                    }
                )

            except PasswordResetToken.DoesNotExist:
                return JsonResponse(
                    {"error": "Invalid or expired reset link"}, status=400
                )

        except Exception as e:
            return JsonResponse(
                {"error": "An unexpected error occurred. Please try again."}, status=500
            )

    # Default case for any other request methods
    return render(request, "reset_password.html", {"error": "Invalid request method"})


def home(request):
    """Render the home page"""
    return render(request, "home.html")

def python_roadmap(request):
    """Show python_roadmap if user is logged in"""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    
    # Fetch the complete user object from the database
    try:
        user = User.objects.get(id=user_id)
        return render(request, "python_roadmap.html", {"user": user})
    except User.DoesNotExist:
        # Handle the case where user doesn't exist anymore
        del request.session["user_id"]
        return redirect("login")

def web_development_roadmap(request):
    """Show python_roadmap if user is logged in"""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    
    # Fetch the complete user object from the database
    try:
        user = User.objects.get(id=user_id)
        return render(request, "web_development_roadmap.html", {"user": user})
    except User.DoesNotExist:
        # Handle the case where user doesn't exist anymore
        del request.session["user_id"]
        return redirect("login")

def cs_roadmap(request):
    """Show python_roadmap if user is logged in"""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    
    # Fetch the complete user object from the database
    try:
        user = User.objects.get(id=user_id)
        return render(request, "cs_roadmap.html", {"user": user})
    except User.DoesNotExist:
        # Handle the case where user doesn't exist anymore
        del request.session["user_id"]
        return redirect("login")

def devops_roadmap(request):
    """Show python_roadmap if user is logged in"""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    
    # Fetch the complete user object from the database
    try:
        user = User.objects.get(id=user_id)
        return render(request, "devops_roadmap.html", {"user": user})
    except User.DoesNotExist:
        # Handle the case where user doesn't exist anymore
        del request.session["user_id"]
        return redirect("login")

def generate_otp():
    """Generate a 4-digit OTP"""
    return "".join([str(random.randint(0, 9)) for _ in range(4)])


def send_otp_email(email, otp):
    """Send OTP to user's email"""
    subject = "Your OTP for Verification"
    message = f"Your OTP is: {otp}. This OTP is valid for 5 minutes."
    from_email = "Career Guidance System"  # Replace with your email
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def register(request):
    """Handle user registration"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Check if this is an OTP verification request
            if "otp" in data:
                email = data.get("email")
                submitted_otp = data.get("otp")

                # Get the latest OTP for this email
                try:
                    stored_otp = OTP.objects.filter(
                        email=email, purpose="registration"
                    ).latest("created_at")

                    # Check if OTP is expired (5 minutes)
                    time_diff = (timezone.now() - stored_otp.created_at).total_seconds()
                    if time_diff > 300:  # 5 minutes
                        stored_otp.delete()
                        return JsonResponse(
                            {"error": "OTP has expired. Please request a new one."},
                            status=400,
                        )

                    # Verify OTP
                    if stored_otp.otp != submitted_otp:
                        return JsonResponse(
                            {"error": "Invalid OTP. Please try again."}, status=400
                        )

                    # Get registration data from session
                    registration_data = request.session.get("registration_data")
                    ip_address = request.META.get('REMOTE_ADDR')
                    if not registration_data:
                        return JsonResponse(
                            {"error": "Registration data not found. Please try again."},
                            status=400,
                        )

                    # Create new user
                    user = User(
                        first_name=registration_data["first_name"],
                        last_name=registration_data["last_name"],
                        email=registration_data["email"],
                        date_of_birth=registration_data["date_of_birth"],
                        contact_number=registration_data["contact_number"],
                        skills=registration_data["skills"],
                        interests=registration_data["interests"],
                        password=registration_data["password"],
                        terms_accepted=registration_data["terms_accepted"],
                    )
                    user.save()

                    # Log user registration activity
                    log_user_activity(
                        request, 
                        'registration', 
                        f"New user registered: {user.first_name} {user.last_name} from IP Address {ip_address}",
                        user
                    )

                    # Clean up
                    stored_otp.delete()
                    del request.session["registration_data"]

                    return JsonResponse(
                        {"message": "Registration successful"}, status=201
                    )

                except OTP.DoesNotExist:
                    return JsonResponse(
                        {"error": "No OTP found. Please request a new one."}, status=400
                    )

            # This is initial registration request
            email = data.get("email")
            contact_number = data.get("contact_number")

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already exists"}, status=400)

            # Check if contact number already exists
            if User.objects.filter(contact_number=contact_number).exists():
                return JsonResponse(
                    {"error": "Contact number already exists"}, status=400
                )

            # Store registration data in session
            request.session["registration_data"] = data

            # Generate and store OTP
            otp = generate_otp()
            OTP.objects.create(email=email, otp=otp, purpose="registration")

            # Send OTP email
            if not send_otp_email(email, otp):
                return JsonResponse(
                    {"error": "Failed to send OTP. Please try again."}, status=500
                )

            return JsonResponse(
                {"message": "OTP sent to your email", "require_otp": True}
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # GET request - show registration form
    return render(request, "register.html")


def login_view(request):
    """Handle user login"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Check if this is an OTP verification request
            if "otp" in data:
                email = data.get("email")
                submitted_otp = data.get("otp")

                try:
                    stored_otp = OTP.objects.filter(
                        email=email, purpose="login"
                    ).latest("created_at")

                    # Check if OTP is expired
                    time_diff = (timezone.now() - stored_otp.created_at).total_seconds()
                    if time_diff > 300:  # 5 minutes
                        stored_otp.delete()
                        return JsonResponse(
                            {"error": "OTP has expired. Please try again."}, status=400
                        )

                    # Verify OTP
                    if stored_otp.otp != submitted_otp:
                        return JsonResponse(
                            {"error": "Invalid OTP. Please try again."}, status=400
                        )

                    # Get user and create session
                    user = User.objects.get(email=email)
                    ip_address = request.META.get('REMOTE_ADDR')
                    request.session["user_id"] = user.id
                    request.session["user_name"] = f"{user.first_name} {user.last_name}"

                    # Log user login activity
                    log_user_activity(
                        request, 
                        'login', 
                        f"{user.first_name} {user.last_name} logged in from IP Address {ip_address}",
                        user
                    )

                    # Clean up
                    stored_otp.delete()

                    return JsonResponse({"message": "Login successful"})

                except OTP.DoesNotExist:
                    return JsonResponse(
                        {"error": "No OTP found. Please try again."}, status=400
                    )

            # This is initial login request
            email = data.get("email")
            password = data.get("password")
            captcha_response = data.get("captcha", "")
            
            # Validation
            if not email or not password:
                return JsonResponse(
                    {"error": "Please enter both email and password"}, status=400
                )
                
            # Verify CAPTCHA presence
            if not captcha_response:
                print("ERROR: Missing CAPTCHA response in request")
                return JsonResponse(
                    {"error": "Please complete the CAPTCHA verification"}, status=400
                )
                
            # Verify the CAPTCHA with Google's reCAPTCHA API
            recaptcha_secret = django_settings.RECAPTCHA_SECRET_KEY
            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            
            try:
                # Send POST request to Google's reCAPTCHA API
                recaptcha_response = requests.post(
                    verify_url,
                    data={
                        "secret": recaptcha_secret,
                        "response": captcha_response,
                        "remoteip": get_client_ip(request)
                    }
                )
                
                recaptcha_result = recaptcha_response.json()
                
                # If CAPTCHA verification failed
                if not recaptcha_result.get("success", False):
                    return JsonResponse(
                        {"error": "CAPTCHA verification failed. Please try again."}, status=400
                    )
            except Exception as recaptcha_error:
                return JsonResponse(
                    {"error": "Error verifying CAPTCHA. Please try again."}, status=400
                )

            # Verify credentials
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    # Log failed login attempt
                    log_user_activity(
                        request, 
                        'failed_login', 
                        f"Failed login attempt for email: {email}",
                        None
                    )
                    return JsonResponse(
                        {"error": "Invalid email or password"}, status=400
                    )

                # Generate and store OTP
                otp = generate_otp()
                OTP.objects.create(email=email, otp=otp, purpose="login")

                # Send OTP email
                if not send_otp_email(email, otp):
                    return JsonResponse(
                        {"error": "Failed to send OTP. Please try again."}, status=500
                    )

                return JsonResponse(
                    {"message": "OTP sent to your email", "require_otp": True}
                )

            except User.DoesNotExist:
                # Log failed login attempt
                log_user_activity(
                    request, 
                    'failed_login', 
                    f"Failed login attempt for non-existent email: {email}",
                    None
                )
                return JsonResponse({"error": "Invalid email or password"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # GET request - show login form
    return render(request, "login.html")

def otp_verification(request):
    """Render OTP verification page"""
    return render(request, "otp_verification.html")


def dashboard(request):
    """Show dashboard if user is logged in"""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user_name = request.session.get("user_name", "User")
    return render(request, "dashboard.html", {"user_name": user_name})


def logout_view(request):
    """Handle user logout"""
    user_id = request.session.get("user_id")
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            ip_address = request.META.get('REMOTE_ADDR')
            # Log user logout activity
            log_user_activity(
                request, 
                'logout', 
                f"{user.first_name} {user.last_name} logged out from IP Address {ip_address}",
                user
            )
        except User.DoesNotExist:
            pass
            
    logout(request)
    request.session.flush()
    return redirect("login")

def require_admin_login(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        admin_id = request.session.get("admin_id")
        if not admin_id:
            return JsonResponse({"success": False, "error": "Unauthorized"})
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_login(request):
    """Handle admin login"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username", "").strip()
            password = data.get("password", "")
            captcha_response = data.get("captcha", "")

            # More detailed debugging
            print(f"Received login request - Username: {username}")
            print(f"CAPTCHA received: {'Yes' if captcha_response else 'No'}")
            if captcha_response:
                print(f"CAPTCHA length: {len(captcha_response)}")
            
            # Validation
            if not username or not password:
                return JsonResponse(
                    {"error": "Please enter both username and password"}, status=400
                )
                
            # Verify CAPTCHA presence
            if not captcha_response:
                print("ERROR: Missing CAPTCHA response in request")
                return JsonResponse(
                    {"error": "Please complete the CAPTCHA verification"}, status=400
                )
                
            # Verify the CAPTCHA with Google's reCAPTCHA API
            recaptcha_secret = django_settings.RECAPTCHA_SECRET_KEY
            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            
            # Log CAPTCHA verification details
            print(f"Verifying CAPTCHA with Google API")
            
            try:
                # Send POST request to Google's reCAPTCHA API
                recaptcha_response = requests.post(
                    verify_url,
                    data={
                        "secret": recaptcha_secret,
                        "response": captcha_response,
                        "remoteip": get_client_ip(request)
                    }
                )
                
                recaptcha_result = recaptcha_response.json()
                print(f"CAPTCHA verification result: {recaptcha_result}")
                
                # If CAPTCHA verification failed
                if not recaptcha_result.get("success", False):
                    print(f"CAPTCHA verification failed: {recaptcha_result.get('error-codes', [])}")
                    return JsonResponse(
                        {"error": "CAPTCHA verification failed. Please try again."}, status=400
                    )
            except Exception as recaptcha_error:
                print(f"Error during CAPTCHA verification: {str(recaptcha_error)}")
                return JsonResponse(
                    {"error": "Error verifying CAPTCHA. Please try again."}, status=400
                )
            
            try:
                admin = Admin.objects.get(username=username)

                if not admin.is_active:
                    return JsonResponse(
                        {"error": "This admin account has been deactivated"}, status=400
                    )

                if admin.check_password(password):
                    # Set session data
                    request.session["admin_id"] = admin.id
                    request.session["admin_username"] = admin.username
                    request.session["admin_full_name"] = admin.full_name

                    # Log successful login attempt
                    UserActivity.objects.create(
                        activity_type="login",
                        description=f"Admin {admin.username} logged in",
                        ip_address=get_client_ip(request)
                    )

                    return JsonResponse(
                        {"success": True, "redirect": "/admin-dashboard/"}
                    )
                else:
                    # Log failed login attempt
                    UserActivity.objects.create(
                        activity_type="login",
                        description=f"Failed login attempt for admin username: {username}",
                        ip_address=get_client_ip(request)
                    )
                    return JsonResponse({"error": "Invalid credentials"}, status=400)

            except Admin.DoesNotExist:
                # Log failed login attempt
                UserActivity.objects.create(
                    activity_type="login",
                    description=f"Failed login attempt for invalid admin username: {username}",
                    ip_address=get_client_ip(request)
                )
                return JsonResponse({"error": "Invalid credentials"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid request format"}, status=400)

        except Exception as e:
            print(f"Unexpected error during login: {str(e)}")
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)

    # If admin is already logged in, redirect to dashboard
    if request.session.get("admin_id"):
        return redirect("admin_dashboard")

    return render(request, "admin_login.html")

# Helper function to get client IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def admin_dashboard(request):
    """Admin dashboard view"""
    # Check if admin is logged in
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return redirect("admin_login")

    try:
        admin = Admin.objects.get(id=admin_id)
        users = User.objects.all()  # Get all registered users
        courses = Course.objects.all()  # Get all courses
        quizzes = Quiz.objects.all()   # Get all quizzes
        questions = Question.objects.all().select_related('quiz')  # Get all questions with quiz data
        
        # Get recent user activities (last 10)
        recent_activities = UserActivity.objects.all().select_related('user')[:10]
        
        context = {
            "admin_username": admin.username, 
            "admin_full_name": admin.full_name,
            "users": users,
            "courses": courses,
            "quizzes": quizzes,
            "questions": questions,
            "recent_activities": recent_activities
        }
        return render(request, "admin_dashboard.html", context)
    except Admin.DoesNotExist:
        # If admin doesn't exist, clear session and redirect to login
        request.session.flush()
        return redirect("admin_login")

def log_user_activity(request, activity_type, description, user=None):
    """Helper function to log user activities"""
    UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=request.META.get('REMOTE_ADDR')
    )

def get_recent_activities(request):
    """API endpoint to get recent user activities for admin dashboard"""
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    try:
        activities = UserActivity.objects.all().select_related('user')[:10]
        
        activities_data = []
        for activity in activities:
            activities_data.append({
                'description': activity.description,
                'time_ago': timesince(activity.timestamp)
            })
        
        return JsonResponse({'activities': activities_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def quiz_performance_data(request):
    """API endpoint to get quiz performance data for the admin dashboard charts"""
    # Check if admin is logged in
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    try:
        # 1. Average scores by course
        average_scores = {}
        courses = Course.objects.filter(quiz__isnull=False)
        
        course_labels = []
        course_scores = []
        
        for course in courses:
            quiz_attempts = QuizAttempt.objects.filter(
                quiz=course.quiz, 
                score__isnull=False
            ).aggregate(avg_score=Avg('score'))
            
            avg_score = quiz_attempts['avg_score'] or 0
            course_labels.append(course.title)
            course_scores.append(round(avg_score, 1))
        
        average_scores = {
            'labels': course_labels,
            'scores': course_scores
        }
        
        # 2. Pass rate trend over time (last 6 months)
        today = datetime.date.today()
        six_months_ago = today - datetime.timedelta(days=180)
        
        # Get attempts grouped by month
        attempts_by_month = QuizAttempt.objects.filter(
            end_time__date__gte=six_months_ago,
            end_time__date__lte=today,
            score__isnull=False
        ).annotate(
            month=TruncMonth('end_time')
        ).values('month').annotate(
            total=Count('id'),
            passed=Count(Case(
                When(score__gte=F('quiz__pass_percentage'), then=1),
                output_field=IntegerField()
            ))
        ).order_by('month')
        
        month_labels = []
        pass_rates = []
        
        for item in attempts_by_month:
            month_name = item['month'].strftime('%b %Y')
            month_labels.append(month_name)
            
            pass_rate = 0
            if item['total'] > 0:
                pass_rate = round((item['passed'] / item['total']) * 100, 1)
            
            pass_rates.append(pass_rate)
        
        pass_rate_trend = {
            'labels': month_labels,
            'passRates': pass_rates
        }
        
        # 3. Overall pass/fail percentage
        overall_stats = QuizAttempt.objects.filter(
            score__isnull=False
        ).aggregate(
            total=Count('id'),
            passed=Count(Case(
                When(score__gte=F('quiz__pass_percentage'), then=1),
                output_field=IntegerField()
            ))
        )
        
        passed_percentage = 0
        failed_percentage = 0
        
        if overall_stats['total'] > 0:
            passed_percentage = round((overall_stats['passed'] / overall_stats['total']) * 100)
            failed_percentage = 100 - passed_percentage
        
        pass_fail_percentage = {
            'passed': passed_percentage,
            'failed': failed_percentage
        }
        
        # 4. Top 5 most attempted quizzes
        top_quizzes = Quiz.objects.annotate(
            attempt_count=Count('quizattempt')
        ).order_by('-attempt_count')[:5]
        
        top_quiz_data = {
            'labels': [quiz.title for quiz in top_quizzes],
            'attempts': [quiz.attempt_count for quiz in top_quizzes]
        }
        
        # Return all data in a single response
        return JsonResponse({
            'average_scores': average_scores,
            'pass_rate_trend': pass_rate_trend,
            'pass_fail_percentage': pass_fail_percentage,
            'top_attempted_quizzes': top_quiz_data
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
     
def get_user_details(request, user_id):
    print("Fetching user details for ID:", user_id)  # Debug print
    if not request.session.get("admin_id"):
        return JsonResponse({"success": False, "error": "Unauthorized"})
    
    try:
        user = User.objects.get(id=user_id)
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "contact_number": user.contact_number,
            "date_of_birth": user.date_of_birth.strftime('%Y-%m-%d'),
            "skills": user.skills,
            "interests": user.interests
        }
        return JsonResponse({"success": True, "user": user_data})
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "User not found"})
    except Exception as e:
        print("Error:", str(e))  # Debug print
        return JsonResponse({"success": False, "error": str(e)})

def add_user(request):
    if not request.session.get("admin_id"):
        return JsonResponse({"success": False, "error": "Unauthorized"})
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Validate password
            if not data.get("password"):
                return JsonResponse({"success": False, "error": "Password is required"})
            
            # Create new user with properly hashed password
            user = User(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                contact_number=data["contact_number"],
                date_of_birth=data["date_of_birth"],
                skills=data.get("skills", ""),
                interests=data.get("interests", ""),
                terms_accepted=True
            )
            
            # Properly set the hashed password using set_password method
            user.set_password(data["password"])
            user.save()
            
            return JsonResponse({"success": True})
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})

def update_user(request):
    print("Update user request received")  # Debug print
    if not request.session.get("admin_id"):
        return JsonResponse({"success": False, "error": "Unauthorized"})
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Received data:", data)  # Debug print
            user_id = data.get("id")
            user = User.objects.get(id=user_id)
            
            user.first_name = data.get("first_name", user.first_name)
            user.last_name = data.get("last_name", user.last_name)
            user.email = data.get("email", user.email)
            user.contact_number = data.get("contact_number", user.contact_number)
            if data.get("date_of_birth"):
                user.date_of_birth = data["date_of_birth"]
            user.skills = data.get("skills", user.skills)
            user.interests = data.get("interests", user.interests)
            
            if data.get("password"):
                user.password = make_password(data["password"])
            
            user.save()
            return JsonResponse({"success": True})
        except Exception as e:
            print("Error:", str(e))  # Debug print
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})

def delete_user(request, user_id):
    print("Delete user request received for ID:", user_id)  # Debug print
    if not request.session.get("admin_id"):
        return JsonResponse({"success": False, "error": "Unauthorized"})
    
    if request.method == "POST":
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            print("Error:", str(e))  # Debug print
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})

@require_admin_login
def get_course_details(request, course_id):
    """Get course details by ID"""
    try:
        course = Course.objects.get(id=course_id)
        course_data = {
            "title": course.title,
            "description": course.description,
            "is_active": course.is_active,
            "roadmap_link": course.roadmap_link,
            #"enrollment_link": course.enrollment_link,
            "image_url": course.image.url if course.image else None
        }
        return JsonResponse({"success": True, "course": course_data})
    except Course.DoesNotExist:
        return JsonResponse({"success": False, "error": "Course not found"})
    except Exception as e:
        print("Error:", str(e))
        return JsonResponse({"success": False, "error": str(e)})

@require_admin_login
def add_course(request):
    """Add a new course"""
    if request.method == "POST":
        try:
            title = request.POST.get("title")
            description = request.POST.get("description")
            is_active = request.POST.get("is_active") == "true"
            roadmap_link = request.POST.get("roadmap_link", "")
            #enrollment_link = request.POST.get("enrollment_link", "")
            
            # Create course object
            course = Course(
                title=title,
                description=description,
                is_active=is_active,
                roadmap_link=roadmap_link,
                #enrollment_link=enrollment_link
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                course.image = request.FILES['image']
                
            course.save()
            return JsonResponse({"success": True})
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})

@require_admin_login
def update_course(request):
    """Update an existing course"""
    if request.method == "POST":
        try:
            course_id = request.POST.get("id")
            course = Course.objects.get(id=course_id)
            
            course.title = request.POST.get("title", course.title)
            course.description = request.POST.get("description", course.description)
            course.is_active = request.POST.get("is_active") == "true"
            course.roadmap_link = request.POST.get("roadmap_link", course.roadmap_link)
            #course.enrollment_link = request.POST.get("enrollment_link", course.enrollment_link)
            
            # Handle image upload
            if 'image' in request.FILES:
                # Delete old image if exists
                if course.image:
                    if os.path.isfile(course.image.path):
                        os.remove(course.image.path)
                course.image = request.FILES['image']
                
            course.save()
            return JsonResponse({"success": True})
        except Course.DoesNotExist:
            return JsonResponse({"success": False, "error": "Course not found"})
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})

@require_admin_login
def delete_course(request, course_id):
    """Delete a course"""
    if request.method == "POST":
        try:
            course = Course.objects.get(id=course_id)
            
            # Check if any quiz is associated with this course
            try:
                quiz = Quiz.objects.get(course=course)
                # Delete the quiz and related data
                quiz.delete()
            except Quiz.DoesNotExist:
                pass
                
            # Delete course
            course.delete()
            return JsonResponse({"success": True})
        except Course.DoesNotExist:
            return JsonResponse({"success": False, "error": "Course not found"})
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})

def get_quiz_details(request, quiz_id):
    """Fetch quiz details for editing"""
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        data = {
            'id': quiz.id,
            'title': quiz.title,
            'course_id': quiz.course.id,
            'description': quiz.description,
            'duration': quiz.duration,
            'is_active': quiz.is_active if hasattr(quiz, 'is_active') else True,
        }
        return JsonResponse({'success': True, 'quiz': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def add_quiz(request):
    """Add a new quiz"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['title', 'course_id', 'duration', 'description']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'{field} is required')
            
            # Get the associated course
            course = get_object_or_404(Course, id=data['course_id'])
            
            # Create new quiz
            quiz = Quiz.objects.create(
                course=course,
                title=data['title'],
                description=data['description'],
                duration=data['duration'],
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Quiz added successfully',
                'quiz_id': quiz.id
            })
            
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def update_quiz(request):
    """Update existing quiz"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quiz_id = data.get('id')
            
            if not quiz_id:
                raise ValidationError('Quiz ID is required')
            
            quiz = get_object_or_404(Quiz, id=quiz_id)
            
            # Update quiz fields
            quiz.title = data.get('title', quiz.title)
            quiz.description = data.get('description', quiz.description)
            quiz.duration = data.get('duration', quiz.duration)
            
            # Update course if provided
            if data.get('course_id'):
                course = get_object_or_404(Course, id=data['course_id'])
                quiz.course = course
            
            quiz.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Quiz updated successfully'
            })
            
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_quiz(request, quiz_id):
    """Delete a quiz"""
    if request.method == 'POST':
        try:
            quiz = get_object_or_404(Quiz, id=quiz_id)
            quiz.delete()
            return JsonResponse({
                'success': True,
                'message': 'Quiz deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_question(request, question_id):
    """Fetch question details"""
    try:
        question = Question.objects.get(id=question_id)
        question_data = {
            'id': question.id,
            'quiz_id': question.quiz.id,
            'text': question.text,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4,
            'correct_option': question.correct_option
        }
        return JsonResponse({'success': True, 'question': question_data})
    except Question.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Question not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
def add_question(request):
    """Add a new question"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get the quiz
            quiz = Quiz.objects.get(id=data['quiz_id'])
            
            # Create question
            question = Question.objects.create(
                quiz=quiz,
                text=data['text'],
                option1=data['option1'],
                option2=data['option2'],
                option3=data['option3'],
                option4=data['option4'],
                correct_option=data['correct_option']
            )
            
            return JsonResponse({'success': True, 'question_id': question.id})
        except Quiz.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Quiz not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def update_question(request):
    """Update an existing question"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get the question
            question = Question.objects.get(id=data['id'])
            
            # Get the quiz
            quiz = Quiz.objects.get(id=data['quiz_id'])
            
            # Update question fields
            question.quiz = quiz
            question.text = data['text']
            question.option1 = data['option1']
            question.option2 = data['option2']
            question.option3 = data['option3']
            question.option4 = data['option4']
            question.correct_option = data['correct_option']
            question.save()
            
            return JsonResponse({'success': True})
        except Question.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Question not found'})
        except Quiz.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Quiz not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_question(request, question_id):
    """Delete a question"""
    if request.method == 'POST':
        try:
            question = Question.objects.get(id=question_id)
            question.delete()
            return JsonResponse({'success': True})
        except Question.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Question not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def admin_logout(request):
    """Handle admin logout"""
    # Clear admin session data
    request.session.pop("admin_id", None)
    request.session.pop("admin_username", None)
    request.session.pop("admin_full_name", None)
    return redirect("admin_login")


def dashboard(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    try:
        user = User.objects.get(id=user_id)
        courses = Course.objects.filter(is_active=True).order_by("-created_at")
        return render(
            request, "dashboard.html", {"user": user, "user_name": user.first_name, "courses": courses}
        )
    except User.DoesNotExist:
        # Handle case where user ID in session doesn't match any user
        request.session.flush()  # Clear invalid session
        return redirect("login")
    
@login_required
def course_roadmap(request, course_id):
    """Handle roadmap link redirect"""
    try:
        course = Course.objects.get(id=course_id, is_active=True)
        if course.roadmap_link:
            return redirect(course.roadmap_link)
        else:
            return JsonResponse({"error": "Roadmap link not available"}, status=404)
    except Course.DoesNotExist:
        return JsonResponse({"error": "Course not found"}, status=404)


def session_login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user_id = request.session.get("user_id")
        if user_id:
            return function(request, *args, **kwargs)
        else:
            return redirect(f"{reverse('login')}?next={request.path}")

    return wrap


# Update the quiz-related views to use the new decorator
@session_login_required
def quiz_start(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user_id = request.session.get("user_id")
    
    try:
        user = User.objects.get(id=user_id)
        
        # Check if a quiz exists for this course
        try:
            quiz = Quiz.objects.get(course=course)
        except Quiz.DoesNotExist:
            messages.error(request, "No quiz available for this course.")
            return redirect("dashboard")
        
        # Check previous quiz attempts for this quiz
        previous_attempts = QuizAttempt.objects.filter(
            user=user, 
            quiz=quiz, 
            end_time__isnull=False
        ).order_by('-end_time')
        
        # If the user has previous attempts
        if previous_attempts.exists():
            latest_attempt = previous_attempts.first()
            
            # If the user has passed the quiz before
            if latest_attempt.score >= quiz.pass_percentage:
                # Recommend jobs for this course
                job_recommendations = recommend_jobs(quiz.title, k=5)
                
                # Pass the recommendations to the template
                return render(
                    request, 
                    "quiz_start.html", 
                    {
                        "course": course, 
                        "quiz": quiz, 
                        "previous_passed": True,
                        "job_recommendations": job_recommendations
                    }
                )
            
            # If the user has not passed, allow retaking the quiz
            return render(
                request, 
                "quiz_start.html", 
                {
                    "course": course, 
                    "quiz": quiz, 
                    "previous_failed": True,
                    "latest_score": latest_attempt.score
                }
            )
        
        # No previous attempts, proceed with normal quiz start
        return render(request, "quiz_start.html", {"course": course, "quiz": quiz})
    
    except User.DoesNotExist:
        request.session.flush()
        return redirect("login")


@session_login_required
def quiz_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user_id = request.session.get("user_id")

    try:
        user = User.objects.get(id=user_id)
        # Check if user has any existing incomplete attempts
        existing_attempt = QuizAttempt.objects.filter(
            user=user, quiz=quiz, end_time__isnull=True
        ).first()

        if existing_attempt:
            attempt = existing_attempt
        else:
            attempt = QuizAttempt.objects.create(
                user=user, quiz=quiz, start_time=timezone.now()
            )

        questions = quiz.questions.all()
        return render(
            request,
            "quiz_questions.html",
            {"quiz": quiz, "questions": questions, "attempt_id": attempt.id},
        )
    except User.DoesNotExist:
        request.session.flush()
        return redirect("login")


@session_login_required
def submit_quiz(request, attempt_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    user_id = request.session.get("user_id")
    try:
        user = User.objects.get(id=user_id)
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=user)

        if attempt.end_time:
            return JsonResponse({"error": "Quiz already submitted"}, status=400)

        try:
            answers = json.loads(request.body)
            correct_count = 0
            total_questions = attempt.quiz.questions.count()

            for answer in answers:
                question = Question.objects.get(id=answer["question_id"])
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=answer["selected_option"],
                )
                if answer["selected_option"] == question.correct_option:
                    correct_count += 1

            score = (correct_count / total_questions) * 100

            attempt.end_time = timezone.now()
            attempt.score = score
            attempt.save()

            return JsonResponse(
                {"success": True, "redirect_url": f"/quiz/{attempt.id}/result/"}
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)


def recommend_jobs(topic, k=5):
    """Recommend jobs based on the quiz topic."""
    import os
    import re
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from django.conf import settings
    
    try:
        # Path to the dataset
        dataset_path = os.path.join(settings.STATIC_ROOT, 'dataset', 'linkedin_job_posts_insights.xlsx')
        # If STATIC_ROOT is not configured, try with STATICFILES_DIRS
        if not os.path.exists(dataset_path):
            dataset_path = os.path.join(settings.BASE_DIR, 'cgs', 'static', 'dataset', 'linkedin_job_posts_insights.xlsx')
        
        # Load dataset
        df = pd.read_excel(dataset_path)
        
        # Clean the data
        # Fill missing values
        df.loc[:, 'seniority_level'] = df['seniority_level'].fillna("Not Specified")
        df.loc[:, 'employment_type'] = df['employment_type'].fillna("Not Specified")
        df.loc[:, 'industry'] = df['industry'].fillna("Unknown Industry")
        df.loc[:, 'location'] = df['location'].fillna("Unknown Location")
        df.loc[:, 'job_function'] = df['job_function'].fillna("General")
        
        # Drop rows with missing essential data
        df.dropna(subset=['job_title', 'company_name'], inplace=True)
        
        # Clean text function
        def clean_text(text):
            if pd.isna(text):
                return ""
            text = str(text).lower().strip()
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
            return text
        
        # Apply text cleaning
        text_columns = ['job_title', 'company_name', 'location', 'seniority_level', 'employment_type', 'industry']
        for col in text_columns:
            df[col] = df[col].apply(clean_text)
        
        # Create combined features
        df['combined_features'] = df['job_title'] + " " + df['company_name'] + " " + df['industry'] + " " + df['seniority_level'] + " " + df['employment_type']
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(df['combined_features'])
        
        # Transform user topic into TF-IDF vector
        user_tfidf = vectorizer.transform([topic])
        
        # Compute similarity
        similarity_scores = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
        
        # Get top-k job indices
        top_indices = np.argpartition(similarity_scores, -k)[-k:]
        top_k = top_indices[np.argsort(-similarity_scores[top_indices])]
        
        recommendations = []
        for job_idx in top_k:
            industry = df.iloc[job_idx]['industry']
            if pd.isna(industry) or industry.strip() == "":
                industry = "Not Specified"
                
            recommendations.append({
                'job_title': df.iloc[job_idx]['job_title'],
                'company_name': df.iloc[job_idx]['company_name'],
                'seniority_level': df.iloc[job_idx]['seniority_level'],
                'employment_type': df.iloc[job_idx]['employment_type'],
                'location': df.iloc[job_idx]['location'],
                'industry': industry,
                'similarity': round(float(similarity_scores[job_idx]), 4)
            })
        
        return recommendations
    except Exception as e:
        print(f"Error recommending jobs: {str(e)}")
        return []
    
@session_login_required
def course_materials(request, course_id):
    user_id = request.session.get("user_id")
    try:
        user = User.objects.get(id=user_id)
        course = get_object_or_404(Course, id=course_id)
        
        # Get all materials for this course ordered by their order
        materials = Material.objects.filter(course=course, is_active=True).order_by('order')
        
        # Get user progress for each material
        total_materials = materials.count()
        completed_count = 0
        
        for material in materials:
            try:
                # Try to get existing user progress
                user_progress = UserProgress.objects.get(user=user, material=material)
                material.user_progress = user_progress
                if user_progress.completed:
                    completed_count += 1
            except UserProgress.DoesNotExist:
                # If no progress exists, set to None
                material.user_progress = None
        
        # Calculate progress percentage
        progress_percentage = 0 if total_materials == 0 else (completed_count / total_materials) * 100
        
        return render(request, "course_materials.html", {
            "user": user,
            "course": course,
            "materials": materials,
            "total_materials": total_materials,
            "completed_count": completed_count,
            "progress_percentage": progress_percentage
        })
    
    except User.DoesNotExist:
        request.session.flush()
        return redirect("login")

@session_login_required
def mark_material_complete(request, material_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    user_id = request.session.get("user_id")
    try:
        user = User.objects.get(id=user_id)
        material = get_object_or_404(Material, id=material_id)
        
        # Get or create user progress
        user_progress, created = UserProgress.objects.get_or_create(
            user=user,
            material=material,
            defaults={"completed": True}
        )
        
        # If progress record exists but not completed, mark as completed
        if not created and not user_progress.completed:
            user_progress.completed = True
            user_progress.save()
        
        # Count total and completed materials for this course
        total_materials = Material.objects.filter(course=material.course, is_active=True).count()
        completed_count = UserProgress.objects.filter(
            user=user, 
            material__course=material.course,
            completed=True
        ).count()
        
        # Log user activity
        UserActivity.objects.create(
            user=user,
            activity_type="course_material",
            description=f"Completed material: {material.title}",
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({
            "success": True,
            "completed_count": completed_count,
            "total_materials": total_materials
        })
    
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@session_login_required
def progress(request):
    user_id = request.session.get("user_id")
    try:
        user = User.objects.get(id=user_id)
        
        # Get all courses that have materials
        courses_with_materials = Course.objects.filter(materials__isnull=False).distinct()
        
        # Get all quiz attempts where the user failed
        # Using django.db.models.F to compare fields
        from django.db.models import F
        failed_quiz_attempts = QuizAttempt.objects.filter(
            user=user,
            score__lt=F('quiz__pass_percentage')
        ).values_list('quiz__course', flat=True).distinct()
        
        in_progress_courses = []
        completed_courses = []
        
        for course in courses_with_materials:
            # Get all materials for this course
            materials = Material.objects.filter(course=course, is_active=True)
            total_materials = materials.count()
            
            if total_materials > 0:
                # Get completed materials count
                completed_materials = UserProgress.objects.filter(
                    user=user,
                    material__course=course,
                    material__is_active=True,
                    completed=True
                ).count()
                
                # Calculate completion percentage
                completion_percentage = round((completed_materials / total_materials) * 100)
                
                # Calculate SVG circle dasharray value (circumference = 2πr = 2 * π * 40 = 251.2)
                progress_dasharray = (completion_percentage / 100) * 251.2
                
                # Get last accessed date
                last_progress = UserProgress.objects.filter(
                    user=user,
                    material__course=course
                ).order_by('-last_accessed').first()
                
                last_accessed = last_progress.last_accessed if last_progress else timezone.now()
                
                course_data = {
                    'id': course.id,
                    'title': course.title,
                    'description': course.description,
                    'image': course.image,
                    'total_materials': total_materials,
                    'completed_materials': completed_materials,
                    'completion_percentage': completion_percentage,
                    'progress_dasharray': progress_dasharray,
                    'last_accessed': last_accessed,
                }
                
                # Check if the user has any completed materials in this course
                # This indicates the user has enrolled in the course
                has_enrolled = UserProgress.objects.filter(
                    user=user,
                    material__course=course
                ).exists()
                
                # Add to appropriate list based on completion status
                # Only show in progress courses if the user has failed the quiz and enrolled
                if completion_percentage == 100:
                    course_data['completion_date'] = last_accessed
                    completed_courses.append(course_data)
                elif course.id in failed_quiz_attempts and has_enrolled:
                    in_progress_courses.append(course_data)
        
        # Sort courses - in progress by last accessed (newest first), completed by completion date
        in_progress_courses.sort(key=lambda x: x['last_accessed'], reverse=True)
        completed_courses.sort(key=lambda x: x['completion_date'], reverse=True)
        
        return render(request, "progress.html", {
            "user": user,
            "in_progress_courses": in_progress_courses,
            "completed_courses": completed_courses,
        })
    
    except User.DoesNotExist:
        request.session.flush()
        return redirect("login")
    
def recommend_courses(topic, k=5):
    """Recommend courses based on the quiz topic when a user fails."""
    import os
    import re
    import pandas as pd
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from django.conf import settings
    
    try:
        # Path to the dataset
        dataset_path = os.path.join(settings.STATIC_ROOT, 'dataset', 'coursea_data.csv')
        # If STATIC_ROOT is not configured, try with STATICFILES_DIRS
        if not os.path.exists(dataset_path):
            dataset_path = os.path.join(settings.BASE_DIR, 'cgs', 'static', 'dataset', 'coursea_data.csv')
        
        # Load dataset
        df = pd.read_csv(dataset_path)
        
        # Clean the data
        # Fill missing values
        df.loc[:, 'course_difficulty'] = df['course_difficulty'].fillna("Mixed")
        df.loc[:, 'course_organization'] = df['course_organization'].fillna("Unknown")
        df.loc[:, 'course_rating'] = df['course_rating'].fillna(0.0)
        
        # Drop rows with missing essential data
        df.dropna(subset=['course_title'], inplace=True)
        
        # Clean text function
        def clean_text(text):
            if pd.isna(text):
                return ""
            text = str(text).lower().strip()
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
            return text
        
        # Apply text cleaning
        text_columns = ['course_title', 'course_organization', 'course_difficulty']
        for col in text_columns:
            df[col] = df[col].apply(clean_text)
        
        # Create combined features
        df['combined_features'] = df['course_title'] + " " + df['course_organization'] + " " + df['course_difficulty']
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(df['combined_features'])
        
        # Transform user topic into TF-IDF vector
        user_tfidf = vectorizer.transform([topic])
        
        # Compute similarity
        similarity_scores = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
        
        # Get top-k course indices
        top_indices = np.argpartition(similarity_scores, -k)[-k:]
        top_k = top_indices[np.argsort(-similarity_scores[top_indices])]
        
        recommendations = []
        for course_idx in top_k:
            difficulty = df.iloc[course_idx]['course_difficulty']
            if pd.isna(difficulty) or difficulty.strip() == "":
                difficulty = "Mixed"
                
            students_enrolled = df.iloc[course_idx].get('course_students_enrolled', 0)
            if pd.isna(students_enrolled):
                students_enrolled = 0
                
            recommendations.append({
                'course_title': df.iloc[course_idx]['course_title'],
                'course_organization': df.iloc[course_idx]['course_organization'],
                'course_difficulty': difficulty,
                'course_rating': round(float(df.iloc[course_idx].get('course_rating', 0)), 1),
                'course_students_enrolled': students_enrolled,
                'similarity': round(float(similarity_scores[course_idx]), 4)
            })
        
        return recommendations
    except Exception as e:
        print(f"Error recommending courses: {str(e)}")
        return []

@session_login_required
def quiz_result(request, attempt_id):
    user_id = request.session.get("user_id")
    try:
        user = User.objects.get(id=user_id)
        attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=user)
        passed = attempt.score >= attempt.quiz.pass_percentage
        
        # Get job recommendations if user passed the quiz
        job_recommendations = []
        course_recommendations = []
        
        if passed:
            # Use the quiz title or topic as the search query
            topic = attempt.quiz.title
            job_recommendations = recommend_jobs(topic, k=5)
        else:
            # Recommend courses if the user failed
            topic = attempt.quiz.title
            course_recommendations = recommend_courses(topic, k=5)
        
        return render(
            request, 
            "quiz_result.html", 
            {
                "attempt": attempt, 
                "passed": passed,
                "job_recommendations": job_recommendations,
                "course_recommendations": course_recommendations
            }
        )
    except User.DoesNotExist:
        request.session.flush()
        return redirect("login")
    
def settings(request):
    """Render settings page"""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    try:
        # Get the complete user object
        user = User.objects.get(id=user_id)
        
        # Default active tab is password-settings
        active_tab = request.POST.get('active_tab', 'password-settings')
        
        return render(request, "settings.html", {
            "user": user,  # Pass the complete user object
            "user_name": user.first_name + " " + user.last_name,
            "user_email": user.email,
            "active_tab": active_tab
        })
    except User.DoesNotExist:
        # If user doesn't exist, clear session and redirect to login
        request.session.flush()
        return redirect("login")

def change_password(request):
    """Handle password change functionality"""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    
    user_name = request.session.get("user_name", "User")
    user_email = request.session.get("user_email", "")
    context = {
        "user_name": user_name,
        "user_email": user_email,
        "active_tab": "password-settings"
    }
    
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        
        try:
            user = User.objects.get(id=user_id)
            
            # Verify current password
            if not check_password(current_password, user.password):
                messages.error(request, "Current password is incorrect.")
                return render(request, "settings.html", context)
            
            # Validate new password
            if new_password != confirm_password:
                messages.error(request, "New password and confirmation do not match.")
                return render(request, "settings.html", context)
            
            if check_password(new_password, user.password):
                messages.warning(request, "New password cannot be the same as your current password.")
                return render(request, "settings.html", context)
            
            if len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return render(request, "settings.html", context)
            
            if not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password):
                messages.error(request, "Password must contain both letters and numbers.")
                return render(request, "settings.html", context)
            
            # Update password
            user.password = make_password(new_password)
            user.save()
            
            messages.success(request, "Password changed successfully.")
            return redirect("dashboard")
            
        except User.DoesNotExist:
            messages.error(request, "An error occurred. Please try logging in again.")
            return redirect("login")
    
    # If GET request, show settings page with password tab active
    return render(request, "settings.html", context)

@session_login_required
def profile_view(request):
    user_id = request.session.get("user_id")
    try:
        user = User.objects.get(id=user_id)
        context = {"user": user, "user_name": request.session.get("user_name", "")}
        return render(request, "profile.html", context)
    except User.DoesNotExist:
        request.session.flush()
        return redirect("login")


@session_login_required
def update_profile(request):
    if request.method == "POST":
        user = User.objects.get(id=request.session["user_id"])
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.contact_number = request.POST.get("contact_number")
        user.date_of_birth = request.POST.get("date_of_birth")  # Add this line
        user.skills = request.POST.get("skills")
        user.interests = request.POST.get("interests")
        user.save()

        # Update session with new name
        full_name = f"{user.first_name} {user.last_name}"
        request.session["user_name"] = full_name

        return JsonResponse({"success": True, "user_name": full_name})
    return JsonResponse({"success": False})


@session_login_required
def update_profile_picture(request):
    if request.method == "POST" and request.FILES.get("profile_picture"):
        try:
            user_id = request.session.get("user_id")
            user = User.objects.get(id=user_id)

            # Delete old profile picture if it exists
            if user.profile_picture:
                try:
                    old_picture_path = os.path.join(
                        settings.MEDIA_ROOT, str(user.profile_picture)
                    )
                    if os.path.exists(old_picture_path):
                        os.remove(old_picture_path)
                except Exception as e:
                    print(f"Error deleting old profile picture: {str(e)}")

            # Validate and save new profile picture
            profile_picture = request.FILES["profile_picture"]
            allowed_types = ["image/jpeg", "image/png", "image/gif"]

            if profile_picture.content_type not in allowed_types:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Invalid file type. Please upload a JPEG, PNG, or GIF image.",
                    },
                    status=400,
                )

            if profile_picture.size > 5 * 1024 * 1024:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "File size too large. Maximum size is 5MB.",
                    },
                    status=400,
                )

            user.profile_picture = profile_picture
            user.save()

            return JsonResponse(
                {
                    "success": True,
                    "profile_picture_url": user.get_profile_picture_url(),
                    "message": "Profile picture updated successfully",
                }
            )

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"An error occurred: {str(e)}"}, status=500
            )

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@session_login_required
def delete_profile_picture(request):
    if request.method == "POST":
        try:
            user_id = request.session.get("user_id")
            user = User.objects.get(id=user_id)

            if user.profile_picture:
                # Delete the file from storage
                try:
                    old_picture_path = os.path.join(
                        settings.MEDIA_ROOT, str(user.profile_picture)
                    )
                    if os.path.exists(old_picture_path):
                        os.remove(old_picture_path)
                except Exception as e:
                    print(f"Error deleting profile picture: {str(e)}")

                # Clear the profile picture field
                user.profile_picture = None
                user.save()

            return JsonResponse(
                {"success": True, "message": "Profile picture removed successfully"}
            )

        except Exception as e:
            return JsonResponse(
                {"success": False, "error": f"An error occurred: {str(e)}"}, status=500
            )

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

def quiz_results(request):
    """
    Display quiz results page with attempted and unattempted quizzes
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    try:
        user = User.objects.get(id=user_id)
        
        # Get the latest quiz attempt for each quiz
        from django.db.models import Max
        latest_attempts = QuizAttempt.objects.filter(user=user).values('quiz').annotate(
            latest_end_time=Max('end_time')
        )
        
        # Create a lookup dictionary for the latest attempt for each quiz
        latest_attempt_lookup = {
            item['quiz']: item['latest_end_time'] 
            for item in latest_attempts
        }
        
        # Get only the latest attempts
        quiz_attempts = []
        for quiz_id, latest_time in latest_attempt_lookup.items():
            attempt = QuizAttempt.objects.filter(
                user=user,
                quiz_id=quiz_id,
                end_time=latest_time
            ).select_related('quiz', 'quiz__course').first()
            
            if attempt:
                quiz_attempts.append(attempt)
        
        # Create a list of attempted quizzes with result details
        attempted_quizzes = []
        attempted_quiz_ids = set()
        
        for attempt in quiz_attempts:
            quiz = attempt.quiz
            course = quiz.course
            
            # Calculate if quiz is passed
            is_passed = attempt.score >= quiz.pass_percentage if attempt.score is not None else False
            
            attempted_quizzes.append({
                'course_title': course.title,
                'quiz_title': quiz.title,
                'score': attempt.score or 0,
                'pass_percentage': quiz.pass_percentage,
                'is_passed': is_passed,
                'date': attempt.end_time
            })
            
            attempted_quiz_ids.add(quiz.id)
        
        # Get unattempted quizzes (rest of your code remains the same)
        unattempted_quizzes = Quiz.objects.filter(
            course__is_active=True
        ).exclude(
            id__in=attempted_quiz_ids
        ).select_related('course')
        
        unattempted_quiz_list = [{
            'course_title': quiz.course.title,
            'quiz_title': quiz.title,
            'description': quiz.description,
            'pass_percentage': quiz.pass_percentage,
            'course_id': quiz.course.id  # Pass the course ID for quiz start URL
        } for quiz in unattempted_quizzes]
        
        context = {
            'user': user,
            'user_name': request.session.get("user_name", "User"),
            'attempted_quizzes': attempted_quizzes,
            'unattempted_quizzes': unattempted_quiz_list
        }
        
        return render(request, "quiz_results.html", context)
    
    except User.DoesNotExist:
        request.session.flush()
        return redirect("login")