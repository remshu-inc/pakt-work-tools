from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import TblUser, TblStudent
from hashlib import sha512

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = TblUser
        fields = ('login', 'password', 'last_name', 'name', 'patronymic')
        
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
    # birthdate = forms.DateField(label='birthdate')
    
    class Meta:
        model = TblStudent
        fields = ('gender', 'group_number', 'course_number')

class LoginForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    
    # class Meta:
    #     # model = TblUser
    #     fields = ('login', 'password')


# class CustomUserChangeForm(UserChangeForm):

#     class Meta:
#         model = TblUser
#         fields = ('username', 'login')