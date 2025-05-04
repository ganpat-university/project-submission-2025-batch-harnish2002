from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse 
from django.conf import settings
import os
from .models import *
from datetime import date
from django.contrib.auth.hashers import check_password
from django.contrib.sessions.models import Session
# from django.contrib.auth.models import User

# =================================================== View Functions here ================================================================

def message(request):
    return HttpResponse("Hello computer")

def Error(request):
    return HttpResponse("This page can't Load")

def index(request):
    return render(request,'index.html')

def contact(request):
    return render(request,'frmContact.html')

def course(request):
    return render(request,'frmCourse.html')

# ===================================================== Functions For User ===============================================================

def UserRegistration(request):
    return render(request,'frmRegistration.html')

def UserRegistration(request):
    courses = tblcourse.objects.all()
    context = {'courses': courses}
    return render(request, 'User/frmRegistration.html', context)

def registration_view(request):
    courses = tblcourse.objects.filter(isActive=True)
    if request.method == 'POST':                                             # Handle form submission
        selected_course = request.POST.get('course')                         # You can get the selected course from request.POST['course']
        course_fee = tblcourse.objects.get(course=selected_course).coursefee # Fetch course fee based on the selected course
    else:
        return render(request, 'registration.html', {'courses': courses}) 

def do_UserRegistration(request):
    password = request.POST.get('Password')
    retype = request.POST.get('repassword')
    print(password)
    print(retype)
    if password == retype :
        if request.method == 'POST':
            s = tblStudentRegistration()
            s.name = request.POST.get('name')
            s.address = request.POST.get('address')
            s.mobileno = request.POST.get('mobileno')
            s.email = request.POST.get('email')        
            s.Course = request.POST.get('course')
            s.coursefee = request.POST.get('coursefee')
            s.Password = request.POST.get('Password')
            s.save()

            sc = tblStuCourse()
            sc.name = request.POST.get('name')
            sc.mobileno = request.POST.get('mobileno')
            sc.course = request.POST.get('course')
            sc.save()
        return render(request,'User/frmLogin.html')
    else:
        return HttpResponse("Password do not Match")

def UserLogin(request):
    return render(request,'User/frmLogin.html')

def do_UserLogin(request):
    if request.method == 'POST':
        mobilenum = request.POST.get('mobileno')            
        s1 = tblStuCourse.objects.filter(mobileno=mobilenum)
        if not s1.exists():
            return HttpResponse("Mobile is not registered")
        else:
            request.session['mobileno'] = mobilenum
            data = {
                'MYCourse': s1,
                'mobilenum': request.session.get('mobileno')
            }
            return render(request, "User/frmStudentCourse.html", data)

def material(request,Course,sdate):
    valcourse = Course
    current_date = date.today()
    sdate = date.fromisoformat(sdate)
    date_difference = (current_date - sdate).days  
    st_list = tblMaterial.objects.filter(course=valcourse)    
    data = {       
        'CourseData': st_list,
        'dd' : date_difference+1,
        'count':1,
    }
    return render(request,'User/frmStuMaterial.html',data)    

def AddStuCourse(request,mobileno):
    valmobileno = mobileno
    courses =   tblcourse.objects.all()
    data = {
        'mobno' : valmobileno,
        'courses': courses,
        'mobilenum': request.session.get('mobileno')    
    }  
    return render(request,'User/frmAddStuCourse.html',data)

def do_AddStuCourse(request):
    if request.method == 'POST':
        s = tblStuCourse()
        s.mobileno = request.POST.get('mobileno')                   
        s.course = request.POST.get('course')            
        s.save()
        mobilenum = request.POST.get('mobileno')            
        s1 = tblStuCourse.objects.filter(mobileno=mobilenum)
        data = {
            'MYCourse': s1
        }
    return render(request, "User/frmStudentCourse.html", data)

def AddStuQuery(request,mobileno):
    courses = tblcourse.objects.all()
    context = {
        'courses': courses,
        'mobno': mobileno, # Pass the mobile number to the template
        'mobilenum': request.session.get('mobileno')
    }
    return render(request, 'User/frmStuQuery.html', context)

def do_AddStuQuery(request):
    q = tblStuquery()
    q.mobileno = request.POST.get('mobileno')
    q.subject = request.POST.get('course')
    q.query = request.POST.get('txtquery')
    q.save()
    return render(request, 'User/frmStuQuery.html')

def StuQueryResponse(request, mobileno):
    queries = tblStuquery.objects.filter(mobileno=mobileno)
    data = {
            'Queries': queries,
            'mobilenum': request.session.get('mobileno')
        }
    return render(request,'User/frmStuQueryResponse.html', data)


# ===================================================== Functions For Admin ===============================================================

def Adminlogin(request):
    return render(request,'Admin/frmAdminLogin.html')

def do_Adminlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')            
        print(password)
        matching_users = tblAdminlogin.objects.filter(username=username)        
        if not matching_users.exists():
            return HttpResponse("User is not registered")
        else:
            user = matching_users.first()
            if not password == user.Password:
                print("Incorrect password")
                return HttpResponse("Incorrect password")
            else:
                s1 = tblcourse.objects.all()
                s2 = tblAdminlogin.objects.filter(username=username)
                data = {
                    'MYCourse': s1,
                    'MYUser': s2
                }
                return render(request, "Admin/frmAdminWelcome.html", data)

