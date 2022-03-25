from django.contrib.auth import login, logout
from .login import MyBackend
# from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationForm, StudentCreationForm, LoginForm
from django.shortcuts import render, redirect
from .models import TblUser

def signup(request):
    try:
        if not request.user.is_teacher:
            return redirect('home')
    except:
        return redirect('home')
    
    if request.method == 'POST':
        form_user = UserCreationForm(request.POST)
        form_student = StudentCreationForm(request.POST)
        
        if request.POST['login'] == '' and request.POST['password'] == '':
            form_user.add_error('login', 'Необходимо заполнить поле')
            form_user.add_error('password', 'Необходимо заполнить поле')
            return render(request, 'signup.html', {'form_user': form_user, 'form_student': form_student})
        elif request.POST['login'] == '':
            form_user.add_error('login', 'Необходимо заполнить поле')
            return render(request, 'signup.html', {'form_user': form_user, 'form_student': form_student})
        elif request.POST['password'] == '':
            form_user.add_error('password', 'Необходимо заполнить поле')
            return render(request, 'signup.html', {'form_user': form_user, 'form_student': form_student})
        
        if form_user.is_valid() and form_student.is_valid():            
            user = form_user.save()
            student = form_student.save(commit=False)

            student.user_id = user.id_user
            student.save()
                
            return redirect('corpus')
            
    else:
        form_user = UserCreationForm()
        form_student = StudentCreationForm()
        
    return render(request, 'signup.html', {'form_user': form_user, 'form_student': form_student})

def log_in(request):
    
    if request.user.is_authenticated:
        return redirect('corpus')
    
    if request.method == "POST":
        form_login = LoginForm(request.POST)
        print(form_login)
        if form_login.is_valid():
            username = form_login.cleaned_data["login"]
            password = form_login.cleaned_data["password"]

            user = MyBackend.authenticate(login=username, password=password)
            
            if user:
                login(request, user)
                return redirect('corpus')
    else:
        form_login = LoginForm()
        
    
    return render(request, 'login.html', {'form_login': form_login})

def log_out(request):
    
    logout(request)
    return redirect('home')