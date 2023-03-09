# from django.views import generic
# from .models import TblText

from .models import TblReason, TblGrade, TblTextGroup, TblTextType, TblText, TblSentence, TblMarkup, TblTag, TblTokenMarkup, TblToken
from user_app.models import TblLanguage, TblTeacher, TblUser, TblStudent, TblGroup, TblStudentGroup
from text_app.models import TblTextGroup
from django.db.models import F, Q
from django.db import connection
from .forms import TextCreationForm, get_annotation_form, SearchTextForm, AssessmentModify, MetaModify, AuthorModify
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from copy import deepcopy
from right_app.views import check_permissions_work_with_annotations, check_permissions_show_text, check_permissions_edit_text, check_is_superuser
import datetime
from log_app.views import log_text

import os
os.environ['NLTK_DATA'] = '/var/www/lingo/nltk_data'
# Test

ASSESSMENT_CHOICES = {TblText.TASK_RATES[i][0]: TblText.TASK_RATES[i][1]
                      for i in range(len(TblText.TASK_RATES))}

# Test

# class TextList(generic.ListView):
#     queryset = TblText.objects
#     template_name = 'corpus.html'


def show_files(request, language=None, text_type=None):
    # Для выбора языка

    if not request.user.is_authenticated:
        return redirect('login')
    elif request.user.is_teacher():
        form_search = SearchTextForm()

    else:
        form_search = False

    #! --------------------------------------------
    #! Переделать
    lang_query = TblLanguage.objects.filter(language_name = language).all().values('id_language')
    languages = [1,2] if not lang_query.exists() else [lang_query[0]['id_language']]
    students = TblStudent.objects.filter(user_id__language_id__in = languages).all().order_by('user_id__last_name')
    #!---------------------------------------------

    all_students = []
    count = 1
    for student in students:
        try:
            user = TblUser.objects.filter(id_user=student.user_id).first()
            all_students.append(
                [user.id_user, user.last_name + ' ' + user.name])
        except:
            count += 1

    if language == None:
        try:
            # Определение сортировки
            order_by = 'language_name'
            reverse = False
            if request.GET:
                order_by = request.GET.get('order_by', 'defaultOrderField')
                # Covert reverse str to bool
                reverse = (request.GET.get(
                    'reverse', 'defaultOrderField') == 'True')

                if reverse:
                    order_by = '-' + order_by

            list_language = TblLanguage.objects.all().order_by(order_by)

            return render(request, "corpus.html", context={'list_language': list_language, 'form_search': form_search, 'order_by': order_by, 'reverse': not reverse, 'all_students': all_students})

        # except TblLanguage.DoesNotExist:
        # TODO: прописать исключение для каждой ошибки?
        except:
            return render(request, "corpus.html", context={'error': True, 'text_html': '<div id = "Text_found_err">404 Not Found<\div>'})

    # Для выбора типа текста
    elif text_type == None:
        order_by = 'text_type_name'
        reverse = False
        if request.GET:
            order_by = request.GET.get('order_by', 'defaultOrderField')
            # Covert reverse str to bool
            reverse = (request.GET.get(
                'reverse', 'defaultOrderField') == 'True')

            if reverse:
                order_by = '-' + order_by

        language_object = TblLanguage.objects.filter(language_name=language)
        if len(language_object) == 0:
            return render(request, "corpus.html", context={'error': True, 'text_html': 'Language not found'})
        else:
            language_id = language_object.first().id_language

        list_text_type = TblTextType.objects.filter(
            language_id=language_id).order_by(order_by)
        if len(list_text_type) == 0:
            return render(request, "corpus.html", context={'error': True, 'text_html': 'Text type not found'})
        else:
            return render(request, "corpus.html", context={'list_text_type': list_text_type, 'form_search': form_search, 'order_by': order_by, 'reverse': not reverse, 'all_students': all_students})

    # Для выбора текста
    else:
        order_by = 'modified_date'
        reverse = False
        if request.GET:
            order_by = request.GET.get('order_by', 'defaultOrderField')
            # Covert reverse str to bool
            reverse = (request.GET.get(
                'reverse', 'defaultOrderField') == 'True')

            if reverse:
                order_by = '-' + order_by

        language_object = TblLanguage.objects.filter(language_name=language)
        if len(language_object) == 0:
            return (render(request, "corpus.html", context={'error': True, 'text_html': 'Language not found'}))
        else:
            language_id = language_object.first().id_language

        text_type_object = TblTextType.objects.filter(
            language_id=language_id, text_type_name=text_type)
        if len(text_type_object) == 0:
            return (render(request, "corpus.html", context={'error': True, 'text_html': 'Text type not found'}))
        else:
            text_type_id = text_type_object.first().id_text_type

        if check_permissions_show_text(request.user.id_user):
            list_text = TblText.objects.filter(
                language_id=language_id, text_type_id=text_type_id).order_by(order_by)
        else:
            list_text = TblText.objects.filter(
                language_id=language_id, text_type_id=text_type_id, user_id=request.user.id_user).order_by(order_by)

        list_text_and_user = []
        for text in list_text:
            user = TblUser.objects.filter(id_user=text.user_id).first()
            if user.name == 'empty':
                list_text_and_user.append([text, ''])
            else:
                list_text_and_user.append(
                    [text, user.last_name + ' ' + user.name])
        return (render(request, "corpus.html", context={'work_with_file': True, 'list_text_and_user': list_text_and_user, 'language_selected': language, 'form_search': form_search, 'order_by': order_by, 'reverse': not reverse, 'all_students': all_students}))

    return (render(request, "corpus.html", context={'text_html': '<div id = "Text_found_err">404 Not Found<\div>'}))


