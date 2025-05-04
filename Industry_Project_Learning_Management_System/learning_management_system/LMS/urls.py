"""
URL configuration for MyProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

# ======================================================== Urls For User ==================================================================

path('',index,name=''),
path('mess/',message,name='mess'),
path('error/',Error,name='error'),
path('contact/',contact,name='contact'),
path('course/',course,name='course'),
#path('admin/', admin.site.urls),

path('UserRegistration/',UserRegistration,name='UserRegistration'),
path('do_UserRegistration/',do_UserRegistration,name='do_UserRegistration'),
path('UserLogin/',UserLogin, name='UserLogin'),
path('do_UserLogin/',do_UserLogin,name='do_UserLogin'),    
path('material/<str:Course>/<str:sdate>',material, name='material'),
path('AddStuCourse/<str:mobileno>',AddStuCourse, name='AddStuCourse'),
path('do_AddStuCourse/',do_AddStuCourse),
path('AddStuQuery/<str:mobileno>',AddStuQuery, name = 'AddStuQuery'),
path('do_AddStuQuery/',do_AddStuQuery, name = 'do_AddStuQuery'),
path('StuQueryResponse/<str:mobileno>',StuQueryResponse, name='StuQueryResponse'),

# ========================================================= Urls For Admin ===============================================================

path('Adminlogin/',Adminlogin, name='Adminlogin'),
path('do_Adminlogin/',do_Adminlogin,name='do_Adminlogin'),
path('AdminHome/',AdminHome,name='AdminHome'),
path('AdmiCourse/',AdmiCourse,name='AdmiCourse'),
path('Adminaddcourse/',Adminaddcourse, name ='Adminaddcourse'),
path('do_Adminaddcourse/',do_Adminaddcourse, name ='do_Adminaddcourse'),
path('updatecourse/<str:course>',updatecourse,name='updatecourse'),
path('do_updatecourse/',do_updatecourse, name ='do_updatecourse'),
path('adminmaterial/<str:course>',adminmaterial,name='adminmaterial'),
path('allmaterials/<str:Course>/<str:sdate>',allmaterials, name='allmaterials'),
path('AdminaddEmp/',AdminaddEmp, name ='AdminaddEmp'),
path('do_AdminaddEmp/',do_AdminaddEmp, name ='do_AdminaddEmp'),
path('uploadmaterial/',uploadmaterial,name='uploadmaterial/'),
path('do_uploadmaterial/',do_uploadmaterial,name='do_uploadmaterial/'),
path('UserList/',UserList,name='UserList'),
path('UpdateUserInfo/<str:mobileno>',UpdateUserInfo,name='UpdateUserInfo'),
path('do_UpdateUserInfo/',do_UpdateUserInfo,name='do_UpdateUserInfo'),
path('EmpList/',EmpList,name='EmpList'),
path('UpdateEmpInfo/<str:ContactNo>',UpdateEmpInfo,name='UpdateEmpInfo'),
path('do_UpdateEmpInfo/',do_UpdateEmpInfo,name='do_UpdateEmpInfo'),
path('Queries_Responses/',Queries_Responses,name='Queries_Responses'),


# ========================================================= Urls For Employee =============================================================

path('Emplogin/',Emplogin, name='Emplogin'),
path('do_Emplogin/',do_Emplogin,name='do_Emplogin'),
path('StuList/<str:course>',StuList,name='StuList'),
path('HREmpList/<str:course>',HREmpList,name='HREmpList'),
path('Empuploadmaterial/<str:Course>',Empuploadmaterial,name='Empuploadmaterial'),
path('QueryList/<str:Course>',QueryList, name='QueryList'),
path('QueryResponse/<int:Id>',QueryResponse, name='QueryResponse'),
path('do_QueryResponse/',do_QueryResponse, name='do_QueryResponse'),


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
