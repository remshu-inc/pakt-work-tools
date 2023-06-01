from urllib import request
from django.contrib.auth import login, logout
from django.contrib.auth.models import AnonymousUser

from .login import MyBackend
# from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import TblTeacher, TblUser, TblStudent, TblGroup, TblStudentGroup, TblLanguage
from .forms import UserCreationForm, StudentCreationForm, LoginForm, GroupCreationForm, GroupModifyForm, \
    GroupModifyStudent, StudentGroupCreationForm

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
    try:
        if not request.user.is_teacher():
            return redirect('home')
    except:
        return redirect('home')

    if request.method == 'POST':
        form_user = UserCreationForm(request.POST)
        form_student = StudentCreationForm(request.POST)
        form_student_group = StudentGroupCreationForm(request.POST)

        # Проверка заполнености полей
        if request.POST['login'] == '' and request.POST['password'] == '':
            form_user.add_error('login', 'Необходимо заполнить поле')
            form_user.add_error('password', 'Необходимо заполнить поле')
            return render(request, 'signup.html', {'form_user': form_user, 'form_student': form_student,
                                                   'form_student_group': form_student_group})
        elif request.POST['login'] == '':
            form_user.add_error('login', 'Необходимо заполнить поле')
            return render(request, 'signup.html', {'form_user': form_user, 'form_student': form_student,
                                                   'form_student_group': form_student_group})
        elif request.POST['password'] == '':
            form_user.add_error('password', 'Необходимо заполнить поле')
            return render(request, 'signup.html', {'form_user': form_user, 'form_student': form_student,
                                                   'form_student_group': form_student_group})

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

            return redirect('corpus')

    else:
        form_user = UserCreationForm()
        form_student = StudentCreationForm()
        form_student_group = StudentGroupCreationForm()

    return render(request, 'signup.html',
                  {'form_user': form_user, 'form_student': form_student, 'form_student_group': form_student_group})


def change_password(request):
    try:
        if not request.user.is_teacher():
            return redirect('home')
    except:
        return redirect('home')

    if request.POST:
        user_id = request.POST['student']
        password = request.POST['password']

        salt = 'DsaVfeqsJw00XvgZnFxlOFkqaURzLbyI'
        hash = sha512((password + salt).encode('utf-8'))
        hash = hash.hexdigest()

        TblUser.objects.filter(id_user=user_id).update(password=hash)

        return redirect('manage')

    else:
        students = TblStudent.objects.all()

        all_students = []
        count = 1
        for student in students:
            try:
                user = TblUser.objects.filter(id_user=student.user_id).first()
                all_students.append(
                    [user.id_user, user.last_name + ' ' + user.name])
            except:
                count += 1

        return render(request, 'change_password.html', {'all_students': all_students})


