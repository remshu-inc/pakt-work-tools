from urllib import request
from django.contrib.auth import login, logout
from django.contrib.auth.models import AnonymousUser
import operator
from functools import reduce

from .login import MyBackend
# from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import TblTeacher, TblUser, TblStudent, TblGroup, TblStudentGroup, TblLanguage
from .forms import UserCreationForm, StudentCreationForm, LoginForm, GroupCreationForm, GroupModifyForm, StudentGroupCreationForm, ChangePasswordForm

from right_app.models import TblUserRights
from right_app.views import check_is_superuser

from text_app.models import TblText, TblMarkup, TblTextType

from string import punctuation
from datetime import datetime
from hashlib import sha512

# for dashboard
from django.http import JsonResponse
from django.db.models import Count, Value, IntegerField, F
import json
from text_app.models import TblTag, TblMarkup, TblGrade, TblEmotional
import numpy as np
import scipy
from . import dashboards

def signup(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)

	if request.method == 'POST':
		form_user = UserCreationForm(request.POST)
		form_student = StudentCreationForm(request.POST)
		form_student_group = StudentGroupCreationForm(request.POST)

		
		# Дописать валидацию для form_student_group.is_valid()
		if form_user.is_valid() and form_student.is_valid():
			# Save StudentGroup
			try:
				student_group = form_student_group.save(commit=False)
			except:
				return render(request, 'signup.html', {'form_user': form_user, 'form_student': form_student,
													   'form_student_group': form_student_group})

			# Save User
			user = form_user.save(commit=False)
			user.language_id = request.user.language_id
			user = user.save()

			# Save Student
			student = form_student.save(commit=False)
			student.user_id = user.id_user
			student = student.save()

			student_group.student_id = student.id_student
			student_group.save()

			return redirect('manage')

	else:
		form_user = UserCreationForm()
		form_student = StudentCreationForm()
		form_student_group = StudentGroupCreationForm()

	return render(request, 'signup.html',
				  {'form_user': form_user, 'form_student': form_student, 'form_student_group': form_student_group})


def change_password_self(request):
	if not (request.user.is_authenticated and (request.user.is_teacher() or request.user.is_student())):
		return render(request, 'access_denied.html', status=403)
		
	if request.POST:
		user_id = request.user.id_user
		password = str(request.POST['password'])
		password_form = ChangePasswordForm(request.POST)

		if password.strip() == '':
			password_form.add_error('password', 'Пожалуйста, введите пароль')
		
		if password_form.is_valid():
			salt = 'DsaVfeqsJw00XvgZnFxlOFkqaURzLbyI'
			hash = sha512((password + salt).encode('utf-8'))
			hash = hash.hexdigest()

			TblUser.objects.filter(id_user=user_id).update(password=hash)

			return redirect('manage')
	else:
		password_form = ChangePasswordForm()

	return render(request, 'change_password_self.html', {'password_form': password_form})


def change_password_student(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)

	if request.POST:
		user_id = request.POST['student']
		password = str(request.POST['password'])
		password_form = ChangePasswordForm(request.POST)

		if password.strip() == '':
			password_form.add_error('password', 'Пожалуйста, введите пароль')
		
		if password_form.is_valid():
			salt = 'DsaVfeqsJw00XvgZnFxlOFkqaURzLbyI'
			hash = sha512((password + salt).encode('utf-8'))
			hash = hash.hexdigest()

			TblUser.objects.filter(id_user=user_id).update(password=hash)

			return redirect('manage')
	else:
		password_form = ChangePasswordForm()

	students = []
	for student in TblStudent.objects.all():
		user = TblUser.objects.filter(id_user=student.user_id)
		if user.exists():
			user = user.first()
			students.append(
				{'id': user.id_user, 'name': (user.last_name + ' ' + user.name), 'login': user.login})

	return render(request, 'change_password_student.html', {'students': students, 'password_form': password_form})


def signup_teacher(request):
	if not (request.user.is_authenticated and request.user.is_teacher() and check_is_superuser(request.user.id_user)):
		return render(request, 'access_denied.html', status=403)

	if request.method == 'POST':
		form_user = UserCreationForm(request.POST)

		if form_user.is_valid():
			# Save User
			user = form_user.save()

			# Save Teacher
			teacher = TblTeacher(user_id=user.id_user)
			teacher.save()

			# Save Teacher's Right
			right_one = TblUserRights(user_id=user.id_user, right_id=1)
			right_one.save()
			right_two = TblUserRights(user_id=user.id_user, right_id=2)
			right_two.save()
			right_three = TblUserRights(user_id=user.id_user, right_id=3)
			right_three.save()
			right_four = TblUserRights(user_id=user.id_user, right_id=4)
			right_four.save()
			right_five = TblUserRights(user_id=user.id_user, right_id=5)
			right_five.save()

			return redirect('manage')

	else:
		form_user = UserCreationForm()

	return render(request, 'signup_teacher.html', {'form_user': form_user})


def log_in(request):
	# Проверка на авторизованность
	if request.user.is_authenticated:
		return redirect('home')

	if request.method == "POST":
		form_login = LoginForm(request.POST)

 		# Проверка заполнености полей
		if request.POST['login'] == '':
			form_login.add_error('login', 'Пожалуйста, введите логин')

		if request.POST['password'] == '':
			form_login.add_error('password', 'Пожалуйста, введите пароль')
	
		if form_login.is_valid():
			username = form_login.cleaned_data["login"]
			password = form_login.cleaned_data["password"]

			user = MyBackend.authenticate(login=username, password=password)

			# Если пользваотель существует
			if user:
				login(request, user)
				return redirect('home')

			# Иначе выдать ошибку
			else:
				form_login.add_error(None, 'Введен неверный логин или пароль')

	else:
		form_login = LoginForm()

	return render(request, 'login.html', {'form_login': form_login})


def log_out(request):
	logout(request)
	return redirect('home')


def manage(request):
	"""
	Teacher management page
	"""
	if isinstance(request.user, AnonymousUser):
		return redirect('login')

	teacher = request.user.is_teacher()
	student = request.user.is_student()

	if teacher:
		return render(request, 'manage_teacher.html', {'superuser': check_is_superuser(request.user.id_user)})

	if student:
		return render(request, 'manage_student.html')

	return redirect('home')


# * Group creation page
def _symbol_check(name: str) -> bool:
	"""_summary_
	Checking the group name for adequacy

	Args:
		name (str): Name of group  

	Returns:
		bool: Decision of adequacy
	"""
	bad_symbols = punctuation + ' \t\n'
	for symbol in name:
		if symbol not in bad_symbols:
			return True
	return False


def group_creation(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)

	if request.method == 'POST':
		form_group = GroupCreationForm(request.POST)
				
		if not _symbol_check(request.POST['group_name']):
				form_group.add_error('group_name', 'Ошибка в названии группы (должна присутствовать хотя бы одна буква или цифра)')

		year = request.POST['year']
		if not (year.isnumeric() and 999 < int(year) < datetime.now().year + 1):
			form_group.add_error('year', 'Неверно указан год')

		if form_group.is_valid():
			group_name = form_group.cleaned_data['group_name']
			enrollment_date = datetime(int(form_group.cleaned_data["year"]), 9, 1)
			if TblGroup.objects.filter(Q(group_name=group_name)
										& Q(enrollment_date=enrollment_date)).values('id_group').all().exists():
				form_group.add_error(None, 'Такая группа уже существует')
				return render(request, 'group_creation.html', {'form': form_group})

			group = form_group.save(commit=False)
			group.language_id = request.user.language_id
			group.enrollment_date = enrollment_date
			group = group.save()

			return render(request, 'group_creation.html', {'form': GroupCreationForm(), 'success': True})

	else:
		form_group = GroupCreationForm()

	return render(request, 'group_creation.html',
				  {'form': form_group})


