from django.contrib import admin
from django.contrib.auth.hashers import make_password 
from .models import User, Admin, Course, Quiz, Question, QuizAttempt, UserAnswer, UserActivity, Material,UserProgress

# Register your models here.
@admin.register(Admin)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'full_name', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'full_name']
    list_filter = ['is_active']
    
    fieldsets = (
        ('Admin Information', {
            'fields': ('username', 'email', 'full_name', 'password')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.password.startswith('pbkdf2_sha256$'):
            obj.password = make_password(obj.password)
        obj.save()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Define the fieldsets to organize fields into sections
    fieldsets = (
        ('User Credentials', {
            'fields': ('email', 'password'),
        }),
        ('Personal Details', {
            'fields': ('profile_picture','first_name', 'last_name', 'date_of_birth', 'contact_number'),
        }),
        ('Skills and Interests', {
            'fields': ('skills', 'interests'),
        }),
        ('Terms Accepted', {
            'fields': ('terms_accepted',),
        }),
    )
    
    # Define the fields to be displayed in the list view
    list_display = ['first_name', 'last_name', 'email', 'terms_accepted']
    
    # Add search functionality on the email field
    search_fields = ['email', 'first_name', 'last_name']
    
    # Add filter functionality for the 'terms_accepted' field
    list_filter = ['terms_accepted']
    
    # Optionally, you can add the ability to change password directly in the admin panel
    def save_model(self, request, obj, form, change):
        if not change:  # Hash the password only when the user is created (not updated)
            obj.password = make_password(obj.password)
        obj.save()

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_active']
    fields = ['title', 'description', 'image', 'roadmap_link', 'is_active']
    search_fields = ['title', 'description']
    list_filter = ['is_active', 'created_at']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'duration', 'pass_percentage']
    search_fields = ['title', 'course__title']
    list_filter = ['course']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'correct_option']
    search_fields = ['text', 'quiz__title']
    list_filter = ['quiz']

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'start_time', 'end_time', 'score']
    search_fields = ['user__email', 'quiz__title']
    list_filter = ['quiz', 'user']

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_option']
    search_fields = ['attempt__user__email', 'question__text']
    list_filter = ['attempt__quiz']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'description', 'ip_address', 'timestamp']
    search_fields = ['user__email', 'activity_type', 'description', 'ip_address']
    list_filter = ['activity_type', 'timestamp']
    readonly_fields = ['user', 'activity_type', 'description', 'ip_address', 'timestamp']
    
    def has_add_permission(self, request):
        # Prevent manual creation of activity logs through admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent editing of activity logs
        return False

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'material_type', 'order', 'is_active', 'created_at']
    list_filter = ['material_type', 'is_active', 'course']
    search_fields = ['title', 'description', 'course__title']
    ordering = ['course', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description',)
        }),
        ('Content', {
            'fields': ('material_type','content',)
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'material', 'completed', 'last_accessed']
    list_filter = ['completed', 'last_accessed', 'material__course']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'material__title']
    
    fieldsets = (
        ('User & Material', {
            'fields': ('user', 'material')
        }),
        ('Progress', {
            'fields': ('completed', 'last_accessed')
        }),
    )
    
    # Optional: Make last_accessed readonly since it updates automatically
    readonly_fields = ['last_accessed']