def corpus_search(request):
    try:
        order_by = request.GET['order_by']
        # Covert reverse str to bool
        reverse = (request.GET['reverse'] == 'True')

        if reverse:
            order_by = '-' + order_by
    except:
        order_by = 'header'
        reverse = False

    if request.POST:
        form_search = SearchTextForm(request.POST)
        # Entry.objects.all().filter(pub_date__year=2006)
        filters = Q()
        if form_search.data['header']:
            filters &= Q(header=form_search.data['header'])
        if form_search.data['user']:
            filters &= Q(user_id=form_search.data['user'])
        if form_search.data['language']:
            filters &= Q(language_id=form_search.data['language'])
        if form_search.data['text_type']:
            filters &= Q(text_type_id=form_search.data['text_type'])
        if form_search.data['create_date']:
            filters &= Q(create_date=form_search.data['create_date'])
        if form_search.data['modified_date']:
            filters &= Q(modified_date=form_search.data['modified_date'])
        if form_search.data['pos_check']:
            filters &= Q(pos_check=form_search.data['pos_check'])
        if form_search.data['error_tag_check']:
            filters &= Q(error_tag_check=form_search.data['error_tag_check'])
        if form_search.data['emotional']:
            filters &= Q(emotional=form_search.data['emotional'])
        if form_search.data['write_place']:
            filters &= Q(write_place=form_search.data['write_place'])

        list_text = TblText.objects.filter(filters).order_by(order_by)

    else:
        form_search = SearchTextForm()
        return (render(request, "corpus_search.html", context={'form_search': form_search}))

    return (render(request, "corpus_search.html", context={'form_search': form_search, 'list_text': list_text, 'order_by': order_by, 'reverse': not reverse}))