def AdminHome(request):
    return render(request, "Admin/frmAdminWelcome.html")

def AdmiCourse(request):
    s1 = tblcourse.objects.all()
    # s2 = tblAdminlogin.objects.all()
    data = {
          'MYCourse': s1,
        #   'MYUser': s2
    }
    return render(request, "Admin/frmAdminCourse.html", data)

def Adminaddcourse(request):
    return render(request, 'Admin/frmAdminaddnewCourse.html')

def do_Adminaddcourse(request):
    c = tblcourse()
    c.course = request.POST.get('course')
    c.coursefee = request.POST.get('coursefee')
    c.save()
    all_courses = tblcourse.objects.all()    
    data = {'MYCourse': all_courses}   
    return render(request, "Admin/frmAdminCourse.html", data)

def updatecourse(request, course):
    course_obj = get_object_or_404(tblcourse, course=course)    
    return render(request, 'Admin/frmUpdateCourse.html', {'course': course_obj})

def do_updatecourse(request):    
    course_fee = request.POST.get('courseFee')
    is_active = request.POST.get('isActive')   
    is_active = is_active == 'on'    
    if course_fee is None or is_active is None:
        return HttpResponse("Invalid data provided")
    
    course_name = request.POST.get('course')
    course, created = tblcourse.objects.update_or_create(
        course=course_name,
        defaults={'coursefee': course_fee, 'isActive': is_active}
    )   
    all_courses = tblcourse.objects.all()    
    data = {'MYCourse': all_courses}   
    return render(request, "Admin/frmAdminCourse.html", data)

def adminmaterial(request,course):
    valcourse = course  
    st_list = tblMaterial.objects.filter(course=valcourse)    
    data =   {       
        'CourseData': st_list,
        'count':1,
    }
    return render(request,'Admin/frmAdminMaterial.html',data) 

def allmaterials(request):
    CourseData = tblMaterial.objects.all()
    dd = 10 
    return render(request, 'Admin/frmAdminMaterial.html', {'CourseData': CourseData, 'dd': dd})

def AdminaddEmp(request):
    return render(request, 'Admin/frmAdminaddEmp.html')

def do_AdminaddEmp(request):
        if request.method == 'POST':
            e = tblEmpDetails()
            e.name = request.POST.get('name')
            e.ContactNo = request.POST.get('ContactNo')
            e.Email = request.POST.get('Email') 
            e.address = request.POST.get('address')      
            e.Designation = request.POST.get('Designation')
            e.Password = request.POST.get('Password')
            e.isActive = request.POST.get('isActive')
            e.save()
        return render(request,'Admin/frmAdminCourse.html')

def uploadmaterial(request):
    courses = tblcourse.objects.all()
    context = {'courses': courses}
    return render(request, 'Admin/frmAdminuploadmaterial.html',context)

def do_uploadmaterial(request):
    if request.method == 'POST':
        # Handle file uploads
        file1 = request.FILES.get('file1')
        file2 = request.FILES.get('file2')
        file3 = request.FILES.get('file3')

        # Save files to specific directories
        if file1:
            save_path = os.path.join(settings.MEDIA_ROOT, 'video', file1.name)
            with open(save_path, 'wb') as f:
                for chunk in file1.chunks():
                    f.write(chunk)

        if file2:
            save_path = os.path.join(settings.MEDIA_ROOT, 'TextMaterial', file2.name)
            with open(save_path, 'wb') as f:
                for chunk in file2.chunks():
                    f.write(chunk)

        if file3:
            save_path = os.path.join(settings.MEDIA_ROOT, 'Program', file3.name)
            with open(save_path, 'wb') as f:
                for chunk in file3.chunks():
                    f.write(chunk)

        # Save form data into tblMaterial table
        course = request.POST.get('course')
        topic = request.POST.get('topic')

        material = tblMaterial.objects.create(
            course=course,
            Topic=topic,
            VideoMaterial=file1,
            TextMaterial=file2,
            Program=file3,
            isActive=True,  # Assuming it should be set to True
            CreatedBy=request.user.username  # Assuming you have user authentication
        )

        return JsonResponse({'message': 'Files and data uploaded successfully'})
    else:
        return render(request, 'Admin/frmAdminuploadmaterial.html')

def UserList(request):    
    all_Info = tblStudentRegistration.objects.all()    
    data = {'UserInfo': all_Info}
    return render(request, "Admin/frmUserList.html", data)

def UpdateUserInfo(request, mobileno):
    User_obj = get_object_or_404(tblStudentRegistration,mobileno=mobileno) 
    context = {
        'UserInfo':User_obj
    }     
    return render(request, 'Admin/frmUpdateUserInfo.html', context)

