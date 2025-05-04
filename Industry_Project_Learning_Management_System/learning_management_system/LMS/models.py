from django.db import models
import os
from django.core.exceptions import ValidationError

# Create your models here.

def validate_video_file(value):
    ext = os.path.splitext(value.name)[1]  # Get the file extension
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']  # List of allowed video file extensions

    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file format. Please upload a valid video file.')

def upload_video_to(instance, filename):
    return f'Video/{filename}'

# ========================================================== Tables For User =============================================================

class tblStudentRegistration(models.Model):
    Id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=100)
    mobileno = models.CharField(max_length=15)
    Course = models.CharField(max_length=100)
    coursefee = models.IntegerField(null= True, blank=True)
    address = models.CharField(max_length=600)
    Password = models.CharField(max_length=30)
    regdate1 = models.DateField(auto_now=True)    
    isActive = models.BooleanField(default=False)   

class tblLogin(models.Model):
    Id = models.AutoField(primary_key=True)
    Username = models.CharField(max_length = 50)
    Password = models.CharField(max_length = 50)
    isActive = models.BooleanField(default=False)

class tblStuCourse(models.Model):
    Id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    mobileno = models.CharField(max_length=15)
    course = models.CharField(max_length=100) 
    regdate1 = models.DateField(auto_now=True)
    modifiedBy = models.CharField(max_length=15, null= True, blank=True)    
    isActive = models.BooleanField(default=False)

class tblStuquery(models.Model):
    Id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=25, null= True, blank=True)
    mobileno = models.CharField(max_length=15)    
    subject = models.CharField(max_length=25)
    query = models.CharField(max_length=500)
    queryans = models.CharField(max_length=500)
    CreatedDate = models.DateField(auto_now=True)
    ModifiedBy = models.CharField(max_length=15, null= True, blank=True)
    ModifiedDate = models.DateField(auto_now=True)      
    isCompleted = models.BooleanField(default=False, null= True)    
    isActive = models.BooleanField(default=True, null= True)
 
class tblcourse(models.Model):
    Id = models.AutoField(primary_key=True)
    course = models.CharField(max_length=30)
    coursefee = models.IntegerField(null= True, blank=True)
    isActive = models.BooleanField(default=False)   
    isDeleted = models.BooleanField(default=False)
    CreatedBy = models.CharField(max_length=15, null= True, blank=True)       
    CreatedDate = models.DateField(auto_now=True)

class tblMaterial(models.Model):
    Id = models.AutoField(primary_key=True)
    course = models.CharField(max_length=30,null= True, blank=True)
    Topic = models.CharField(max_length=100)
    VideoMaterial =  models.FileField(
        upload_to=upload_video_to,
        null=True,
        validators=[validate_video_file]
    )
    TextMaterial = models.FileField(upload_to="TextMaterial/",null=True,blank=True)
    Program = models.FileField(upload_to="Program/",null=True,blank=True)
    isActive =models.BooleanField(default=False)   
    isDeleted = models.BooleanField(default=False)
    CreatedBy = models.CharField(max_length=15, null= True, blank=True)       
    CreatedDate = models.DateField(auto_now=True)
    ModifiedBy = models.CharField(max_length=15, null= True, blank=True)       
    ModifiedDate = models.DateField(auto_now=True)

# ========================================================== Tables For Admin =============================================================

class tblAdminlogin(models.Model):
    Id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=200)    
    Password = models.CharField(max_length=30)
    regdate1 = models.DateField(auto_now=True)    
    isActive = models.BooleanField(default=False)  

# ========================================================== Tables For Employee ===========================================================

class tblEmpDetails(models.Model):
    Id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    ContactNo = models.CharField(max_length=20)
    Email = models.CharField(max_length=100)
    address = models.CharField(max_length=600)
    Designation = models.CharField(max_length=50)
    Course = models.CharField(max_length=50, null=True)
    Password = models.CharField(max_length=30)
    Createdate = models.DateField(auto_now=True)
    Modifydate = models.DateField(auto_now=True)
    isActive = models.BooleanField(default=False)
    isDeactive = models.BooleanField(default=False)

class tblEmpCourse(models.Model):
    Id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    ContactNo = models.CharField(max_length=20)
    Course = models.CharField(max_length=50, null=True)
    isActive = models.BooleanField(default=False)