def new_text(request, language=None, text_type=None):

    # Проверка на выбранный язык и тип текста
    if language != None and text_type != None:

        language_object = TblLanguage.objects.filter(language_name=language)
        if len(language_object) != 0:
            language_id = language_object[0].id_language
        else:
            return render(request, 'corpus.html')

        text_type_objects = TblTextType.objects.filter(
            language_id=language_id, text_type_name=text_type)
        if len(text_type_objects) == 0:
            return render(request, 'corpus.html')
    else:
        return render(request, 'corpus.html')

    if request.method == 'POST':
        from nltk.tokenize import sent_tokenize, word_tokenize
        if not request.user.is_authenticated:
            return redirect('home')
        elif request.user.is_teacher():
            custom_user = TblUser.objects.filter(
                id_user=request.POST['student']).first()
        else:
            custom_user = request.user

        student = TblStudent.objects.filter(
            user_id=custom_user.id_user).first()
        groups = TblStudentGroup.objects.filter(
            student_id=student.id_student).values_list('group_id', flat=True)

        student_groups = TblGroup.objects.filter(id_group__in=groups)

        form_text = TextCreationForm(
            custom_user, language_object[0], text_type_objects[0], data=request.POST)

        if form_text.is_valid():
            text = form_text.save(commit=False)
            # print(text)
            text.modified_date = text.create_date
            text = text.save()
            # print(text)

            textgroup = TblTextGroup(
                group_id=request.POST['student_group'],
                text_id=text.id_text
            )
            textgroup.save()

            count_sent = 0
            for sent in sent_tokenize(text.text):
                sent_object = TblSentence(
                    text_id=text,
                    text=sent,
                    order_number=count_sent
                )
                sent_object.save()
                count_sent += 1

                count_token = 0
                for token in word_tokenize(sent):
                    token_object = TblToken(
                        sentence_id=sent_object.id_sentence,
                        text=token,
                        order_number=count_token
                    )
                    token_object.save()

                    count_token += 1

            # log_text('create', request.user, text.header, text.user_id, language, text_type)

            return redirect('text_type', language=language, text_type=text_type)
        else:
            # print(form_text.errors)
            pass

    else:
        custom_user = request.user
        student = TblStudent.objects.filter(
            user_id=custom_user.id_user).first()
        groups = TblStudentGroup.objects.filter(
            student_id=student.id_student).values_list('group_id', flat=True)
        student_groups = TblGroup.objects.filter(id_group__in=groups)

        form_text = TextCreationForm(
            custom_user, language_object[0], text_type_objects[0])
        return render(request, 'new_text.html', {'form_text': form_text, 'student_groups': student_groups, 'student': student})

    return render(request, 'new_text.html', {'form_text': form_text, 'student_groups': student_groups, 'student': request.POST['student']})


def delete_text(request):
    """Function for delete student's text

    Args:
        request (_type_): _description_

    Returns:
        html: redirect to back page
    """

    if not request.user.is_authenticated:
        return redirect('home')
    elif not check_is_superuser(request.user.id_user):
        return redirect('home')
    
    print('1111')

    if request.method == 'POST':
        print('2222')
        language = request.POST['language']
        text_type = request.POST['text_type']
        text_id = request.POST['text_id']

        TblTokenMarkup.objects.filter(
            token_id__sentence_id__text_id=text_id).delete()
        TblMarkup.objects.filter(
            token_id__sentence_id__text_id=text_id).delete()
        TblToken.objects.filter(sentence_id__text_id=text_id).delete()
        TblSentence.objects.filter(text_id=text_id).delete()
        TblTextGroup.objects.filter(text_id=text_id).delete()
        TblText.objects.filter(id_text=text_id).delete()

    return redirect('text_type', language=language, text_type=text_type)


def _drop_none(info_dict: dict, ignore: list):
    result = {}
    for key in info_dict.keys():
        if key not in ignore and \
                (info_dict[key] == None or (type(info_dict[key]) == int and info_dict[key] < 0)):

            result[key] = 'Не указано'
        else:
            result[key] = info_dict[key]
    return (result)


