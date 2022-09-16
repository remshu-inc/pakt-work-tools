from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import TblGroup, TblStudentGroup, TblUser, TblStudent
from hashlib import sha512
import datetime

class DateInput(forms.DateInput):
    input_type = 'date'

class UserCreationForm(forms.ModelForm):
    class Meta:
        model = TblUser
        fields = ('login', 'password', 'last_name', 'name', 'patronymic')
        
        widgets = {
            'login': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def save(self, commit=True):
        user = super().save(commit=False)
        
        salt = 'DsaVfeqsJw00XvgZnFxlOFkqaURzLbyI'
        hash = sha512((user.password+salt).encode('utf-8'))
        hash = hash.hexdigest()
        user.password = hash
        
        if commit:
            user.save()
            
        return user
    
        
class StudentCreationForm(forms.ModelForm):
    birthdate = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = TblStudent
        fields = ('birthdate', 'gender', 'course_number')
        
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            # 'group_number': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
            'course_number': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
        }  
        
        # Выдать список из существующих групп
        # self.fields['group_number'] = forms.ModelChoiceField(queryset=TblGroup.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
        
    def save(self, commit=True):
        student = super().save(commit=False)
        
        if commit:
            student.save()
            
        return student

class StudentGroupCreationForm(forms.ModelForm):
    class Meta:
        model = TblStudentGroup
        fields = ('group',)
        
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }
        
    def save(self, commit=True):
        student_group = super().save(commit=False)
        
        if commit:
            student_group.save()
            
        return student_group



class LoginForm(forms.Form):
    login = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


#* Group creation form

class GroupCreationForm(forms.Form):
    default = datetime.datetime.now()
    if 0 < default.month < 9:
        default = default.year - 1
    else:
        default = default.year

    group_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=256)
    year = forms.CharField(widget  = forms.TextInput(attrs={'class':'form-control'}), 
        initial = str(default),
        max_length=4)

class GroupModifyForm(forms.Form):
    fields = ['group_name', 'year']

    def __init__(self, year, group_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['year']  =   forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            initial = str(year),
            max_length=4)

        self.fields['group_name'] = forms.CharField(
            widget  = forms.TextInput(attrs={'class':'form-control'}), 
            initial = group_name,
            max_length =256)

class GroupModifyStudent(forms.Form):
    fields = ['studs']
    def __init__(self, students, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = []
        for student in students:
            options.append(
                (student['id'],
                student['id_str']+' '
                +str(student['last_name'])+' '
                +str(student['name'])+' '
                +str(student['patronymic'])+' ('
                +str(student['login'])+')')
                )
        self.fields['studs'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                        choices=options)

