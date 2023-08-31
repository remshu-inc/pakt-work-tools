from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import TblGroup, TblStudentGroup, TblUser, TblStudent, TblTeacher
from hashlib import sha512
import datetime

# custom_default_errors = {
#     'blank': 'Необходимо заполнить поле',
# }


class DateInput(forms.DateInput):
	input_type = 'date'


class UserCreationForm(forms.ModelForm):
	class Meta:
		model = TblUser
		fields = ('login', 'password', 'last_name', 'name', 'patronymic')

		widgets = {
			'login': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'autocomplete': 'off'}),

			'password': forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required', 'autocomplete': 'new-password'}),
			'last_name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
			'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'autocomplete': 'off'}),
			'patronymic': forms.TextInput(attrs={'class': 'form-control', 'required': 'required',  'autocomplete': 'off'}),
		}

		# TODO: Переписать ошибки под общие поля
		error_messages = {
			'login': {
				'required': 'Необходимо заполнить поле',
				'unique': 'Такой логин уже существует',
			},

			'password': {
				'required': 'Необходимо заполнить поле',
			},

			'last_name': {
				'required': 'Необходимо заполнить поле',
			},

			'name': {
				'required': 'Необходимо заполнить поле',
			},
		}

	def save(self, commit=True):
		user = super().save(commit=False)

		salt = 'DsaVfeqsJw00XvgZnFxlOFkqaURzLbyI'
		hash = sha512((user.password + salt).encode('utf-8'))
		hash = hash.hexdigest()
		user.password = hash

		if commit:
			user.save()

		return user


class StudentCreationForm(forms.ModelForm):
	class Meta:
		model = TblStudent
		fields = ('birthdate', 'gender', 'course_number')

		widgets = {
			'birthdate': DateInput(attrs={'class': 'form-control', 'required': 'required'}),
			'gender': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
			'course_number': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min':'1', 'max':'10'}),
		}

		# TODO: Переписать ошибки под общие поля
		error_messages = {
			'birthdate': {
				'required': 'Необходимо заполнить поле',
			},

			'course_number': {
				'required': 'Пожалуйста, выберите номер курса',
				'max_value': 'Некорректный номер курса',
				'min_value': 'Некорректный номер курса'
			},
		}

	# Чтобы после сохранения выдать id для сохранения в TblStudentGroup
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

		# TODO: Переписать ошибки под общие поля
		error_messages = {
			'group': {
				'required': 'Пожалуйста, выберите группу',
			},
		}

	def save(self, commit=True):
		student_group = super().save(commit=False)

		if commit:
			student_group.save()

		return student_group


class LoginForm(forms.Form):
	login = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}))
	password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control',  'placeholder': 'Пароль'}))

	def __init__(self, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)
		self.fields['login'].required = False
		self.fields['password'].required = False


def get_default_year():
	default = datetime.datetime.now()
	if 0 < default.month < 9:
		default = default.year - 1
	else:
		default = default.year    
	return default


# * Group creation form
class GroupCreationForm(forms.ModelForm):
	year = forms.IntegerField(widget=forms.NumberInput(attrs={'id':'year-input', 'class': 'form-control', 'min': '1900', 'max': '9999', 'value': get_default_year(), 'autocomplete':'off'}))

	class Meta:
		model = TblGroup
		fields = ('group_name', 'course_number')

		widgets = {
			'group_name': forms.TextInput(attrs={'class': 'form-control', 'max-length': '256', 'autocomplete':'off'}),
			'course_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10})
		}

		error_messages = {
			'group_name': {
				'required': 'Введите название группы',
			},
			
			'course_number': {
				'required': 'Выберите номер курса',
				'min_value': 'Некорректный номер курса',
				'max_value': 'Некорректный номер курса'
			},
		}

	def save(self, commit=True):
		group = super().save(commit=False)

		if commit:
			group.save()

		return group



class GroupModifyForm(forms.Form):
	fields = ['group_name', 'year', 'course_number']

	def __init__(self, year, group_name, course_number, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['year'] = forms.IntegerField(
			widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'year-input', 'min': 1900, 'max': 9999,  'value':int(year), 'autocomplete':'off'}),
			)

		self.fields['group_name'] = forms.CharField(
			widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete':'off'}),
			initial=group_name,
			max_length=256)
		self.fields['course_number'] = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}), initial=course_number)

class ChangePasswordForm(forms.Form):
	password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type':'password', 'autocomplete':'new-password', 'value':''}))
	
	def __init__(self, *args, **kwargs):
		super(ChangePasswordForm, self).__init__(*args, **kwargs)
		self.fields['password'].required = False
	