def _get_text_info(text_id: int):
    '''
    Function for getting meta information

    params:
    text_id (int) -- id of current text

    return:
    dict of metatags 
    '''
    raw_info = TblText.objects.filter(id_text=text_id).values(
        'header',
        'user_id',
        'user_id__name',
        'user_id__last_name',
        'user_id__login',
        'creation_course',
        'create_date',
        'text_type_id__text_type_name',
        'emotional_id__emotional_name',
        'write_tool_id__write_tool_name',
        'write_place_id__write_place_name',
        'education_level',
        'self_rating',
        'student_assesment',
        'assessment',
        'completeness',
        'structure',
        'coherence',
        'teacher_id__user_id__name',
        'teacher_id__user_id__last_name',
        'pos_check',
        'pos_check_user_id__name',
        'pos_check_user_id__last_name',
        'error_tag_check',
        'error_tag_check_user_id__name',
        'error_tag_check_user_id__last_name'
    ).all()[0]

    group_number = TblTextGroup.objects.filter(text_id=text_id)

    if group_number.exists():
        group_number = group_number.values(
            'group_id__group_name', 'group_id__enrollement_date')[0]
        group_number = group_number['group_id__group_name']+' ('\
            + str(group_number['group_id__enrollement_date'].year)+' / ' +\
            str(group_number['group_id__enrollement_date'].year+1)+')'

    else:
        group_number = 'Отсутствует'

    raw_info = _drop_none(
        raw_info, ['assessment', 'pos_check', 'error_tag_check'])

    raw_info['assessment'] = False if not raw_info['assessment']\
        or raw_info['assessment'] not in ASSESSMENT_CHOICES.keys() else ASSESSMENT_CHOICES[raw_info['assessment']]

    raw_info['completeness'] = 'Не указано' if not raw_info['completeness']\
        or raw_info['completeness'] not in ASSESSMENT_CHOICES.keys() else ASSESSMENT_CHOICES[raw_info['completeness']]

    raw_info['structure'] = 'Не указано' if not raw_info['structure']\
        or raw_info['structure'] not in ASSESSMENT_CHOICES.keys() else ASSESSMENT_CHOICES[raw_info['structure']]

    raw_info['coherence'] = 'Не указано' if not raw_info['coherence']\
        or raw_info['coherence'] not in ASSESSMENT_CHOICES.keys() else ASSESSMENT_CHOICES[raw_info['coherence']]

    assessment_name = str(raw_info['teacher_id__user_id__name']) + ' ' +\
        str(raw_info['teacher_id__user_id__last_name'])
    assessment_name = 'Не указано' if assessment_name == 'Не указано Не указано' else assessment_name

    pos_name = str(raw_info['pos_check_user_id__name']) + ' ' +\
        str(raw_info['pos_check_user_id__last_name'])
    pos_name = 'Не указано' if pos_name == 'Не указано Не указано' else pos_name

    error_name = str(raw_info['error_tag_check_user_id__name']) + ' ' +\
        str(raw_info['error_tag_check_user_id__last_name'])
    error_name = 'Не указано' if error_name == 'Не указано Не указано' else error_name

    return ({

        # Информация о тексте
        'text_name': raw_info['header'],
        'text_type': raw_info['text_type_id__text_type_name'],
        'course': raw_info['creation_course'],
        'create_date': raw_info['create_date'],

        # Информация об авторе

        'author_name':
            str(raw_info['user_id__name']) + '  '
            + str(raw_info['user_id__last_name'])
            + ' ('+str(raw_info['user_id__login'])+')',
        'group_number': group_number,

        # Мета. информация
        'emotional': raw_info['emotional_id__emotional_name'],
        'write_tool': raw_info['write_tool_id__write_tool_name'],
        'write_place': raw_info['write_place_id__write_place_name'],
        'education_level': raw_info['education_level'],
        'self_rating': raw_info['self_rating'],
        'student_assessment': raw_info['student_assesment'],

        # Оценка работы
        'assessment': raw_info['assessment'],
        'completeness': raw_info['completeness'],
        'structure': raw_info['structure'],
        'coherence': raw_info['coherence'],
        'teacher_name': assessment_name,

        'pos_check': raw_info['pos_check'],
        'pos_check_name': pos_name,

        'error_check': raw_info['error_tag_check'],
        'error_check_name': error_name

    })