# * Group selection page
def group_selection(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
	
	group_filter = request.GET.get('group-filter')
	group_filter = group_filter.strip() if group_filter else ''
		
	groups = TblGroup.objects.filter(Q(language_id=request.user.language_id) & Q(group_name__icontains=group_filter))\
		.order_by('-enrollment_date', 'course_number', 'group_name')\
		.values()
	
	for index in range(len(groups)):
		groups[index]['enrollment_date'] = str(groups[index]['enrollment_date'].year) \
			+ ' /  ' + str(groups[index]['enrollment_date'].year + 1)

	return (render(request, 'group_select.html', context={'groups' : groups, 'filter' : group_filter}))


# * Group modify
def _get_group_students(group_id: int, in_: bool) -> list:
	language_id = TblGroup.objects.filter(
		id_group=group_id).values('language_id')[0]['language_id']
	students_in_group = TblStudentGroup.objects.filter(
		Q(group_id=group_id) &
		Q(student_id__user_id__language_id=language_id)
	).values('student_id')
	if in_:
		query = Q(id_student__in=students_in_group)
	else:
		query = ~Q(id_student__in=students_in_group) & Q(
			user_id__language_id=language_id)

	students = TblStudent.objects.filter(query).values(
		'id_student',
		'user_id__login',
		'user_id__last_name',
		'user_id__name',
		'user_id__patronymic',
	).order_by('user_id__last_name')

	students_reform = []

	for student in students:
		students_reform.append({
			'id': student['id_student'],
			'id_str': str(student['id_student']),
			'login': student['user_id__login'],
			'last_name': student['user_id__last_name'],
			'name': student['user_id__name'],
			'patronymic': student['user_id__patronymic']
		})

	return (students_reform)


def group_modify(request, group_id):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
	
	groups = TblGroup.objects.filter(id_group=group_id).values(
			'enrollment_date', 'group_name', 'course_number')
	
	if not groups.exists():
		return (render(request, 'group_modify.html', context={
				'group_not_found': True
			}, status=404))
	
	year = groups[0]['enrollment_date'].year
	group_name = groups[0]['group_name']
	course_number = groups[0]['course_number']
	students_in = _get_group_students(group_id, True)
	students_out = _get_group_students(group_id, False)

	data_form = GroupModifyForm(year, group_name, course_number)

	if request.method == 'POST':
		if 'group_info_modify' in request.POST:
			data_form = GroupModifyForm(year, group_name, course_number, request.POST)

			group_name_new = str(request.POST['group_name']).strip()
			year_new = str(request.POST['year'])
			course_number_new = str(request.POST['course_number'])

			if not _symbol_check(group_name_new):
				data_form.add_error('group_name', 'Ошибка в названии группы (должна присутствовать хотя бы одна буква или цифра)')
			if not (year_new.isnumeric() and 1900 <= int(year_new) < datetime.now().year + 1):
				data_form.add_error('year', 'Неверно указан год ')
			if not (course_number_new.isnumeric() and 1 <= int(course_number_new) <= 10):
				data_form.add_error('course_number', 'Некорректный номер курса')

			if data_form.is_valid():
				enrollment_date = datetime(int(data_form.cleaned_data['year']), 9, 1)
				group_name = str(data_form.cleaned_data['group_name'])
				if TblGroup.objects.filter(Q(group_name=group_name_new)
										& Q(enrollment_date=enrollment_date)
										& ~Q(id_group=group_id)).values('id_group').all().exists():
					data_form.add_error(None, 'Такая группа уже существует')
				else:
					group = TblGroup.objects.get(id_group=group_id)
					group.group_name = group_name
					group.enrollment_date = enrollment_date
					group.course_number = int(data_form.cleaned_data['course_number'])
					group.save()

	# Render page
	context = {
		'group_id': group_id,
		'group_name': group_name,
		'group_students': students_in,
		'not_group_students': students_out,
		'data_form': data_form
	}

	return (render(request, 'group_modify.html', context=context))

def group_delete_student(request, group_id, student_id):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	query = TblStudentGroup.objects.filter(Q(group_id=group_id) & Q(student_id=student_id))

	if query.exists():
		query.delete()

	return group_modify(request, group_id)

def delete_group(request, group_id) :
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
	
	TblGroup.objects.filter(id_group=group_id).delete()
	return redirect('group_selection')


def group_add_student(request, group_id, student_id):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html')

	if TblStudent.objects.filter(Q(id_student=student_id)).exists() and (not TblStudentGroup.objects.filter(
						Q(group_id=group_id) &
						Q(student_id=student_id)).exists()):	
		TblStudentGroup.objects.create(student_id=student_id, group_id=group_id)

	return group_modify(request, group_id)


def task_list_select(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)

	students = []
	students_query = TblStudent.objects.filter(Q(user_id__language_id=request.user.language_id))
	
	student_filter = request.GET.get('student-filter')
	
	if student_filter != None and student_filter !='' and students_query.exists():
		search_args = []
		for term in student_filter.split():
			for query in ('user_id__last_name__icontains', 'user_id__name__icontains', 'user_id__login__icontains', 'user_id__patronymic__icontains'):
				search_args.append(Q(**{query: term}))
		students_query = students_query.filter(reduce(operator.or_, search_args))

	for student in students_query.values('id_student',
										'user_id__login',
										'user_id__last_name',
										'user_id__name',
										'user_id__patronymic',
										'user_id'):
		students.append({
			'id': student['id_student'],
			'user_id': student['user_id'],
			'login': student['user_id__login'],
			'last_name': student['user_id__last_name'],
			'name': student['user_id__name'],
			'patronymic': student['user_id__patronymic']
		})

	return render(request, 'task_list_select.html', context={'students': students, 'filter': student_filter})


def tasks_info(request, user_id):
	if not (request.user.is_authenticated and ((request.user.is_student() and request.user.id_user == user_id) or request.user.is_teacher())):
				return render(request, 'access_denied.html', status=403)
	
	about_student = TblStudent.objects\
		.filter(user_id=user_id)\
		.values('user_id__name', 'user_id__last_name', 'user_id__patronymic').all()
	

	author_data = {}
	if about_student.exists():
		about_student = about_student.first();
		author_data = {
			'name': about_student['user_id__name'] if about_student['user_id__name'] else '',
			'last_name': about_student['user_id__last_name'] if about_student['user_id__last_name'] else '',
			'patronymic': about_student['user_id__patronymic'] if about_student['user_id__patronymic'] else '',
		}

	title_filter = request.GET.get('title-filter')

	tasks = TblText.objects\
		.filter(user_id=user_id)\
		.order_by('-create_date')\
		.values(
			'id_text',
			'language_id__language_name',
			'text_type_id__text_type_name',
			'header',
			'create_date',
			'error_tag_check',
			'assessment',
		).all()
	
	task_list = []
	if tasks.exists():
		if title_filter != None and title_filter != '':
			tasks = tasks.filter(Q(header__icontains=title_filter))

		for task in tasks:
			error_check = 'Да' if task['error_tag_check'] else 'Нет'
			assessment = ''
			if task['assessment'] and task['assessment'] > 0:
				for element in TblText.TASK_RATES:
					if task['assessment'] == element[0]:
						assessment = element[1]
						break
			if assessment:
				num_of_errors = TblMarkup.objects.filter(
					Q(token_id__sentence_id__text_id=task['id_text']) &
					Q(tag_id__markup_type_id=1)
				).count()
			else:
				num_of_errors = ''

			path = {'lang': task['language_id__language_name'],
					'type': task['text_type_id__text_type_name'],
					'id': task['id_text']
					}

			task_list.append({
				'header': task['header'],
				'path': path,
				'error_check': error_check,
				'assessment': assessment,
				'err_count': num_of_errors,
				'date': task['create_date']
			})

	return (render(request, 'task_list.html', context={
		'author': author_data,
		'tasks': task_list,
		'filter': title_filter
	}))


def list_charts(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	return render(request, 'dashboards.html')


def chart_types_errors(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		levels = dashboards.get_levels()
		groups = list(TblGroup.objects.values('group_name', 'language').distinct().order_by('group_name'))
		courses = list(
			TblGroup.objects.values('course_number', 'language').filter(course_number__gt=0).distinct().order_by(
				'course_number'))
		texts = list(
			TblText.objects.values('header', 'language').filter(error_tag_check=1).distinct().order_by('header'))
		text_types = list(
			TblTextType.objects.values().filter(tbltext__error_tag_check=1).distinct().order_by('id_text_type'))
		
		data_count_errors = list(
			 TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
						  'tag__tag_text_russian', 'sentence__text_id').filter(
				 Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1)).annotate(
				 count_data=Count('tag__id_tag')))
		
		data_on_tokens = dashboards.get_data_on_tokens(data_count_errors, 'tag__id_tag', 'tag__tag_language', True,
							       False)
		data = dashboards.get_data_errors(data_on_tokens, 0, True)
		
		tag_parents, dict_children = dashboards.get_dict_children()
		
		return render(request, 'dashboard_error_types.html', {'right': True, 'languages': languages, 'levels': levels,
								      'groups': groups, 'courses': courses, 'texts': texts,
								      'text_types': text_types, 'data': data,
								      'tag_parents': tag_parents,
								      'dict_children': dict_children})
		
	else:
		list_filters = json.loads(request.body)
		flag_post = list_filters['flag_post']
		
		if flag_post == 'enrollment_date':
			enrollment_date = dashboards.get_enrollment_date(list_filters)
			return JsonResponse({'enrollment_date': enrollment_date}, status=200)
			
		if flag_post == 'choice_all':
			texts, text_types = dashboards.get_filters_for_choice_all(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_group':
			texts, text_types = dashboards.get_filters_for_choice_group(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_student':
			texts, text_types = dashboards.get_filters_for_choice_student(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_course':
			texts, text_types = dashboards.get_filters_for_choice_course(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_text':
			groups, courses, text_types = dashboards.get_filters_for_choice_text(list_filters)
			return JsonResponse({'groups': groups, 'courses': courses, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_text_type':
			groups, courses, texts = dashboards.get_filters_for_choice_text_type(list_filters)
			return JsonResponse({'groups': groups, 'courses': courses, 'texts': texts}, status=200)
			
		if flag_post == 'update_diagrams':
			group = list_filters['group']
			date = list_filters['enrollment_date']
			surname = list_filters['surname']
			name = list_filters['name']
			patronymic = list_filters['patronymic']
			course = list_filters['course']
			text = list_filters['text']
			text_type = list_filters['text_type']
			level = int(list_filters['level'])
			
			if surname and name and patronymic and text and text_type:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic) & Q(sentence__text_id__header=text) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and patronymic and text:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and patronymic and text_type:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and patronymic:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and text and text_type:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif surname and name and text:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and text_type:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name)).annotate(count_data=Count('tag__id_tag')))
				
			elif course and text_type and text:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif course and text:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif course and text_type:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif course:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif group and text and text_type:
				group_date = date[:4] + '-09-01'
				
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif group and text:
				group_date = date[:4] + '-09-01'
				
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif group and text_type:
				group_date = date[:4] + '-09-01'
				
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif group:
				group_date = date[:4] + '-09-01'
				
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif text_type and text:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__text_type=text_type) & Q(sentence__text_id__header=text)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif text_type:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif text:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			else:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1)).annotate(
						count_data=Count('tag__id_tag')))
				
			data_on_tokens = dashboards.get_data_on_tokens(data_count_errors, 'tag__id_tag', 'tag__tag_language', True,
								       False)
			data = dashboards.get_data_errors(data_on_tokens, level, True)
			
			return JsonResponse({'data_type_errors': data}, status=200)