def do_UpdateUserInfo(request):    
    if request.method == 'POST':
        User_name = request.POST.get('name')
        User_address = request.POST.get('address')
        User_mobileno = request.POST.get('mobileno')
        User_email = request.POST.get('email')
        User_Course = request.POST.get('Course')
        User_coursefee = request.POST.get('coursefee')
        User_Password = request.POST.get('Password')
        User_isActive = request.POST.get('isActive') == 'on'

        tblStudentRegistration.objects.filter(mobileno=User_mobileno).update(
            name=User_name,
            address=User_address,
            email=User_email,
            Course=User_Course,
            coursefee=User_coursefee,
            Password=User_Password,
            isActive=User_isActive
        )
        all_Info = tblStudentRegistration.objects.all()    
        data = {'UserInfo': all_Info}
        return render(request, "Admin/frmUserList.html", data)

def EmpList(request):    
    all_Info = tblEmpDetails.objects.all()
    data = {'EmpInfo': all_Info}
    return render(request, 'Admin/frmEmpList.html', data)

def UpdateEmpInfo(request, ContactNo):
    Emp_obj = get_object_or_404(tblEmpDetails,ContactNo=ContactNo) 
    context = {'EmpInfo': Emp_obj}     
    return render(request, 'Admin/frmUpdateEmpInfo.html', context)

def do_UpdateEmpInfo(request):
    if request.method == 'POST':
        Emp_name = request.POST.get('name')
        Emp_ContactNo = request.POST.get('ContactNo')
        Emp_Email = request.POST.get('Email')
        Emp_address = request.POST.get('address')
        Emp_Designation = request.POST.get('Designation')
        Emp_Course = request.POST.get('Course')
        Emp_Password = request.POST.get('Password')
        Emp_isActive = request.POST.get('isActive') == 'on'

        tblEmpDetails.objects.filter(ContactNo=Emp_ContactNo).update(
            name=Emp_name,
            Email=Emp_Email,
            address=Emp_address,
            Designation=Emp_Designation,
            Course=Emp_Course,
            Password=Emp_Password,
            isActive=Emp_isActive
        )
        all_Info = tblEmpDetails.objects.all()    
        data = {'EmpInfo': all_Info}
        return render(request, "Admin/frmEmpList.html", data)

def Queries_Responses(request):
    queries = tblStuquery.objects.all()
    data = {'Queries': queries}
    return render(request,'Admin/frmQueryQueryResponse.html', data)


# ===================================================== Functions For Employee ===============================================================

def Emplogin(request):
    return render(request,'Emp/frmEmpLogin.html')

def do_Emplogin(request):
    if request.method == 'POST':
        username = request.POST.get('ContactNo')
        password = request.POST.get('password')            
        print(password)
        matching_users = tblEmpDetails.objects.filter(ContactNo=username)        
        if not matching_users.exists():
            return HttpResponse("User is not registered")
        else:
            user = matching_users.first()
            if not password == user.Password:
                print("Incorrect password")
                return HttpResponse("Incorrect password")
            else:
                Designation = user.Designation
                if Designation=='HR':
                    s1 = tblcourse.objects.all()
                    Designation = tblEmpDetails.objects.all()
                    data = {
                        'MYCourse': s1,
                        'Designation' : Designation
                    }
                    return render(request, "Emp/HR/frmHRCourse.html", data)
                else:
                    s1 = tblEmpCourse.objects.filter(ContactNo=username)
                    Designation = tblEmpDetails.objects.all()
                    data = {
                        'MYCourse': s1,
                        'Designation' : Designation, 
                    }
                    return render(request, "Emp/TL/frmEmpCourse.html", data)

def StuList(request, course):    
    s1= tblStudentRegistration.objects.filter(Course=course)
    data = {
        'MYCourse': s1  
    }
    return render(request, 'Emp/HR/frmStuList.html', data)

def HREmpList(request, course):    
    s1= tblEmpDetails.objects.filter(Course=course)
    data = {
        'MYCourse': s1  
    }
    return render(request, 'Emp/HR/frmHREmpList.html', data)

def Empuploadmaterial(request, Course):
    course_obj = get_object_or_404(tblcourse, course=Course)   
    context = {
        'Course': course_obj
    }
    return render(request, 'Emp/TL/frmEmpuploadmaterial.html', context)

def QueryList(request, Course):
    s1 = tblEmpCourse.objects.all()
    queries = tblStuquery.objects.filter(subject=Course)
    data = {
        'Queries': queries,
        'MYcourse' : s1
    }
    return render(request, "Emp/TL/frmQueryList.html", data)

def QueryResponse(request, Id):
    employee_course = tblEmpDetails.objects.first().Course
    default_query = tblStuquery.objects.filter(Id=Id).first()
    context = {
        'default_query': default_query
    }
    return render(request, 'Emp/TL/frmQueryResponse.html', context)

def do_QueryResponse(request):
    if request.method == 'POST':
        query_id = request.POST.get('query')
        qr = get_object_or_404(tblStuquery, query=query_id)
        qr.queryans = request.POST.get('queryans')
        qr.isActive = request.POST.get('isActive')
        qr.isCompleted = request.POST.get('isCompleted')
        qr.save()
        return redirect('QueryResponse', Id=qr.Id)


        