def signup_teacher(request):
    try:
        if not request.user.is_teacher():
            return redirect('home')
    except:
        return redirect('home')

    if request.method == 'POST':
        form_user = UserCreationForm(request.POST)

        # Проверка заполнености полей
        if request.POST['login'] == '' and request.POST['password'] == '':
            form_user.add_error('login', 'Необходимо заполнить поле')
            form_user.add_error('password', 'Необходимо заполнить поле')
            return render(request, 'signup_teacher.html', {'form_user': form_user})
        elif request.POST['login'] == '':
            form_user.add_error('login', 'Необходимо заполнить поле')
            return render(request, 'signup_teacher.html', {'form_user': form_user})
        elif request.POST['password'] == '':
            form_user.add_error('password', 'Необходимо заполнить поле')
            return render(request, 'signup_teacher.html', {'form_user': form_user})

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

            return redirect('corpus')

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
        if request.POST['login'] == '' and request.POST['password'] == '':
            form_login.add_error('login', 'Необходимо заполнить поле')
            form_login.add_error('password', 'Необходимо заполнить поле')
            return render(request, 'login.html', {'form_login': form_login})

        elif request.POST['login'] == '':
            form_login.add_error('login', 'Необходимо заполнить поле')
            return render(request, 'login.html', {'form_login': form_login})

        elif request.POST['password'] == '':
            form_login.add_error('password', 'Необходимо заполнить поле')
            return render(request, 'login.html', {'form_login': form_login})

        if form_login.is_valid():
            username = form_login.cleaned_data["login"]
            password = form_login.cleaned_data["password"]

            user = MyBackend.authenticate(login=username, password=password)

            # Если пользваотель существует
            if user:
                login(request, user)
                return redirect('corpus')

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

    if teacher or student:
        # TODO Связать с таблицей работ и дэшем
        # if teacher:
        #     available_students = []
        #     lang = [1,2] if not request.user.language_id else [request.user.language_id]
        #     available_students = [
        #         {
        #             'id':el['user_id'],
        #             'name': f"{el['user_id__last_name']} {el['user_id__name']} {el['user_id__patronymic']}"
        #          }   for el in TblStudent.objects\
        #                                                 .filter(user_id__language_id__in = lang)\
        #                                                 .all()\
        #                                                 .order_by(
        #                                                         'user_id__last_name',
        #                                                         'user_id__name',
        #                                                         'user_id__patronymic'
        #                                                         )\
        #                                                 .values(
        #                                                     'user_id__last_name',
        #                                                     'user_id__name',
        #                                                     'user_id__patronymic',
        #                                                     'user_id'
        #                                                 )]
        return (render(request, 'manage_page.html',
                       {
                           'teacher': teacher,
                           'student': student,
                           # 'avaliable_students': available_students,
                           'superuser': check_is_superuser(request.user.id_user)
                       }
                       ))
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
    if hasattr(request.user, "is_teacher") and request.user.is_teacher():
        if request.method != 'POST':
            return (render(request, 'group_creation_form.html',
                           {
                               'right': True,
                               'form': GroupCreationForm(),
                               'bad_name': False,
                               'bad_year': False,
                               'exist': False,
                               'success': False,
                           }))
        else:
            form = GroupCreationForm(request.POST or None)
            if form.is_valid():
                group_name = str(form.cleaned_data['group_name'])
                year = str(form.cleaned_data['year'])
                course_number = int(form.cleaned_data['course_number'])

                if _symbol_check(group_name):
                    if year.isnumeric() and 999 < int(year) < datetime.now().year + 1:

                        enrollement_date = datetime(int(year), 9, 1)
                        valid_sample = TblGroup.objects.filter(Q(group_name=group_name)
                                                               & Q(enrollement_date=enrollement_date)).values(
                            'id_group').all()

                        if not valid_sample.exists():
                            new_row = TblGroup(
                                group_name=group_name,
                                enrollement_date=enrollement_date,
                                language_id=request.user.language_id,
                                course_number=course_number)
                            new_row.save()

                            return (render(request, 'group_creation_form.html',
                                           {
                                               'right': True,
                                               'form': GroupCreationForm(),
                                               'bad_name': False,
                                               'bad_year': False,
                                               'exist': False,
                                               'success': True,
                                           }))
                        else:
                            return (render(request, 'group_creation_form.html',
                                           {
                                               'right': True,
                                               'form': GroupCreationForm(),
                                               'bad_name': False,
                                               'bad_year': False,
                                               'exist': True,
                                               'success': False,
                                           }, status=400))
                    else:
                        return (render(request, 'group_creation_form.html',
                                       {
                                           'right': True,
                                           'form': GroupCreationForm(),
                                           'bad_name': False,
                                           'bad_year': True,
                                           'exist': False,
                                           'success': False,
                                       }, status=400))
            else:
                return (render(request, 'group_creation_form.html',
                               {
                                   'right': True,
                                   'form': GroupCreationForm(),
                                   'bad_name': True,
                                   'bad_year': False,
                                   'exist': False,
                                   'success': False,
                               }, status=400))
    else:
        return (render(request, 'group_creation_form.html',
                       {
                           'right': False,
                           'form': GroupCreationForm(),
                           'bad_name': False,
                           'bad_year': False,
                           'exist': False,
                           'success': False,
                       }, status=403))


