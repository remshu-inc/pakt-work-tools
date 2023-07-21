from urllib import request
from django.contrib.auth import login, logout
from django.contrib.auth.models import AnonymousUser

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
from django.views.generic import View
from text_app.models import TblTag, TblMarkup
# ----------------------------


def signup(request):
	if not (hasattr(request.user, 'is_teacher') and request.user.is_teacher()):
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


def change_password(request):
	if not (hasattr(request.user, 'is_teacher') and request.user.is_teacher()):
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

	return render(request, 'change_password.html', {'students': students, 'password_form': password_form})


def signup_teacher(request):
	if not (hasattr(request.user, 'is_teacher') and request.user.is_teacher() and check_is_superuser(request.user.id_user)):
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
		return redirect('corpus')

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
	if not (hasattr(request.user, 'is_teacher') and request.user.is_teacher()):
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
	if not (hasattr(request.user, 'is_teacher') and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
	
	groups = TblGroup.objects.filter(
		language_id=request.user.language_id).order_by('-enrollment_date', 'course_number', 'group_name').values()

	for index in range(len(groups)):
		groups[index]['enrollment_date'] = str(groups[index]['enrollment_date'].year) \
			+ ' /  ' + str(groups[index]['enrollment_date'].year + 1)

	return (render(request, 'group_select.html', context={'groups': groups}))

		

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
	if not (hasattr(request.user, 'is_teacher') and request.user.is_teacher()):
		return render(request, 'access_denied.html')
	
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
	if not (hasattr(request.user, 'is_teacher') and request.user.is_teacher()):
		return render(request, 'access_denied.html')
		
	query = TblStudentGroup.objects.filter(Q(group_id=group_id) & Q(student_id=student_id))

	if query.exists():
		query.delete()

	return group_modify(request, group_id)

def delete_group(request, group_id) :
	if not (hasattr(request.user, 'is_teacher') and request.user.is_teacher()):
		return render(request, 'access_denied.html')
	
	TblGroup.objects.filter(id_group=group_id).delete()
	return redirect('group_selection')


def group_add_student(request, group_id, student_id):
	if not (hasattr(request.user, 'is_teacher') and request.user.is_teacher()):
		return render(request, 'access_denied.html')

	if TblStudent.objects.filter(Q(id_student=student_id)).exists() and (not TblStudentGroup.objects.filter(
						Q(group_id=group_id) &
						Q(student_id=student_id)).exists()):	
		TblStudentGroup.objects.create(student_id=student_id, group_id=group_id)

	return group_modify(request, group_id)


def tasks_info(request, user_id):
	if not ((request.user.is_student() and request.user.id_user == user_id) or request.user.is_teacher()):
				return render(request, 'access_denied.html')
	
	about_student = TblStudent.objects\
		.filter(user_id=user_id)\
		.values('user_id__name', 'user_id__last_name', 'user_id__patronymic').all()
	
	author_data = {}
	if about_student.exists():
		author_data = {
			'name': about_student[0]['user_id__name'] if about_student[0]['user_id__name'] else '',
			'last_name': about_student[0]['user_id__last_name'] if about_student[0]['user_id__last_name'] else '',
			'patronymic': about_student[0]['user_id__patronymic'] if about_student[0]['user_id__patronymic'] else '',
		}

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
		'tasks': task_list
	}))


# * Dashboard (Polina Osipova)
def DFS(v, c, h, data):
	h[v] = 1
	c += data[v]["count_data"]
	for i in range(len(data)):
		if data[i]["tag__tag_parent"] == data[v]["tag__id_tag"]:
			if h[i] == 0:
				c = DFS(i, c, h, data)

	return c


def data_group_by_parent_id(data):
	n = len(data)
	h = [0 for i in range(n)]

	for i in range(n):
		if h[i] == 0 and data[i]["tag__tag_parent"] == None:
			c = 0
			c = DFS(i, c, h, data)
			data[i]["count_data"] = c

	data_group = []
	for el in data:
		if el["tag__tag_parent"] == None:
			data_group.append(el)

	return data_group