# Form for assessments modify proccesing
def assessment_form(request, text_id=1, **kwargs):
    if check_permissions_work_with_annotations(request.user.id_user, text_id):

        initial_values = TblText.objects.filter(id_text=text_id).values(
            'assessment',
            'completeness',
            'structure',
            'coherence',
            'pos_check',
            'error_tag_check').all()[0]

        if request.method == "POST":
            # instance = get_object_or_404(TblText, id_text = text_id)
            instance = TblText.objects.get(id_text=text_id)
            form = AssessmentModify(initial_values, request.user.is_teacher(),
                                    request.POST or None,
                                    instance=instance)

            if form.is_valid():
                assessment = form.cleaned_data['assessment']
                completeness = form.cleaned_data['completeness']
                structure = form.cleaned_data['structure']
                coherence = form.cleaned_data['coherence']

                pos_check = form.cleaned_data['pos_check']
                error_tag_check = form.cleaned_data['error_tag_check']

                if assessment != initial_values['assessment'] and request.user.is_teacher():
                    teacher_id = TblTeacher.objects.get(
                        user_id=request.user.id_user)
                    form.instance.teacher = teacher_id

                if completeness != initial_values['completeness'] and request.user.is_teacher():
                    teacher_id = TblTeacher.objects.get(
                        user_id=request.user.id_user)
                    form.instance.teacher = teacher_id

                if structure != initial_values['structure'] and request.user.is_teacher():
                    teacher_id = TblTeacher.objects.get(
                        user_id=request.user.id_user)
                    form.instance.teacher = teacher_id

                if coherence != initial_values['coherence'] and request.user.is_teacher():
                    teacher_id = TblTeacher.objects.get(
                        user_id=request.user.id_user)
                    form.instance.teacher = teacher_id

                if pos_check != initial_values['pos_check']:
                    form.instance.pos_check_user = TblUser.objects.get(
                        id_user=request.user.id_user)
                    form.instance.pos_check_date = datetime.date.today()  # .strftime('%Y-%M-%d')

                if error_tag_check != initial_values['error_tag_check']:
                    form.instance.error_tag_check_user = TblUser.objects.get(
                        id_user=request.user.id_user)
                    form.instance.error_tag_check_date = datetime.date.today()  # .strftime('%Y-%M-%d')

                form.save()
            return (redirect(request.path[:request.path.rfind('/')+1]))
        else:
            form = AssessmentModify(initial_values, request.user.is_teacher())
            return (render(request, 'assessment_form.html', {
                'right': True,
                'form': form
            }))

    else:
        return (render(request, 'assessment_form.html', {'right': False}))

# Form for meta modify


def meta_form(request, text_id=1, **kwargs):
    if request.user.id_user == TblText.objects\
            .filter(id_text=text_id).values('user_id')[0]['user_id']:

        initial_values = TblText.objects.filter(id_text=text_id).values(
            'emotional',
            'write_tool',
            'write_place',
            'education_level',
            'self_rating',
            'student_assesment').all()[0]

        if request.method == "POST":
            # instance = get_object_or_404(TblText, id_text = text_id)
            instance = TblText.objects.get(id_text=text_id)
            form = MetaModify(initial_values,
                              request.POST or None,
                              instance=instance)

            if form.is_valid():
                form.save()
            return (redirect(request.path[:request.path.rfind('/')+1]))
        else:
            form = MetaModify(initial_values)
            return (render(request, 'meta_form.html', {
                'right': True,
                'form': form
            }))
    else:
        return render(request, 'meta_form.html', {'right': False})

def show_text(request, text_id=1, language=None, text_type=None):
    if not hasattr(request.user, 'id_user'):
        return redirect('login')

    text_info = TblText.objects.filter(id_text=text_id).values(
        'header', 'language_id', 'language_id__language_name', 'user_id').all()
    if text_info.exists() and check_permissions_show_text(request.user.id_user, text_id):
        header = text_info[0]['header']
        text_language_name = text_info[0]['language_id__language_name']
        text_language = text_info[0]['language_id']
        tags = TblTag.objects.filter(tag_language_id=text_language).values(
            'id_tag', 'tag_text', 'tag_text_russian', 'tag_parent', 'tag_color').all()
        tags_info = []
        if tags.exists():
            for element in tags:
                parent_id = 0
                if element['tag_parent'] and element['tag_parent'] > 0:
                    parent_id = element['tag_parent']
                spoiler = False
                for child in tags:
                    if element['id_tag'] == child['tag_parent']:
                        spoiler = True
                        break
                tags_info.append({
                    'isspoiler': spoiler,
                    'tag_id': element['id_tag'],
                    'tag_text': element['tag_text'],
                    'tag_text_russian': element['tag_text_russian'],
                    'parent_id': parent_id,
                    'tag_color': element['tag_color']
                })

        reasons = TblReason.objects.filter(
            reason_language_id=text_language).values('id_reason', 'reason_name')
        grades = TblGrade.objects.filter(
            grade_language_id=text_language).values('id_grade', 'grade_name')
        annotation_form = get_annotation_form(grades, reasons)

        ann_right = check_permissions_work_with_annotations(
            request.user.id_user, text_id)
        text_owner = True if request.user.id_user == text_info[0]['user_id'] else False

        text_meta_info = _get_text_info(text_id)

        if request.user.is_teacher() and text_language == 1:
            cursor = connection.cursor()
            cursor.execute(
                f'CALL getallMarks({text_id}, @g0, @g1, @g2, @mg, @l0, @l1, @l2, @ml, @p0, @p1, @p2, @mp, @dis, @skip, @extra);')
            cursor.execute(
                "SELECT @g0, @g1, @g2, @mg, @l0, @l1, @l2, @ml, @p0, @p1, @p2, @mp, @dis, @skip, @extra;")
            auto_degree = cursor.fetchone()
            grammatik = auto_degree[0:4]
            lexik = auto_degree[4:8]
            orth = auto_degree[8:12]
            dis = auto_degree[12]
            skip = auto_degree[13]
            extra = auto_degree[14]
            cursor.close()

        if request.user.is_teacher() and text_language == 1:
            return render(request, "work_area.html", context={
                'founded': True,
                'ann_right': ann_right,
                'teacher': request.user.is_teacher(),
                'superuser': check_is_superuser(request.user.id_user),
                'text_owner': text_owner,
                'user_id': request.user.id_user,
                'annotation_form': annotation_form,
                'text_id': text_id,
                'lang_name': text_language_name,
                'text_info': text_meta_info,
                'auto_degree': True,
                'auto_grammatik': grammatik,
                'auto_lexik': lexik,
                'count_dis': dis,
                'count_skip': skip,
                'count_extra': extra,
                'auto_orth': orth,
                'language': language,
                'text_type': text_type,
            })

        else:
            return render(request, "work_area.html", context={
                'founded': True,
                'ann_right': ann_right,
                'teacher': request.user.is_teacher(),
                'superuser': check_is_superuser(request.user.id_user),
                'text_owner': text_owner,
                'user_id': request.user.id_user,
                'annotation_form': annotation_form,
                'text_id': text_id,
                'lang_name': text_language_name,
                'text_info': text_meta_info,
                'auto_degree': False,
                'language': language,
                'text_type': text_type,
            })
    else:
        return render(request, 'work_area.html', context={'founded': False})