# * Group selection page
def group_selection(request):
    if hasattr(request.user, 'is_teacher') and request.user.is_teacher():
        groups = TblGroup.objects.filter(
            language_id=request.user.language_id).order_by('-enrollement_date')
        if groups.exists():
            groups = groups.values()
            for index in range(len(groups)):
                groups[index]['enrollement_date'] = str(groups[index]['enrollement_date'].year) \
                    + ' /  ' + str(groups[index]['enrollement_date'].year + 1)

            return (render(request, 'group_select.html', context={
                'right': True,
                'groups_exist': True,
                'groups': groups
            }))
        else:
            return (render(request, 'group_select.html', context={
                'right': True,
                'groups_exist': False,
                'groups': []
            }, status=404))
    else:
        return (render(request, 'group_select.html', context={
            'right': False,
            'groups_exist': False,
            'groups': []
        }, status=403))

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
    if hasattr(request.user, 'is_teacher') and request.user.is_teacher():
        groups = TblGroup.objects.filter(id_group=group_id).values(
            'enrollement_date', 'group_name', 'course_number')
        if groups.exists():
            year = groups[0]['enrollement_date'].year
            group_name = groups[0]['group_name']
            course_number = groups[0]['course_number']
            students_in = _get_group_students(group_id, True)
            students_out = _get_group_students(group_id, False)
        else:
            return (render(request, 'group_modify.html', context={
                'right': True,
                'exist': False
            }, status=404))
        if request.method != 'POST':

            # * Page Creation
            groups = TblGroup.objects.filter(id_group=group_id).values(
                'enrollement_date', 'group_name')
            if groups.exists():
                return (render(request, 'group_modify.html', context={
                    'right': True,
                    'exist': True,
                    'bad_name': False,
                    'bad_year': False,
                    'group_students': students_in,
                    'del_std_form': GroupModifyStudent(students_in),
                    'add_std_form': GroupModifyStudent(students_out),
                    'data_form': GroupModifyForm(year, group_name, course_number)}))

        # * Modify info about group
        elif 'group_info_modify' in request.POST:

            form = GroupModifyForm(
                year, group_name, course_number, request.POST or None)
            if form.is_valid():
                group_name_new = str(form.cleaned_data['group_name'])
                year_new = str(form.cleaned_data['year'])
                course_number_new = int(form.cleaned_data['course_number'])

                if _symbol_check(group_name_new):
                    if year_new.isnumeric() and 999 < int(year_new) < datetime.now().year + 1:
                        enrollement_date = datetime(int(year_new), 9, 1)

                        group = TblGroup.objects.get(id_group=group_id)
                        group.group_name = group_name_new
                        group.enrollement_date = enrollement_date
                        group.course_number = course_number_new

                        group.save()
                        return (render(request, 'group_modify.html', context={
                            'right': True,
                            'exist': True,
                            'bad_name': False,
                            'bad_year': False,
                            'group_students': students_in,
                            'del_std_form': GroupModifyStudent(students_in),
                            'add_std_form': GroupModifyStudent(students_out),
                            'data_form': GroupModifyForm(year, group_name, course_number)}))

                    else:
                        return (render(request, 'group_modify.html', context={
                            'right': True,
                            'exist': True,
                            'bad_name': False,
                            'bad_year': True,
                            'group_students': students_in,
                            'del_std_form': GroupModifyStudent(students_in),
                            'add_std_form': GroupModifyStudent(students_out),
                            'data_form': GroupModifyForm(year, group_name, course_number)}, status=400))
                else:
                    return (render(request, 'group_modify.html', context={
                        'right': True,
                        'exist': True,
                        'bad_name': True,
                        'bad_year': False,
                        'group_students': students_in,
                        'del_std_form': GroupModifyStudent(students_in),
                        'add_std_form': GroupModifyStudent(students_out),
                        'data_form': GroupModifyForm(year, group_name, course_number)}, status=400))

        elif 'add_studs' in request.POST:
            form = GroupModifyStudent(students_out, request.POST or None)

            if form.is_valid():
                values = [int(element)
                          for element in form.cleaned_data['studs']]
                # TODO: Добавить вывод ошибки
                if not TblStudentGroup.objects.filter(
                        Q(group_id=group_id) &
                        Q(student_id__in=values)).exists():
                    values = [TblStudentGroup(
                        student_id=value, group_id=group_id) for value in values]
                    TblStudentGroup.objects.bulk_create(values)

                updated_students_in = _get_group_students(group_id, True)
                updated_students_out = _get_group_students(group_id, False)

                return (render(request, 'group_modify.html', context={
                    'right': True,
                    'exist': True,
                    'bad_name': False,
                    'bad_year': False,
                    'group_students': updated_students_in,
                    'del_std_form': GroupModifyStudent(updated_students_in),
                    'add_std_form': GroupModifyStudent(updated_students_out),
                    'data_form': GroupModifyForm(year, group_name, course_number)}))
            else:
                return (render(request, 'group_modify.html', context={
                    'right': False}, status=400))

        elif 'del_studs' in request.POST:
            form = GroupModifyStudent(students_in, request.POST or None)
            if form.is_valid():
                values = [int(element)
                          for element in form.cleaned_data['studs']]

                query = TblStudentGroup.objects.filter(
                    Q(group_id=group_id) & Q(student_id__in=values))
                # TODO: Добавить вывод ошибки
                if query.exists() and len(query) == len(values):
                    query.delete()
                else:
                    return (render(request, 'group_modify.html', context={
                        'right': True,
                        'exist': True,
                        'bad_name': False,
                        'bad_year': False,
                        'group_students': students_in,
                        'del_std_form': GroupModifyStudent(students_in),
                        'add_std_form': GroupModifyStudent(students_out),
                        'data_form': GroupModifyForm(year, group_name, course_number)}))

                updated_students_in = _get_group_students(group_id, True)
                updated_students_out = _get_group_students(group_id, False)

                return (render(request, 'group_modify.html', context={
                    'right': True,
                    'exist': True,
                    'bad_name': False,
                    'bad_year': False,
                    'group_students': updated_students_in,
                    'del_std_form': GroupModifyStudent(updated_students_in),
                    'add_std_form': GroupModifyStudent(updated_students_out),
                    'data_form': GroupModifyForm(year, group_name, course_number)}))

        elif 'del_group' in request.POST:
            TblGroup.objects.filter(id_group=group_id).delete()
            return redirect('group_selection')

        else:
            return (render(request, 'group_modify.html', context={
                'right': False
            }, status=403))

    else:
        return (render(request, 'group_modify.html', context={
            'right': False
        }, status=403))