def get_data_errors(data_count_errors):
	list_tag_id_in_markup = []
	for data in data_count_errors:
		list_tag_id_in_markup.append(data["tag__id_tag"])

	data_tags_not_in_errors = list(
		TblTag.objects.values('id_tag', 'tag_parent', 'tag_language', 'tag_text', 'tag_text_russian').filter(
			Q(markup_type=1) & ~Q(id_tag__in=list_tag_id_in_markup)).annotate(
			count_data=Value(0, output_field=IntegerField()), tag__id_tag=F('id_tag'), tag__tag_parent=F('tag_parent'),
			tag__tag_language=F('tag_language'), tag__tag_text=F('tag_text'),
			tag__tag_text_russian=F('tag_text_russian')))

	data = data_count_errors + data_tags_not_in_errors
	data = data_group_by_parent_id(data)

	return data


class DiagramView(View):
	def get(self, request):
		if request.user.is_teacher():
			languages = list(TblLanguage.objects.values())
			text_types = list(TblTextType.objects.values())
			groups = list(TblGroup.objects.values(
				'group_name').distinct().order_by('group_name'))
			enrollment_date = list(TblGroup.objects.values(
				'enrollment_date').distinct().order_by('enrollment_date'))
			courses = list(TblStudent.objects.values(
				'course_number').distinct().order_by('course_number'))
			texts = list(TblText.objects.values(
				'header', 'language').distinct().order_by('header'))

			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(tag__markup_type=1).annotate(
					count_data=Count('tag__id_tag')))
			data = get_data_errors(data_count_errors)

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					tag__markup_type=1).annotate(count_data=Count('grade__id_grade')))

			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				return JsonResponse({'data_type_errors': data, 'list_languages': languages, 'list_text_types': text_types,
									'list_groups': groups, 'list_courses': courses, 'list_texts': texts,
									 'data_grade_errors': data_grade, 'enrollment_date': enrollment_date}, status=200)

			return render(request, 'dashboard.html', context={'right': True})
		else:
			return render(request, 'dashboard.html', context={'right': False})

	def post(self, request):
		list_filter = json.loads(request.body)
		text_types_id = list_filter['text_type_id']
		text = list_filter['text']
		surname = list_filter['surname']
		name = list_filter['name']
		patronymic = list_filter['patronymic']
		course = list_filter['course']
		groups = list_filter['groups']
		date = list_filter['date']

		if surname and name and patronymic and text and text_types_id:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__user__patronymic=patronymic) & Q(
						sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_types_id)).annotate(
					count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__user__patronymic=patronymic) & Q(
						sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_types_id)).annotate(
					count_data=Count('grade__id_grade')))

		elif surname and name and patronymic and text:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__user__patronymic=patronymic) & Q(
						sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__user__patronymic=patronymic) & Q(
						sentence__text_id__header=text)).annotate(count_data=Count('grade__id_grade')))

		elif surname and name and patronymic and text_types_id:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__user__patronymic=patronymic) & Q(
						sentence__text_id__text_type=text_types_id)).annotate(count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__user__patronymic=patronymic) & Q(
						sentence__text_id__text_type=text_types_id)).annotate(count_data=Count('grade__id_grade')))

		elif surname and name and patronymic:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(
						sentence__text_id__user__patronymic=patronymic)).annotate(count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(
						sentence__text_id__user__patronymic=patronymic)).annotate(count_data=Count('grade__id_grade')))

		elif surname and name and text and text_types_id:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__header=text) & Q(
						sentence__text_id__text_type=text_types_id)).annotate(count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__header=text) & Q(
						sentence__text_id__text_type=text_types_id)).annotate(count_data=Count('grade__id_grade')))

		elif surname and name and text:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__header=text)).annotate(
					count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__header=text)).annotate(
					count_data=Count('grade__id_grade')))

		elif surname and name and text_types_id:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__text_type=text_types_id)).annotate(
					count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name) & Q(sentence__text_id__text_type=text_types_id)).annotate(
					count_data=Count('grade__id_grade')))

		elif surname and name:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name)).annotate(count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__last_name=surname) & Q(
						sentence__text_id__user__name=name)).annotate(count_data=Count('grade__id_grade')))

		elif course and text_types_id and text:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__tblstudent__course_number=course) & Q(
						sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_types_id)).annotate(
					count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__tblstudent__course_number=course) & Q(
						sentence__text_id__header=text) & Q(sentence__text_id__text_type=text_types_id)).annotate(
					count_data=Count('grade__id_grade')))

		elif course and text:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__tblstudent__course_number=course) & Q(
						sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__tblstudent__course_number=course) & Q(
						sentence__text_id__header=text)).annotate(count_data=Count('grade__id_grade')))

		elif course and text_types_id:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__tblstudent__course_number=course) & Q(
						sentence__text_id__text_type=text_types_id)).annotate(count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__tblstudent__course_number=course) & Q(
						sentence__text_id__text_type=text_types_id)).annotate(count_data=Count('grade__id_grade')))

		elif course:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__tblstudent__course_number=course)).annotate(
					count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__user__tblstudent__course_number=course)).annotate(
					count_data=Count('grade__id_grade')))

		elif groups and text and text_types_id:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(Q(tag__markup_type=1) & Q(
											 sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
											 sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollment_date=datetime.strptime(
												 date, "%Y-%m-%d")) & Q(sentence__text_id__header=text) & Q(
											 sentence__text_id__text_type=text_types_id)).annotate(count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(
						sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
						sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollment_date=datetime.strptime(
							date, "%Y-%m-%d")) & Q(sentence__text_id__header=text) & Q(
						sentence__text_id__text_type=text_types_id)).annotate(count_data=Count('grade__id_grade')))

		elif groups and text:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(Q(tag__markup_type=1) & Q(
											 sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
											 sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollment_date=datetime.strptime(
												 date, "%Y-%m-%d")) & Q(sentence__text_id__header=text)).annotate(
					count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(
						sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
						sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollment_date=datetime.strptime(
							date, "%Y-%m-%d")) & Q(sentence__text_id__header=text)).annotate(
					count_data=Count('grade__id_grade')))

		elif groups and text_types_id:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(Q(tag__markup_type=1) & Q(
											 sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
											 sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollment_date=datetime.strptime(
												 date, "%Y-%m-%d")) & Q(sentence__text_id__text_type=text_types_id)).annotate(
					count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(
						sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
						sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollment_date=datetime.strptime(
							date, "%Y-%m-%d")) & Q(sentence__text_id__text_type=text_types_id)).annotate(
					count_data=Count('grade__id_grade')))

		elif groups:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(Q(tag__markup_type=1) & Q(
											 sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
											 sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollment_date=datetime.strptime(
												 date, "%Y-%m-%d"))).annotate(count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(
						sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
						sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollment_date=datetime.strptime(
							date, "%Y-%m-%d"))).annotate(count_data=Count('grade__id_grade')))

		elif text_types_id and text:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__text_type=text_types_id) & Q(
						sentence__text_id__header=text)).annotate(count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__text_type=text_types_id) & Q(
						sentence__text_id__header=text)).annotate(count_data=Count('grade__id_grade')))

		elif text_types_id:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__text_type=text_types_id)).annotate(
					count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__text_type=text_types_id)).annotate(
					count_data=Count('grade__id_grade')))

		elif text:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__header=text)).annotate(
					count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					Q(tag__markup_type=1) & Q(sentence__text_id__header=text)).annotate(
					count_data=Count('grade__id_grade')))

		else:
			data_count_errors = list(
				TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
										 'tag__tag_text_russian').filter(tag__markup_type=1).annotate(
					count_data=Count('tag__id_tag')))

			data_grade = list(
				TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
					tag__markup_type=1).annotate(count_data=Count('grade__id_grade')))

		data = get_data_errors(data_count_errors)

		return JsonResponse({'data_type_errors': data, 'data_grade_errors': data_grade}, status=200)