def chart_grade_errors(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		groups = list(TblGroup.objects.values('group_name', 'language').distinct().order_by('group_name'))
		courses = list(
			TblGroup.objects.values('course_number', 'language').filter(course_number__gt=0).distinct().order_by(
				'course_number'))
		texts = list(
			TblText.objects.values('header', 'language').filter(error_tag_check=1).distinct().order_by('header'))
		text_types = list(
			TblTextType.objects.values().filter(tbltext__error_tag_check=1).distinct().order_by('id_text_type'))
		
		data_grade = list(TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
							   'sentence__text_id').filter(
			Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
				grade__id_grade__isnull=False)).annotate(count_data=Count('grade__id_grade')))
		
		data_grade = dashboards.get_data_on_tokens(data_grade, 'grade__id_grade', 'grade__grade_language', True, False)
		data_grade = dashboards.get_zero_count_grade_errors(data_grade)
		data_grade = sorted(data_grade, key=lambda d: d['count_data'], reverse=True)
		
		return render(request, 'dashboard_error_grade.html', {'right': True, 'languages': languages, 'groups': groups,
								      'courses': courses, 'texts': texts,
								      'text_types': text_types, 'data': data_grade})
	else:
		list_filters = json.loads(request.body)
		flag_post = list_filters['flag_post']
		
		if flag_post == 'enrollment_date':
			enrollment_date = dashboards.get_enrollment_date(list_filters)
			return JsonResponse({'enrollment_date': enrollment_date}, status=200)
			
		if flag_post == 'choice_all':
			texts, text_types = dashboards.get_filters_for_choice_all(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_group':
			texts, text_types = dashboards.get_filters_for_choice_group(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_student':
			texts, text_types = dashboards.get_filters_for_choice_student(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_course':
			texts, text_types = dashboards.get_filters_for_choice_course(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_text':
			groups, courses, text_types = dashboards.get_filters_for_choice_text(list_filters)
			return JsonResponse({'groups': groups, 'courses': courses, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_text_type':
			groups, courses, texts = dashboards.get_filters_for_choice_text_type(list_filters)
			return JsonResponse({'groups': groups, 'courses': courses, 'texts': texts}, status=200)
			
		if flag_post == 'update_diagrams':
			group = list_filters['group']
			date = list_filters['enrollment_date']
			surname = list_filters['surname']
			name = list_filters['name']
			patronymic = list_filters['patronymic']
			course = list_filters['course']
			text = list_filters['text']
			text_type = list_filters['text_type']
			
			if surname and name and patronymic and text and text_type:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic) & Q(sentence__text_id__header=text) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('grade__id_grade')))
				
			elif surname and name and patronymic and text:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('grade__id_grade')))
				
			elif surname and name and patronymic and text_type:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('grade__id_grade')))
				
			elif surname and name and patronymic:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic)).annotate(
						count_data=Count('grade__id_grade')))
				
			elif surname and name and text and text_type:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('grade__id_grade')))
				
			elif surname and name and text:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('grade__id_grade')))
				
			elif surname and name and text_type:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('grade__id_grade')))
				
			elif surname and name:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name)).annotate(count_data=Count('grade__id_grade')))
				
			elif course and text_type and text:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('grade__id_grade')))
				
			elif course and text:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('grade__id_grade')))
				
			elif course and text_type:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('grade__id_grade')))
				
			elif course:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course)).annotate(
						count_data=Count('grade__id_grade')))
				
			elif group and text and text_type:
				group_date = date[:4] + '-09-01'
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('grade__id_grade')))
				
			elif group and text:
				group_date = date[:4] + '-09-01'
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('grade__id_grade')))
				
			elif group and text_type:
				group_date = date[:4] + '-09-01'
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('grade__id_grade')))
				
			elif group:
				group_date = date[:4] + '-09-01'
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date)).annotate(
						count_data=Count('grade__id_grade')))
				
			elif text_type and text:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__text_type=text_type) & Q(sentence__text_id__header=text)).annotate(
						count_data=Count('grade__id_grade')))
				
			elif text_type:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('grade__id_grade')))
				
			elif text:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('grade__id_grade')))
				
			else:
				data_grade = list(
					TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language',
								 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1)).annotate(
						count_data=Count('grade__id_grade')))
				
			data_grade = dashboards.get_data_on_tokens(data_grade, 'grade__id_grade', 'grade__grade_language', True,
								   False)
			data_grade = dashboards.get_zero_count_grade_errors(data_grade)
			data_grade = sorted(data_grade, key=lambda d: d['count_data'], reverse=True)
			
			return JsonResponse({'data_grade_errors': data_grade}, status=200)


