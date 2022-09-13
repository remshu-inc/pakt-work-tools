from django.contrib.auth import login, logout
from .login import MyBackend
# from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import TblUser, TblGroup
from .forms import UserCreationForm, StudentCreationForm, LoginForm,  GroupCreationForm

from string import punctuation
from datetime import datetime

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
        # print(form_login)
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

#* Teacher managment page
def manage(request):
    if  request.user.is_teacher:
        return(render(request, 'manage_page.html', {'teacher': True}))
    else:
        return(render(request, 'manage_page.html', {'teacher': False}))

#* Group creation page
def _symbol_check(name:str)->bool:
    """_summary_
    Checking the group name for adequacy

    Args:
        name (str): Name of group  

    Returns:
        bool: Decision of adequacy
    """    
    bad_symbols = punctuation+' \t\n'
    for symbol in name:
        if symbol not in bad_symbols:
            return(True)
    return(False)


def group_creation(request):
    if request.user.is_teacher:
        if request.method != 'POST':
            return(render(request, 'group_creation_form.html', 
            {
                'right':True,
                'form': GroupCreationForm(),
                'bad_name':False,
                'bad_year':False,
                'exist':False,
                'success':False,
            }))
        else:
            form = GroupCreationForm(request.POST or None)
            if form.is_valid():
                group_name = str(form.cleaned_data['group_name'])
                year = str(form.cleaned_data['year'])

                if _symbol_check(group_name):
                    if year.isnumeric() and 999 < int(year) < datetime.now().year+1:

                        enrollement_date = datetime(int(year), 9, 1)
                        valid_sample = TblGroup.objects.filter(Q(group_name = group_name)\
                             & Q(enrollement_date = enrollement_date)).values('id_group').all()
                        
                        if not valid_sample.exists():
                            new_row = TblGroup(group_name = group_name, enrollement_date = enrollement_date)
                            new_row.save()

                            return(render(request, 'group_creation_form.html', 
                                {
                                    'right':True,
                                    'form': GroupCreationForm(),
                                    'bad_name':False,
                                    'bad_year':False,
                                    'exist':False,
                                    'success':True,
                            }))
                        else:
                            return(render(request, 'group_creation_form.html', 
                                {
                                    'right':True,
                                    'form': GroupCreationForm(),
                                    'bad_name':False,
                                    'bad_year':False,
                                    'exist':True,
                                    'success':False,
                            }))
                    else:
                        return(render(request, 'group_creation_form.html', 
                            {
                                'right':True,
                                'form': GroupCreationForm(),
                                'bad_name':False,
                                'bad_year':True,
                                'exist':False,
                                'success':False,
                        }))
            else:
                return(render(request, 'group_creation_form.html', 
                    {
                        'right':True,
                        'form': GroupCreationForm(),
                        'bad_name':True,
                        'bad_year':False,
                        'exist':False,
                        'success':False,
                }))  
    else:
        return(render(request, 'group_creation_form.html', 
            {
                'right':False,
                'form': GroupCreationForm(),
                'bad_name':False,
                'bad_year':False,
                'exist':False,
                'success':False,
        }))