def tasks_info(request, user_id):
    if (request.user.is_student() and request.user.id_user == user_id) or request.user.is_teacher():
        about_student = TblStudent.objects\
            .filter(user_id=user_id)\
            .values('user_id__name', 'user_id__last_name', 'user_id__patronymic').all()
        if about_student.exists():
            about_student = {
                'name': about_student[0]['user_id__name'] if about_student[0]['user_id__name'] else '',
                'last_name': about_student[0]['user_id__last_name'] if about_student[0]['user_id__last_name'] else '',
                'patronymic': about_student[0]['user_id__patronymic'] if about_student[0]['user_id__patronymic'] else '',
            }
        else:
            about_student = {
                'name': 'Не указано',
                'last_name': 'Не указано',
                'patronymic': 'Не указано'
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
        out = []
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

                out.append({
                    'header': task['header'],
                    'path': path,
                    'error_check': error_check,
                    'assessment': assessment,
                    'err_count': num_of_errors,
                    'date': task['create_date']
                })

        return (render(request, 'tasks_list.html', context={
            'right': True,
            'author': about_student,
            'tasks': out
        }))
    else:
        return (render(request, 'tasks_list.html', context={
            'right': False
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
            enrollement_date = list(TblGroup.objects.values(
                'enrollement_date').distinct().order_by('enrollement_date'))
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
                                     'data_grade_errors': data_grade, 'enrollement_date': enrollement_date}, status=200)

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
                                             sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollement_date=datetime.strptime(
                                                 date, "%Y-%m-%d")) & Q(sentence__text_id__header=text) & Q(
                                             sentence__text_id__text_type=text_types_id)).annotate(count_data=Count('tag__id_tag')))

            data_grade = list(
                TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
                    Q(tag__markup_type=1) & Q(
                        sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
                        sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollement_date=datetime.strptime(
                            date, "%Y-%m-%d")) & Q(sentence__text_id__header=text) & Q(
                        sentence__text_id__text_type=text_types_id)).annotate(count_data=Count('grade__id_grade')))

        elif groups and text:
            data_count_errors = list(
                TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
                                         'tag__tag_text_russian').filter(Q(tag__markup_type=1) & Q(
                                             sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
                                             sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollement_date=datetime.strptime(
                                                 date, "%Y-%m-%d")) & Q(sentence__text_id__header=text)).annotate(
                    count_data=Count('tag__id_tag')))

            data_grade = list(
                TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
                    Q(tag__markup_type=1) & Q(
                        sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
                        sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollement_date=datetime.strptime(
                            date, "%Y-%m-%d")) & Q(sentence__text_id__header=text)).annotate(
                    count_data=Count('grade__id_grade')))

        elif groups and text_types_id:
            data_count_errors = list(
                TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
                                         'tag__tag_text_russian').filter(Q(tag__markup_type=1) & Q(
                                             sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
                                             sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollement_date=datetime.strptime(
                                                 date, "%Y-%m-%d")) & Q(sentence__text_id__text_type=text_types_id)).annotate(
                    count_data=Count('tag__id_tag')))

            data_grade = list(
                TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
                    Q(tag__markup_type=1) & Q(
                        sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
                        sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollement_date=datetime.strptime(
                            date, "%Y-%m-%d")) & Q(sentence__text_id__text_type=text_types_id)).annotate(
                    count_data=Count('grade__id_grade')))

        elif groups:
            data_count_errors = list(
                TblMarkup.objects.values('tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text',
                                         'tag__tag_text_russian').filter(Q(tag__markup_type=1) & Q(
                                             sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
                                             sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollement_date=datetime.strptime(
                                                 date, "%Y-%m-%d"))).annotate(count_data=Count('tag__id_tag')))

            data_grade = list(
                TblMarkup.objects.values('grade__id_grade', 'grade__grade_name', 'grade__grade_language').filter(
                    Q(tag__markup_type=1) & Q(
                        sentence__text_id__user__tblstudent__tblstudentgroup__group__group_name=groups) & Q(
                        sentence__text_id__user__tblstudent__tblstudentgroup__group__enrollement_date=datetime.strptime(
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