def chart_types_grade_errors(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		levels = dashboards.get_levels()
		groups = list(TblGroup.objects.values('group_name', 'language').distinct().order_by('group_name'))
		courses = list(
			TblGroup.objects.values('course_number', 'language').filter(course_number__gt=0).distinct().order_by(
				'course_number'))
		texts = list(
			TblText.objects.values('header', 'language').filter(error_tag_check=1).distinct().order_by('header'))
		text_types = list(
			TblTextType.objects.values().filter(tbltext__error_tag_check=1).distinct().order_by('id_text_type'))
		grades = list(TblGrade.objects.values('id_grade', 'grade_name', 'grade_language').order_by('grade_language'))
		
		data_on_tokens = []
		texts_id = {}
		count_grades_for_language = {}
		for grade in grades:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
							 'tag__tag_text_russian', 'sentence__text_id').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
						grade=grade["id_grade"])).annotate(count_data=Count('tag__id_tag')))
			
			texts_id = dashboards.get_texts_id_keys(data_count_errors, texts_id, 'tag__tag_language')
			data_count_on_tokens, texts_id = dashboards.get_texts_id_and_data_on_tokens(data_count_errors, texts_id,
												    'tag__id_tag',
												    'tag__tag_language')
			data_on_tokens.append(data_count_on_tokens)
			
			if grade['grade_language'] not in count_grades_for_language.keys():
				count_grades_for_language[grade['grade_language']] = 1
			else:
				count_grades_for_language[grade['grade_language']] += 1
		
		data = []
		for i in range(len(data_on_tokens)):
			data_count = dashboards.get_on_tokens(texts_id, data_on_tokens[i], 'tag__tag_language')
			data.append(dashboards.get_data_errors(data_count, 0, False))
			
		for i in range(len(data[0])):
			offset = 0
			for language in count_grades_for_language.keys():
				sum_count = 0
				for j in range(count_grades_for_language[language]):
					sum_count += data[offset + j][i]['count_data']
					
				for j in range(count_grades_for_language[language]):
					data[offset + j][i]['sum_count'] = sum_count
					
				offset += count_grades_for_language[language]
				
		for i in range(len(data)):
			data[i] = sorted(data[i], key=lambda d: d['sum_count'], reverse=True)
			
		tag_parents, dict_children = dashboards.get_dict_children()
		
		return render(request, 'dashboard_error_types_grade.html', {'right': True, 'languages': languages,
									    'levels': levels, 'groups': groups,
									    'courses': courses, 'texts': texts,
									    'text_types': text_types, 'data': data,
									    'grades': grades, 'tag_parents': tag_parents,
									    'dict_children': dict_children,
									    'count_grades_for_language':
									    	count_grades_for_language})
	else:
		list_filters = json.loads(request.body)
		flag_post = list_filters['flag_post']
		
		if flag_post == 'enrollment_date':
			enrollment_date = dashboards.get_enrollment_date(list_filters)
			return JsonResponse({'enrollment_date': enrollment_date}, status=200)
			
		if flag_post == 'choice_all':
			texts, text_types = dashboards.get_filters_for_choice_all(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_group':
			texts, text_types = dashboards.get_filters_for_choice_group(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_student':
			texts, text_types = dashboards.get_filters_for_choice_student(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_course':
			texts, text_types = dashboards.get_filters_for_choice_course(list_filters)
			return JsonResponse({'texts': texts, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_text':
			groups, courses, text_types = dashboards.get_filters_for_choice_text(list_filters)
			return JsonResponse({'groups': groups, 'courses': courses, 'text_types': text_types}, status=200)
			
		if flag_post == 'choice_text_type':
			groups, courses, texts = dashboards.get_filters_for_choice_text_type(list_filters)
			return JsonResponse({'groups': groups, 'courses': courses, 'texts': texts}, status=200)
			
		if flag_post == 'update_diagrams':
			group = list_filters['group']
			date = list_filters['enrollment_date']
			surname = list_filters['surname']
			name = list_filters['name']
			patronymic = list_filters['patronymic']
			course = list_filters['course']
			text = list_filters['text']
			text_type = list_filters['text_type']
			level = int(list_filters['level'])
			
			grades = list(
				TblGrade.objects.values('id_grade', 'grade_name', 'grade_language').order_by('grade_language'))
			
			data_on_tokens = []
			texts_id = {}
			count_grades_for_language = {}
			for grade in grades:
				if surname and name and patronymic and text and text_type:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__user__last_name=surname) & Q(
								sentence__text_id__user__name=name) & Q(
								sentence__text_id__user__patronymic=patronymic) & Q(sentence__text_id__header=text) & Q(
								sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
					
				elif surname and name and patronymic and text:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__user__last_name=surname) & Q(
								sentence__text_id__user__name=name) & Q(
								sentence__text_id__user__patronymic=patronymic) & Q(
								sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
					
				elif surname and name and patronymic and text_type:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__user__last_name=surname) & Q(
								sentence__text_id__user__name=name) & Q(
								sentence__text_id__user__patronymic=patronymic) & Q(
								sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
					
				elif surname and name and patronymic:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__user__last_name=surname) & Q(
								sentence__text_id__user__name=name) & Q(
								sentence__text_id__user__patronymic=patronymic)).annotate(
							count_data=Count('tag__id_tag')))
					
				elif surname and name and text and text_type:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__user__last_name=surname) & Q(
								sentence__text_id__user__name=name) & Q(sentence__text_id__header=text) & Q(
								sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
					
				elif surname and name and text:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__user__last_name=surname) & Q(
								sentence__text_id__user__name=name) & Q(sentence__text_id__header=text)).annotate(
							count_data=Count('tag__id_tag')))
					
				elif surname and name and text_type:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__user__last_name=surname) & Q(
								sentence__text_id__user__name=name) & Q(
								sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
					
				elif surname and name:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__user__last_name=surname) & Q(
								sentence__text_id__user__name=name)).annotate(count_data=Count('tag__id_tag')))
					
				elif course and text_type and text:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(
								sentence__text_id__tbltextgroup__group__course_number=course) & Q(
								sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
							count_data=Count('tag__id_tag')))
					
				elif course and text:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(
								sentence__text_id__tbltextgroup__group__course_number=course) & Q(
								sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
					
				elif course and text_type:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(
								sentence__text_id__tbltextgroup__group__course_number=course) & Q(
								sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
					
				elif course:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(
								sentence__text_id__tbltextgroup__group__course_number=course)).annotate(
							count_data=Count('tag__id_tag')))
					
				elif group and text and text_type:
					group_date = date[:4] + '-09-01'
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(
								sentence__text_id__tbltextgroup__group__group_name=group) & Q(
								sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
								sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
							count_data=Count('tag__id_tag')))
					
				elif group and text:
					group_date = date[:4] + '-09-01'
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(
								sentence__text_id__tbltextgroup__group__group_name=group) & Q(
								sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
								sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
					
				elif group and text_type:
					group_date = date[:4] + '-09-01'
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(
								sentence__text_id__tbltextgroup__group__group_name=group) & Q(
								sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
								sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
					
				elif group:
					group_date = date[:4] + '-09-01'
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(
								sentence__text_id__tbltextgroup__group__group_name=group) & Q(
								sentence__text_id__tbltextgroup__group__enrollment_date=group_date)).annotate(
							count_data=Count('tag__id_tag')))
					
				elif text_type and text:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__text_type=text_type) & Q(
								sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
					
				elif text_type:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__text_type=text_type)).annotate(
							count_data=Count('tag__id_tag')))
					
				elif text:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"]) & Q(sentence__text_id__header=text)).annotate(
							count_data=Count('tag__id_tag')))
					
				else:
					data_count_errors = list(
						TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
									 'tag__tag_text_russian', 'sentence__text_id').filter(
							Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
								grade=grade["id_grade"])).annotate(count_data=Count('tag__id_tag')))
					
				texts_id = dashboards.get_texts_id_keys(data_count_errors, texts_id, 'tag__tag_language')
				data_count_on_tokens, texts_id = dashboards.get_texts_id_and_data_on_tokens(data_count_errors, texts_id,
													    'tag__id_tag',
													    'tag__tag_language')
				data_on_tokens.append(data_count_on_tokens)
				
				if grade['grade_language'] not in count_grades_for_language.keys():
					count_grades_for_language[grade['grade_language']] = 1
				else:
					count_grades_for_language[grade['grade_language']] += 1
			data = []
			for i in range(len(data_on_tokens)):
				data_count = dashboards.get_on_tokens(texts_id, data_on_tokens[i], 'tag__tag_language')
				data.append(dashboards.get_data_errors(data_count, level, False))
				
			for i in range(len(data[0])):
				offset = 0
				for language in count_grades_for_language.keys():
					sum_count = 0
					for j in range(count_grades_for_language[language]):
						sum_count += data[offset + j][i]['count_data']
						
					for j in range(count_grades_for_language[language]):
						data[offset + j][i]['sum_count'] = sum_count
						
					offset += count_grades_for_language[language]
					
			for i in range(len(data)):
				data[i] = sorted(data[i], key=lambda d: d['sum_count'], reverse=True)
				
			return JsonResponse({'data': data}, status=200)


