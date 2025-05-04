from django.contrib import admin
from .models import *

# Register your models here.
class stuRegistrationList(admin.ModelAdmin):
    list_display=('name','mobileno','Course','regdate1','isActive')
    search_fields =('name','mobileno','Course')

admin.site.register(tblStudentRegistration,stuRegistrationList)

class stuLoginList(admin.ModelAdmin):
    list_display=('Username','isActive')
   
admin.site.register(tblLogin,stuLoginList)

class stuCourseList(admin.ModelAdmin):
    list_display=('course', 'name', 'mobileno','regdate1','isActive')
    
admin.site.register(tblStuCourse,stuCourseList)

class CourseList(admin.ModelAdmin):
    list_display=('course','isActive')
    search_fields =('course','isActive')

admin.site.register(tblcourse,CourseList)

class stuMaterialList(admin.ModelAdmin):
    list_display=('course','Topic','VideoMaterial','TextMaterial','Program','isActive')
    search_fields =('course','Topic')
    
admin.site.register(tblMaterial,stuMaterialList)

class tblAdminloginList(admin.ModelAdmin):
    list_display=('username','Password')
    search_fields =('username','Password')

admin.site.register(tblAdminlogin,tblAdminloginList)

class tblStuquerylist(admin.ModelAdmin):
    list_display=( 'Id', 'mobileno','subject', 'query', 'queryans')
    search_fields =('mobileno','subject', 'query')

admin.site.register(tblStuquery,tblStuquerylist)

admin.site.register(tblEmpDetails)

admin.site.register(tblEmpCourse)

    