def author_form(request, text_id=1, **kwargs):
    url = request.get_full_path()
    go_back_url = url[:url.rfind('/')]

    no_error = True
    is_student = True
    right = True

    options = []
    initial = ()
    current_group = TblTextGroup.objects.filter(text_id=text_id)

    creator = TblText.objects.filter(id_text=text_id).all()

    if request.user.is_teacher():
        labels = TblStudentGroup.objects.all().filter(student_id__user_id__language_id=request.user.language_id)\
            .order_by(
                'student_id__user_id__last_name',
                'student_id__user_id__name',
                'student_id__user_id__patronymic',
                'group_id__group_name',
                '-group_id__enrollement_date'
        )\
            .values(
            'student_id__user_id',
            'group_id',
            'student_id__user_id__login',
            'student_id__user_id__last_name',
            'student_id__user_id__name',
            'student_id__user_id__patronymic',
            'group_id__group_name',
            'group_id__enrollement_date'
        )
        if labels.exists():
            for label in labels:
                options.append(
                    (str(label['student_id__user_id'])+' '+str(label['group_id']),
                     str(label['student_id__user_id__last_name'])+' ' +
                     str(label['student_id__user_id__name'])+' ' +
                     str(label['student_id__user_id__patronymic'])+' Логин: ' +
                     str(label['student_id__user_id__login'])+' Группа: ' +
                     str(label['group_id__group_name']) + ' (' +
                     str(label['group_id__enrollement_date'].year)+')')
                )
        else:
            no_error = False

        if creator.exists() and current_group.exists():
            student_id = TblStudent.objects.filter(
                user_id=creator.values('user_id')[0]['user_id'])

            if student_id.exists():
                student_id = student_id.values(
                    'user_id', 'user_id__login', 'user_id__last_name', 'user_id__name', 'user_id__patronymic')[0]
                current_group = current_group.values(
                    'group_id',
                    'group_id__group_name',
                    'group_id__enrollement_date')[0]

                initial = (str(student_id['user_id'])+' '
                           + str(current_group['group_id']),
                           str(student_id['user_id__last_name'])+' ' +
                           str(student_id['user_id__name'])+' ' +
                           str(student_id['user_id__patronymic'])+' Логин: ' +
                           str(student_id['user_id__login'])+' Группа: ' +
                           str(current_group['group_id__group_name']) + ' (' +
                           str(current_group['group_id__enrollement_date'].year)+')'
                           )
            else:
                initial = ('   ', 'Отсутствует')
        else:
            initial = ('   ', 'Отсутствует')

    elif creator.exists() and creator.values('user_id')[0]['user_id'] == request.user.id_user:
        student_id = TblStudent.objects.filter(
            user_id=creator.values('user_id')[0]['user_id'])

        if student_id.exists():
            labels = TblStudentGroup.objects.\
                filter(student_id=student_id.values('id_student')[0]['id_student']).\
                order_by('group_id__group_name', '-group_id__enrollement_date').\
                values('group_id', 'group_id__group_name',
                       'group_id__enrollement_date')

            if labels.exists():
                for label in labels:
                    options.append((
                        label['group_id'],
                        str(label['group_id__group_name'])+' '
                        + str(label['group_id__enrollement_date'].year)
                    ))
            else:
                no_error = False

            if current_group.exists():
                current_group = current_group.values(
                    'group_id', 'group_id__group_name', 'group_id__enrollement_date')[0]
                initial = (str(current_group['group_id']),
                           str(current_group['group_id__group_name'])+' '
                           + str(current_group['group_id__enrollement_date'].year))
            else:
                initial = (' ', 'Отсутствует')

        else:
            is_student = False
    else:
        right = False

    if request.method != 'POST':
        return (render(request, 'author_modify.html', context={
            'right': right,
            'no_error': no_error,
            'is_student': is_student,
            'is_teacher': request.user.is_teacher(),
            'form': AuthorModify(options, initial),
            'go_back': go_back_url,
        }))

    else:
        form = AuthorModify(options, initial, request.POST or None)
        if form.is_valid():
            value = form.cleaned_data['user']

            if request.user.is_teacher():
                if value and ' ' in value\
                        and value.split(' ')[0].isnumeric()\
                        and value.split(' ')[1].isnumeric():

                    user_id = int(value.split(' ')[0])
                    group_id = int(value.split(' ')[1])

                    text = TblText.objects.get(id_text=text_id)
                    text.user_id = user_id
                    text.save()

                    group = TblTextGroup.objects.filter(text_id=text_id)

                    if group.exists():
                        group = TblTextGroup.objects.get(text_id=text_id)
                        group.group_id = group_id
                        group.save()

                    else:
                        group = TblTextGroup(
                            text_id=text_id, group_id=group_id)
                        group.save()
                else:
                    no_error = False

            elif creator.exists() and creator.values('user_id')[0]['user_id'] == request.user.id_user:
                if value.isnumeric():
                    group_id = int(value)

                    group = TblTextGroup.objects.filter(text_id=text_id)
                    if group.exists():
                        group = TblTextGroup.objects.get(text_id=text_id)
                        group.group_id = group_id
                        group.save()
                    else:
                        group = TblTextGroup(
                            text_id=text_id, group_id=group_id)
                        group.save()
                else:
                    no_error = False
            else:
                right = False
        else:
            no_error = False

        return (render(request, 'author_modify.html', context={
            'right': right,
            'no_error': no_error,
            'is_student': is_student,
            'is_teacher': request.user.is_teacher(),
            'form': AuthorModify(options, initial),
            'go_back': go_back_url,
        }))


def show_raw(request, text_id: int, **kwargs):
    author_id = TblText.objects.filter(id_text=text_id).values(
        'user_id',
        'language_id__language_name',
        'text_type_id__text_type_name',
        'header').all()
    output = []
    right = True
    language = ''
    text_type = ''
    header = ''

    if author_id.exists() and (request.user.is_teacher() or request.user.id_user == author_id[0]['user_id']):
        sentences = TblSentence.objects\
            .filter(text_id=text_id)\
            .order_by('order_number')\
            .values('text').all()
        language = author_id[0]['language_id__language_name']
        text_type = author_id[0]['text_type_id__text_type_name']
        header = author_id[0]['header']
        if sentences.exists():
            output = [
                [i+1, sentence['text'].replace('-EMPTY-', '')] for i, sentence in enumerate(sentences)]
    else:
        right = False

    return (render(request, 'raw_text_show.html', context={
        'right': right,
        'sentences': output,
        'lang_name': language,
        'text_type': text_type,
        'text_name': header
    }))