def chart_student_dynamics(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		tags = list(TblTag.objects.values('id_tag', 'tag_language', 'tag_text', 'tag_text_russian').filter(
			markup_type=1).order_by('id_tag'))
		
		return render(request, 'dashboard_student_dynamics.html', {'right': True, 'languages': languages, 'tags': tags})
	else:
		list_filters = json.loads(request.body)
		text_type = list_filters['text_type']
		surname = list_filters['surname']
		name = list_filters['name']
		patronymic = list_filters['patronymic']
		tag = list_filters['tag']
		checked_tag_children = list_filters['checked_tag_children']
		
		tags = [tag]
		if checked_tag_children:
			tags = dashboards.get_tag_children(tag)
			
		list_text_id_with_markup = []
		if surname and name and patronymic and tag and text_type:
			data_count_errors = list(TblMarkup.objects.values('tag__tag_language', 'sentence__text_id__create_date',
									  'sentence__text_id').filter(
				Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
					sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
					sentence__text_id__user__patronymic=patronymic) & Q(tag__id_tag__in=tags) & Q(
					sentence__text_id__text_type=text_type)).annotate(
				count_data=Count('sentence__text_id__create_date')))
			
			for data in data_count_errors:
				list_text_id_with_markup.append(data["sentence__text_id"])
				
			texts_without_markup = list(TblText.objects.annotate(tag__tag_language=F('language'),
									     sentence__text_id__create_date=F('create_date'),
									     sentence__text_id=F('id_text')).values(
				'tag__tag_language', 'sentence__text_id__create_date', 'sentence__text_id').filter(
				Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(
					user__patronymic=patronymic) & Q(text_type=text_type) & ~Q(
					id_text__in=list_text_id_with_markup)).annotate(count_data=Value(0, output_field=IntegerField())))
			
		elif surname and name and patronymic and tag:
			data_count_errors = list(TblMarkup.objects.values('tag__tag_language', 'sentence__text_id__create_date',
									  'sentence__text_id').filter(
				Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
					sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
					sentence__text_id__user__patronymic=patronymic) & Q(tag__id_tag__in=tags)).annotate(
				count_data=Count('sentence__text_id__create_date')))
			
			for data in data_count_errors:
				list_text_id_with_markup.append(data["sentence__text_id"])
				
			texts_without_markup = list(TblText.objects.annotate(tag__tag_language=F('language'),
									     sentence__text_id__create_date=F('create_date'),
									     sentence__text_id=F('id_text')).values(
				'tag__tag_language', 'sentence__text_id__create_date', 'sentence__text_id').filter(
				Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(
					user__patronymic=patronymic) & ~Q(id_text__in=list_text_id_with_markup)).annotate(
				count_data=Value(0, output_field=IntegerField())))
			
		elif surname and name and tag and text_type:
			data_count_errors = list(TblMarkup.objects.values('tag__tag_language', 'sentence__text_id__create_date',
									  'sentence__text_id').filter(
				Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
					sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
					tag__id_tag__in=tags) & Q(sentence__text_id__text_type=text_type)).annotate(
				count_data=Count('sentence__text_id__create_date')))
			
			for data in data_count_errors:
				list_text_id_with_markup.append(data["sentence__text_id"])
				
			texts_without_markup = list(TblText.objects.annotate(tag__tag_language=F('language'),
									     sentence__text_id__create_date=F('create_date'),
									     sentence__text_id=F('id_text')).values(
				'tag__tag_language', 'sentence__text_id__create_date', 'sentence__text_id').filter(
				Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(text_type=text_type) & ~Q(
					id_text__in=list_text_id_with_markup)).annotate(count_data=Value(0, output_field=IntegerField())))
			
		elif surname and name and tag:
			data_count_errors = list(TblMarkup.objects.values('tag__tag_language', 'sentence__text_id__create_date',
									  'sentence__text_id').filter(
				Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
					sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
					tag__id_tag__in=tags)).annotate(count_data=Count('sentence__text_id__create_date')))
			
			for data in data_count_errors:
				list_text_id_with_markup.append(data["sentence__text_id"])
				
			texts_without_markup = list(TblText.objects.annotate(tag__tag_language=F('language'),
									     sentence__text_id__create_date=F('create_date'),
									     sentence__text_id=F('id_text')).values(
				'tag__tag_language', 'sentence__text_id__create_date', 'sentence__text_id').filter(
				Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & ~Q(
					id_text__in=list_text_id_with_markup)).annotate(count_data=Value(0, output_field=IntegerField())))
			
		data_count_errors.extend(texts_without_markup)
		data_count_errors = dashboards.get_data_on_tokens(data_count_errors, '', 'tag__tag_language', False, False)
		
		texts_with_create_date = []
		for data in data_count_errors:
			if data['sentence__text_id__create_date'] is None:
				texts_with_create_date.append(data)
				
		for text in texts_with_create_date:
			data_count_errors.remove(text)
			
		data_count_errors = sorted(data_count_errors, key=lambda d: d['sentence__text_id__create_date'])
		
		if patronymic:
			text_types = list(TblTextType.objects.values().filter(Q(tbltext__error_tag_check=1) & Q(
				tbltext__user__last_name=surname) & Q(tbltext__user__name=name) & Q(
				tbltext__user__patronymic=patronymic) & Q(
				tbltext__tblsentence__tblmarkup__tag__in=tags)).distinct().order_by('id_text_type'))
		else:
			text_types = list(TblTextType.objects.values().filter(Q(tbltext__error_tag_check=1) & Q(
				tbltext__user__last_name=surname) & Q(tbltext__user__name=name) & Q(
				tbltext__tblsentence__tblmarkup__tag__in=tags)).distinct().order_by('id_text_type'))
			
		return JsonResponse({'data': data_count_errors, 'text_types': text_types}, status=200)


