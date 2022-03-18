from django.contrib.auth import login, logout
from .login import MyBackend
# from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationForm, StudentCreationForm, LoginForm
from django.shortcuts import render, redirect

def signup(request):
    
    if request.method == 'POST':
        form_user = UserCreationForm(request.POST)
        form_student = StudentCreationForm(request.POST)
        if form_user.is_valid() and form_student.is_valid():
            user = form_user.save()
            student = form_student.save(commit=False)
            student.user_id = user.id_user
            student.save()
            
            
            username = form_user.cleaned_data.get('login')
            password = form_user.cleaned_data.get('password')
            
            user = MyBackend.authenticate(login=username, password=password)
            
            if user:
                login(request, user)
                
            return redirect('home')
            
    else:
        form_user = UserCreationForm()
        form_student = StudentCreationForm()
        
    return render(request, 'signup.html', {'form_user': form_user, 'form_student': form_student})

def log_in(request):
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["login"]
            password = form.cleaned_data["password"]

            user = MyBackend.authenticate(login=username, password=password)
            
            if user:
                login(request, user)
                return redirect('home')
            else:
                form_login = LoginForm()
    else:
        form_login = LoginForm()
        
    
    return render(request, 'login.html', {'form_login': form_login})

def log_out(request):
    
    logout(request)
    
    return redirect('home')