def chart_groups_errors(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		tags = list(TblTag.objects.values('id_tag', 'tag_language', 'tag_text', 'tag_text_russian').filter(
			markup_type=1).order_by('id_tag'))
		groups = list(TblGroup.objects.values('group_name', 'enrollment_date', 'language').distinct().order_by(
			'-enrollment_date'))
		
		for group in groups:
			group['enrollment_date'] = str(group['enrollment_date'].year) + ' \ ' \
							+ str(group['enrollment_date'].year + 1)
			
		return render(request, 'dashboard_error_groups.html', {'right': True, 'languages': languages, 'tags': tags,
								       'groups': groups})
	else:
		list_filters = json.loads(request.body)
		text = list_filters['text']
		text_type = list_filters['text_type']
		group = list_filters['group']
		tag = list_filters['tag']
		checked_tag_children = list_filters['checked_tag_children']
		
		tags = [tag]
		if checked_tag_children:
			tags = dashboards.get_tag_children(tag)
			
		group_number = []
		group_date = []
		for group in group:
			idx = group.find("(")
			number = int(group[:idx])
			group_number.append(number)
			
			year = group[idx + 2:idx + 6]
			date = year + '-09-01'
			group_date.append(date)
			
		data = []
		texts = []
		text_types = []
		
		for i in range(len(group_number)):
			if group and text and tag and text_type:
				d = list(TblMarkup.objects.annotate(id_group=F('sentence__text_id__tbltextgroup__group__id_group'),
								    number=F('sentence__text_id__tbltextgroup__group__group_name'),
								    date=F(
									    'sentence__text_id__tbltextgroup__group__enrollment_date')).values(
					'tag__tag_language', 'id_group', 'number', 'date', 'sentence__text_id').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(number=group_number[i]) & Q(
						date=group_date[i]) & Q(tag__id_tag__in=tags) & Q(sentence__text_id__header=text) & Q(
						sentence__text_id__text_type=text_type)).annotate(count_data=Count('id_group')))
				
			elif group and tag and text:
				d = list(TblMarkup.objects.annotate(id_group=F('sentence__text_id__tbltextgroup__group__id_group'),
								    number=F('sentence__text_id__tbltextgroup__group__group_name'),
								    date=F(
									    'sentence__text_id__tbltextgroup__group__enrollment_date')).values(
					'tag__tag_language', 'id_group', 'number', 'date', 'sentence__text_id').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(number=group_number[i]) & Q(
						date=group_date[i]) & Q(tag__id_tag__in=tags) & Q(sentence__text_id__header=text)).annotate(
					count_data=Count('id_group')))
				
			elif group and tag and text_type:
				d = list(TblMarkup.objects.annotate(id_group=F('sentence__text_id__tbltextgroup__group__id_group'),
								    number=F('sentence__text_id__tbltextgroup__group__group_name'),
								    date=F(
									    'sentence__text_id__tbltextgroup__group__enrollment_date')).values(
					'tag__tag_language', 'id_group', 'number', 'date', 'sentence__text_id').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(number=group_number[i]) & Q(
						date=group_date[i]) & Q(tag__id_tag__in=tags) & Q(
						sentence__text_id__text_type=text_type)).annotate(count_data=Count('id_group')))
				
			elif group and tag:
				d = list(TblMarkup.objects.annotate(id_group=F('sentence__text_id__tbltextgroup__group__id_group'),
								    number=F('sentence__text_id__tbltextgroup__group__group_name'),
								    date=F(
									    'sentence__text_id__tbltextgroup__group__enrollment_date')).values(
					'tag__tag_language', 'id_group', 'number', 'date', 'sentence__text_id').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(number=group_number[i]) & Q(
						date=group_date[i]) & Q(tag__id_tag__in=tags)).annotate(count_data=Count('id_group')))
				
			if d != []:
				d = dashboards.get_data_on_tokens(d, '', 'tag__tag_language', False, True)
			else:
				d = list(TblGroup.objects.annotate(tag__tag_language=F('language'), number=F('group_name'),
								   date=F('enrollment_date')).values('tag__tag_language',
												     'id_group', 'number',
												     'date').filter(
					Q(number=group_number[i]) & Q(date=group_date[i])))
				
				d[0]['count_data'] = 0
				d[0]['count_data_on_tokens'] = 0
				
			data.append(d)
			
			if text:
				text_types_for_group = list(TblTextType.objects.values().filter(Q(tbltext__error_tag_check=1) & Q(
					tbltext__tbltextgroup__group__group_name=group_number[i]) & Q(
					tbltext__tbltextgroup__group__enrollment_date=group_date[i]) & Q(
					tbltext__tblsentence__tblmarkup__tag__in=tags) & Q(tbltext__header=text)).distinct().order_by(
					'id_text_type'))
			else:
				text_types_for_group = list(TblTextType.objects.values().filter(Q(tbltext__error_tag_check=1) & Q(
					tbltext__tbltextgroup__group__group_name=group_number[i]) & Q(
					tbltext__tbltextgroup__group__enrollment_date=group_date[i]) & Q(
					tbltext__tblsentence__tblmarkup__tag__in=tags)).distinct().order_by('id_text_type'))
				
			for type_text in text_types_for_group:
				if type_text not in text_types:
					text_types.append(type_text)
					
			if text_type:
				texts_for_group = list(TblText.objects.values('header', 'language').filter(
					Q(error_tag_check=1) & Q(tbltextgroup__group__group_name=group_number[i]) & Q(
						tbltextgroup__group__enrollment_date=group_date[i]) & Q(text_type=text_type) & Q(
						tblsentence__tblmarkup__tag__in=tags)).distinct().order_by('header'))
			else:
				texts_for_group = list(TblText.objects.values('header', 'language').filter(
					Q(error_tag_check=1) & Q(tbltextgroup__group__group_name=group_number[i]) & Q(
						tbltextgroup__group__enrollment_date=group_date[i]) & Q(
						tblsentence__tblmarkup__tag__in=tags)).distinct().order_by('header'))
				
			for text_for_group in texts_for_group:
				if text_for_group not in texts:
					texts.append(text_for_group)
					
		data_all = []
		for i in range(len(data)):
			for data_item in data[i]:
				data_item['date'] = str(data_item['date'].year) + ' \ ' \
							+ str(data_item['date'].year + 1)
				data_all.append(data_item)
				
		data_all = sorted(data_all, key=lambda d: d['count_data'], reverse=True)
		
		return JsonResponse({'data': data_all, 'texts': texts, 'text_types': text_types}, status=200)


def chart_emotions_errors(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		levels = dashboards.get_levels()
		emotions = list(TblEmotional.objects.values())
		tag_parents, dict_children = dashboards.get_dict_children()
		
		return render(request, 'dashboard_error_emotions.html', {'right': True, 'languages': languages,
									 'levels': levels, 'emotions': emotions,
									 'tag_parents': tag_parents,
									 'dict_children': dict_children})
	else:
		list_filters = json.loads(request.body)
		flag_post = list_filters['flag_post']
		
		if flag_post == 'enrollment_date':
			enrollment_date = dashboards.get_enrollment_date(list_filters)
			return JsonResponse({'enrollment_date': enrollment_date}, status=200)
			
		if flag_post == 'update_diagrams':
			group = list_filters['group']
			date = list_filters['enrollment_date']
			surname = list_filters['surname']
			name = list_filters['name']
			patronymic = list_filters['patronymic']
			course = list_filters['course']
			text = list_filters['text']
			text_type = list_filters['text_type']
			emotion = list_filters['emotion']
			level = int(list_filters['level'])
			
			data_count_errors = []
			if surname and name and patronymic and text and text_type and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name) & Q(sentence__text_id__user__patronymic=patronymic) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif surname and name and patronymic and text and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name) & Q(sentence__text_id__user__patronymic=patronymic) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and patronymic and text_type and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name) & Q(sentence__text_id__user__patronymic=patronymic) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and patronymic and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and text and text_type and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name) & Q(sentence__text_id__header=text) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and text and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name) & Q(sentence__text_id__header=text)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif surname and name and text_type and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif surname and name and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name)).annotate(count_data=Count('tag__id_tag')))
				
			elif course and text_type and text and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif course and text and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif course and text_type and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif course and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif group and text and text_type and emotion:
				group_date = date[:4] + '-09-01'
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif group and text and emotion:
				group_date = date[:4] + '-09-01'
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif group and text_type and emotion:
				group_date = date[:4] + '-09-01'
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif group and emotion:
				group_date = date[:4] + '-09-01'
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif text_type and text and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__header=text) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif text_type and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif text and emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion) & Q(sentence__text_id__header=text)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif emotion:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__emotional=emotion)).annotate(count_data=Count('tag__id_tag')))
				
			data_count_on_tokens = dashboards.get_data_on_tokens(data_count_errors, 'tag__id_tag', 'tag__tag_language',
									     True, False)
			data_errors = dashboards.get_data_errors(data_count_on_tokens, level, True)
			
			groups, courses, texts = dashboards.get_filters_for_choice_text_type(list_filters)
			_, _, text_types = dashboards.get_filters_for_choice_text(list_filters)
			
			return JsonResponse({'data': data_errors, 'groups': groups, 'courses': courses, 'texts': texts,
					     'text_types': text_types}, status=200)


def chart_self_rating_errors(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		levels = dashboards.get_levels()
		self_ratings = list(TblText.objects.values('self_rating').filter(
			Q(self_rating__gt=0) & Q(error_tag_check=1)).distinct().order_by('self_rating'))
		tag_parents, dict_children = dashboards.get_dict_children()
		
		self_rating_text = TblText.TASK_RATES
		
		for self_rating in self_ratings:
			idx = self_rating["self_rating"]
			self_rating["self_rating_text"] = self_rating_text[idx - 1][1]
			
		return render(request, 'dashboard_error_self_rating.html', {'right': True, 'languages': languages,
									    'levels': levels, 'tag_parents': tag_parents,
									    'self_ratings': self_ratings,
									    'dict_children': dict_children})
	else:
		list_filters = json.loads(request.body)
		flag_post = list_filters['flag_post']
		
		if flag_post == 'enrollment_date':
			enrollment_date = dashboards.get_enrollment_date(list_filters)
			return JsonResponse({'enrollment_date': enrollment_date}, status=200)
			
		if flag_post == 'update_diagrams':
			group = list_filters['group']
			date = list_filters['enrollment_date']
			surname = list_filters['surname']
			name = list_filters['name']
			patronymic = list_filters['patronymic']
			course = list_filters['course']
			text = list_filters['text']
			text_type = list_filters['text_type']
			self_rating = list_filters['self_rating']
			level = int(list_filters['level'])
			
			data_count_errors = []
			if surname and name and patronymic and text and text_type and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic) & Q(sentence__text_id__header=text) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and patronymic and text and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and patronymic and text_type and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and patronymic and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__user__patronymic=patronymic)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and text and text_type and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif surname and name and text and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and text_type and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__user__last_name=surname) & Q(sentence__text_id__user__name=name) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif surname and name and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__user__last_name=surname) & Q(
							sentence__text_id__user__name=name)).annotate(count_data=Count('tag__id_tag')))
				
			elif course and text_type and text and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif course and text and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif course and text_type and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif course and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__tbltextgroup__group__course_number=course)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif group and text and text_type and self_rating:
				group_date = date[:4] + '-09-01'
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_type)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif group and text and self_rating:
				group_date = date[:4] + '-09-01'
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))
				
			elif group and text_type and self_rating:
				group_date = date[:4] + '-09-01'
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif group and self_rating:
				group_date = date[:4] + '-09-01'
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__tbltextgroup__group__group_name=group) & Q(
							sentence__text_id__tbltextgroup__group__enrollment_date=group_date)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif text_type and text and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(sentence__text_id__header=text) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif text_type and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(
							sentence__text_id__text_type=text_type)).annotate(count_data=Count('tag__id_tag')))
				
			elif text and self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating) & Q(sentence__text_id__header=text)).annotate(
						count_data=Count('tag__id_tag')))
				
			elif self_rating:
				data_count_errors = list(
					TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
								 'tag__tag_text_russian', 'sentence__text_id').filter(
						Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
							sentence__text_id__self_rating=self_rating)).annotate(count_data=Count('tag__id_tag')))
				
			data_count_on_tokens = dashboards.get_data_on_tokens(data_count_errors, 'tag__id_tag', 'tag__tag_language',
									     True, False)
			data_errors = dashboards.get_data_errors(data_count_on_tokens, level, True)
			
			groups, courses, texts = dashboards.get_filters_for_choice_text_type(list_filters)
			_, _, text_types = dashboards.get_filters_for_choice_text(list_filters)
			
			return JsonResponse({'data': data_errors, 'groups': groups, 'courses': courses, 'texts': texts,
					     'text_types': text_types}, status=200)


def chart_relation_assessment_self_rating(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		
		return render(request, 'dashboard_assessment_self_rating.html', {'right': True, 'languages': languages})
	else:
		list_filters = json.loads(request.body)
		surname = list_filters['surname']
		name = list_filters['name']
		patronymic = list_filters['patronymic']
		text_type = list_filters['text_type']
		
		if surname and name and patronymic and text_type:
			data_relation = list(TblText.objects.values('language', 'assessment', 'self_rating').filter(
				Q(self_rating__gt=0) & Q(assessment__gt=0) & Q(user__last_name=surname) & Q(user__name=name) & Q(
					user__patronymic=patronymic) & Q(text_type=text_type) & Q(error_tag_check=1)).distinct())
			
		elif surname and name and patronymic:
			data_relation = list(TblText.objects.values('language', 'assessment', 'self_rating').filter(
				Q(self_rating__gt=0) & Q(assessment__gt=0) & Q(user__last_name=surname) & Q(user__name=name) & Q(
					user__patronymic=patronymic) & Q(error_tag_check=1)).distinct())
			
		elif surname and name and text_type:
			data_relation = list(TblText.objects.values('language', 'assessment', 'self_rating').filter(
				Q(self_rating__gt=0) & Q(assessment__gt=0) & Q(user__last_name=surname) & Q(user__name=name) & Q(
					text_type=text_type) & Q(error_tag_check=1)).distinct())
			
		else:
			data_relation = list(TblText.objects.values('language', 'assessment', 'self_rating').filter(
				Q(self_rating__gt=0) & Q(assessment__gt=0) & Q(user__last_name=surname) & Q(user__name=name) & Q(
					error_tag_check=1)).distinct())
			
		assessment_types = TblText.TASK_RATES
		
		for data in data_relation:
			idx = data["self_rating"]
			data["self_rating_text"] = assessment_types[idx - 1][1]
			
			idx = data["assessment"]
			data["assessment_text"] = assessment_types[idx - 1][1]
			
		if patronymic:
			text_types = list(TblTextType.objects.values().filter(
				Q(tbltext__self_rating__gt=0) & Q(tbltext__assessment__gt=0) & Q(tbltext__user__last_name=surname) & Q(
					tbltext__user__name=name) & Q(tbltext__user__patronymic=patronymic) & Q(
					tbltext__error_tag_check=1)).distinct().order_by('id_text_type'))
		else:
			text_types = list(TblTextType.objects.values().filter(
				Q(tbltext__self_rating__gt=0) & Q(tbltext__assessment__gt=0) & Q(tbltext__user__last_name=surname) & Q(
					tbltext__user__name=name) & Q(tbltext__error_tag_check=1)).distinct().order_by('id_text_type'))
			
		return JsonResponse({'data': data_relation, 'text_types': text_types}, status=200)


def relation_emotions_self_rating(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		courses = list(
			TblGroup.objects.values('course_number', 'language').filter(course_number__gt=0).distinct().order_by(
				'course_number'))
		groups = list(TblGroup.objects.values('group_name', 'language').distinct().order_by('group_name'))
		
		data_relation = list(
			TblText.objects.values('language', 'emotional', 'self_rating').filter(
				Q(emotional__isnull=False) & Q(self_rating__gt=0) & ~Q(emotional=2)))
		
		data, relation, data_fisher = dashboards.get_stat(data_relation, 'emotional', 'emotional__emotional_name',
								  'self_rating', 'self_rating_text', True)
		
		return render(request, 'relation_emotions_self_rating.html', {'right': True, 'languages': languages,
									      'courses': courses, 'groups': groups,
									      'data_relation': data, 'relation': relation,
									      'data_fisher': data_fisher})
	else:
		list_filters = json.loads(request.body)
		flag_post = list_filters['flag_post']
		
		if flag_post == 'enrollment_date':
			group = list_filters['group']
			enrollment_date = list(
				TblGroup.objects.values('enrollment_date').filter(group_name=group).distinct().order_by(
					'enrollment_date'))
			
			for date in enrollment_date:
				date['enrollment_date'] = str(date['enrollment_date'].year) + ' \ ' \
								+ str(date['enrollment_date'].year + 1)
				
			return JsonResponse({'enrollment_date': enrollment_date}, status=200)
			
		if flag_post == 'course':
			course = list_filters['course']
			
			data_relation = list(TblText.objects.values('language', 'emotional', 'self_rating').filter(
				Q(emotional__isnull=False) & Q(self_rating__gt=0) & Q(tbltextgroup__group__course_number=course) & ~Q(
					emotional=2)))
			
		if flag_post == 'group':
			group = list_filters['group']
			date = list_filters['date']
			group_date = date[:4] + '-09-01'
			
			data_relation = list(
				TblText.objects.values('language', 'emotional', 'self_rating').filter(
					Q(emotional__isnull=False) & Q(self_rating__gt=0) & Q(
						tbltextgroup__group__group_name=group) & Q(
						tbltextgroup__group__enrollment_date=group_date) & ~Q(emotional=2)))
			
		data, relation, data_fisher = dashboards.get_stat(data_relation, 'emotional', 'emotional__emotional_name',
								  'self_rating', 'self_rating_text', True)
		
		return JsonResponse({'data_relation': data, 'relation': relation, 'data_fisher': data_fisher}, status=200)


def relation_emotions_assessment(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		courses = list(
			TblGroup.objects.values('course_number', 'language').filter(course_number__gt=0).distinct().order_by(
				'course_number'))
		groups = list(TblGroup.objects.values('group_name', 'language').distinct().order_by('group_name'))
		
		data_relation = list(
			TblText.objects.values('language', 'emotional', 'assessment').filter(
				Q(emotional__isnull=False) & Q(assessment__gt=0) & ~Q(emotional=2)))
		
		data, relation, data_fisher = dashboards.get_stat(data_relation, 'emotional', 'emotional__emotional_name',
								  'assessment', 'assessment_text', True)
		
		return render(request, 'relation_emotions_assessment.html', {'right': True, 'languages': languages,
									     'courses': courses, 'groups': groups,
									     'data_relation': data, 'relation': relation,
									     'data_fisher': data_fisher})
	else:
		list_filters = json.loads(request.body)
		flag_post = list_filters['flag_post']
		
		if flag_post == 'enrollment_date':
			group = list_filters['group']
			enrollment_date = list(
				TblGroup.objects.values('enrollment_date').filter(group_name=group).distinct().order_by(
					'enrollment_date'))
			
			for date in enrollment_date:
				date['enrollment_date'] = str(date['enrollment_date'].year) + ' \ ' \
								+ str(date['enrollment_date'].year + 1)
				
			return JsonResponse({'enrollment_date': enrollment_date}, status=200)
			
		if flag_post == 'course':
			course = list_filters['course']
			
			data_relation = list(
				TblText.objects.values('language', 'emotional', 'assessment').filter(
					Q(emotional__isnull=False) & Q(assessment__gt=0) & Q(
						tbltextgroup__group__course_number=course) & ~Q(emotional=2)))
			
		if flag_post == 'group':
			group = list_filters['group']
			date = list_filters['date']
			group_date = date[:4] + '-09-01'
			
			data_relation = list(TblText.objects.values('language', 'emotional', 'assessment').filter(
				Q(emotional__isnull=False) & Q(assessment__gt=0) & Q(tbltextgroup__group__group_name=group) & Q(
					tbltextgroup__group__enrollment_date=group_date) & ~Q(emotional=2)))
			
		data, relation, data_fisher = dashboards.get_stat(data_relation, 'emotional', 'emotional__emotional_name',
								  'assessment', 'assessment_text', True)
		
		return JsonResponse({'data_relation': data, 'relation': relation, 'data_fisher': data_fisher}, status=200)


def relation_self_rating_assessment(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		courses = list(
			TblGroup.objects.values('course_number', 'language').filter(course_number__gt=0).distinct().order_by(
				'course_number'))
		groups = list(TblGroup.objects.values('group_name', 'language').distinct().order_by('group_name'))
		
		data_relation = list(TblText.objects.values('language', 'self_rating', 'assessment').filter(
			Q(self_rating__gt=0) & Q(assessment__gt=0)))
		
		data, relation, data_fisher = dashboards.get_stat(data_relation, 'self_rating', 'self_rating_text',
								  'assessment', 'assessment_text', False)
		
		return render(request, 'relation_self_rating_assessment.html', {'right': True, 'languages': languages,
										'courses': courses, 'groups': groups,
										'data_relation': data, 'relation': relation,
										'data_fisher': data_fisher})
	else:
		list_filters = json.loads(request.body)
		flag_post = list_filters['flag_post']
		
		if flag_post == 'enrollment_date':
			group = list_filters['group']
			enrollment_date = list(
				TblGroup.objects.values('enrollment_date').filter(group_name=group).distinct().order_by(
					'enrollment_date'))
			
			for date in enrollment_date:
				date['enrollment_date'] = str(date['enrollment_date'].year) + ' \ ' \
								+ str(date['enrollment_date'].year + 1)
				
			return JsonResponse({'enrollment_date': enrollment_date}, status=200)
			
		if flag_post == 'course':
			course = list_filters['course']
			
			data_relation = list(TblText.objects.values('language', 'self_rating', 'assessment').filter(
				Q(self_rating__gt=0) & Q(assessment__gt=0) & Q(tbltextgroup__group__course_number=course)))
			
		if flag_post == 'group':
			group = list_filters['group']
			date = list_filters['date']
			group_date = date[:4] + '-09-01'
			
			data_relation = list(TblText.objects.values('language', 'self_rating', 'assessment').filter(
				Q(self_rating__gt=0) & Q(assessment__gt=0) & Q(tbltextgroup__group__group_name=group) & Q(
					tbltextgroup__group__enrollment_date=group_date)))
			
		data, relation, data_fisher = dashboards.get_stat(data_relation, 'self_rating', 'self_rating_text',
								  'assessment', 'assessment_text', False)
		
		return JsonResponse({'data_relation': data, 'relation': relation, 'data_fisher': data_fisher}, status=200)


def relation_course_errors(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
		
	if request.method != 'POST':
		languages = list(TblLanguage.objects.values())
		tags = list(TblTag.objects.values('id_tag', 'tag_language', 'tag_text', 'tag_text_russian').filter(
			markup_type=1).order_by('id_tag'))
		
		return render(request, 'relation_course_errors.html', {'right': True, 'languages': languages, 'tags': tags})
	else:
		list_filters = json.loads(request.body)
		flag_post = list_filters['flag_post']
		tag = list_filters['tag']
		checked_tag_children = list_filters['checked_tag_children']
		
		tags = [tag]
		if checked_tag_children:
			tags = dashboards.get_tag_children(tag)
			
		if flag_post == 'courses':
			data_relation = list(
				TblMarkup.objects.values('sentence__text_id__tbltextgroup__group__course_number').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(tag__id_tag__in=tags) & Q(
						sentence__text_id__tbltextgroup__group__course_number__isnull=False)).annotate(
					count_data=Count('sentence__text_id__tbltextgroup__group__course_number')))
			
		if flag_post == 'students':
			data_relation = list(TblMarkup.objects.values('sentence__text_id__user',
								      'sentence__text_id__tbltextgroup__group__course_number').filter(
				Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(tag__id_tag__in=tags) & Q(
					sentence__text_id__tbltextgroup__group__course_number__isnull=False)).annotate(
				count_data=Count('sentence__text_id__tbltextgroup__group__course_number')))
			
		if flag_post == 'groups':
			data_relation = list(TblMarkup.objects.values('sentence__text_id__tbltextgroup__group',
								      'sentence__text_id__tbltextgroup__group__course_number').filter(
				Q(tag__markup_type=1) & Q(sentence__text_id__error_tag_check=1) & Q(
					sentence__text_id__tbltextgroup__group__isnull=False) & Q(tag__id_tag__in=tags)).annotate(
				count_data=Count('sentence__text_id__tbltextgroup__group__course_number')))
			
		course = []
		count_errors = []
		
		for data in data_relation:
			course.append(data['sentence__text_id__tbltextgroup__group__course_number'])
			count_errors.append(data['count_data'])
			
		critical_stat_level = 0.05
		n = len(course)
		
		if n > 1:
			if len(set(course)) == 1 or len(set(count_errors)) == 1:
				relation = {'result': 'один из параметров константа', 'stat': 'None', 'pvalue': 'None', 'N': n}
				
			else:
				result = scipy.stats.spearmanr(course, count_errors)
				
				t = abs(result.statistic) * np.sqrt((n-2) / (1 - result.statistic * result.statistic))
				t_critical = scipy.stats.t.ppf(1-critical_stat_level/2, n-2)
				
				if t < t_critical:
					worth = 'корреляция статистически не значимая'
				else:
					worth = 'статистически значимая корреляция'
					
				if np.isnan(result.pvalue):
					pvalue = 'Nan'
				else:
					pvalue = result.pvalue
					
				if result.statistic == 0:
					relation = {'result': f'связь отсутствует  ({worth})', 'stat': result.statistic, 'pvalue': pvalue,
						    'N': n}
				elif result.statistic >= 0.75:
					relation = {'result': f'очень высокая положительная связь ({worth})', 'stat': result.statistic,
						    'pvalue': pvalue, 'N': n}
				elif 0.5 <= result.statistic < 0.75:
					relation = {'result': f'высокая положительная связь  ({worth})', 'stat': result.statistic,
						    'pvalue': pvalue, 'N': n}
				elif 0.25 <= result.statistic < 0.5:
					relation = {'result': f'средняя положительная связь  ({worth})', 'stat': result.statistic,
						    'pvalue': pvalue, 'N': n}
				elif 0 < result.statistic < 0.25:
					relation = {'result': f'слабая положительная связь  ({worth})', 'stat': result.statistic,
						    'pvalue': pvalue, 'N': n}
				elif -0.25 <= result.statistic < 0:
					relation = {'result': f'слабая отрицательная связь  ({worth})', 'stat': result.statistic,
						    'pvalue': pvalue, 'N': n}
				elif -0.5 <= result.statistic < -0.25:
					relation = {'result': f'средняя отрицательная связь  ({worth})', 'stat': result.statistic,
						    'pvalue': pvalue, 'N': n}
				elif -0.75 <= result.statistic < -0.5:
					relation = {'result': f'высокая отрицательная связь  ({worth})', 'stat': result.statistic,
						    'pvalue': pvalue, 'N': n}
				else:
					relation = {'result': f'очень высокая отрицательная связь  ({worth})', 'stat': result.statistic,
						    'pvalue': pvalue, 'N': n}
		else:
			relation = {'result': '-', 'stat': '-', 'pvalue': '-', 'N': n}
			
		return JsonResponse({'data_relation': data_relation, 'relation': relation}, status=200)
