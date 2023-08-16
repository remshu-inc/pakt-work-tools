# from django.views import generic
# from .models import TblText
import datetime
import os

from django.core.exceptions import FieldError
from django.db import connection
from django.db.models import Q
from django.shortcuts import render, redirect

from right_app.views import check_permissions_work_with_annotations, check_permissions_show_text, \
	check_is_superuser
from text_app.models import TblTextGroup
from user_app.models import TblLanguage, TblTeacher, TblUser, TblStudent, TblGroup, TblStudentGroup
from .forms import TextCreationForm, get_annotation_form, SearchTextForm, AssessmentModify, MetaModify, AuthorModify
from .models import TblReason, TblGrade, TblTextType, TblText, TblSentence, TblMarkup, TblTag, \
	TblTokenMarkup, TblToken
from nltk.tokenize import sent_tokenize, word_tokenize

os.environ['NLTK_DATA'] = '/var/www/lingo/nltk_data'

ASSESSMENT_CHOICES = {TblText.TASK_RATES[i][0]: TblText.TASK_RATES[i][1]
					  for i in range(len(TblText.TASK_RATES))}

def corpus(request, language=None, text_type=None):
	if not request.user.is_authenticated:
		return redirect('login')
	
	is_teacher = request.user.is_teacher()
	search_form = SearchTextForm(language_id=request.user.language_id) if is_teacher else None

	# Определение сортировки
	order = None
	reverse = False

	if request.GET:
		order = request.GET.get('order_by', None)
		reverse = (request.GET.get('reverse', False) == 'True')

		if reverse and not (order is None):
			order = '-' + order

	context={'is_teacher': is_teacher, 'search_form': search_form, 'reverse': reverse, 'order_by': order}

	#  Language choice
	if language is None:
		if order is None:
			order='language_name'
			context['order_by'] = order

		languages = TblLanguage.objects.all().order_by(order)

		context['content']='languages'
		context['languages'] = languages
		return render(request, "corpus.html", context=context)
	
	language_object = TblLanguage.objects.filter(language_name=language)
	if not language_object.exists():
			context['content'] = 'error'
			context['error_message'] = 'Язык ' + language + ' не найден'
			return render(request, "corpus.html", context=context)
	language_object = language_object.first()

	language_id = language_object.id_language
	context['selected_language']=language_object.language_name
	

	# Text type choice
	if text_type is None:
		if order is None:
			order='text_type_name'
			context['order_by'] = order

		text_types = TblTextType.objects.filter(language_id=language_id).order_by(order)
		context['content']='text_types'
		context['text_types']=text_types
		return render(request, "corpus.html", context=context)

	text_type_object = TblTextType.objects.filter(
	 		language_id=language_id, text_type_name=text_type)
	if not text_type_object.exists():
		context['content'] = 'error'
		context['error_message'] = 'Тип текста ' + text_type + ' не найден'
		return render(request, "corpus.html", context=context)
	text_type_object = text_type_object.first()
	text_type_id = text_type_object.id_text_type
	context['selected_text_type']=text_type_object.text_type_name


	# Text choice
	texts = TblText.objects.filter(language_id=language_id, text_type_id=text_type_id)
	if not check_permissions_show_text(request.user.id_user):
		texts = texts.filter(user_id=request.user.id_user)
	
	if order is None:
			order='modified_date'
			context['order_by'] = order
	texts = texts.order_by(order)

	text_user_list = []
	for text in texts:
		user = TblUser.objects.filter(id_user=text.user_id).first()
		text_user_list.append({
			'text': text,
			'author_name': user.last_name + ' ' + user.name + ((' ' + user.patronymic) if user.patronymic else ''),
			'author_login': user.login
		})
	
	context['content'] = 'texts'
	context['text_list'] = text_user_list

	return render(request, "corpus.html", context=context)


def corpus_search(request):
	if not (request.user.is_authenticated and request.user.is_teacher()):
		return render(request, 'access_denied.html', status=403)
	
	order = 'header'
	reverse = False

	if request.GET:
		order = request.GET.get('order_by', 'header')
		reverse = (request.GET.get('reverse', False) == 'True')

		if reverse and not (order is None):
			order = '-' + order

	text_list = TblText.objects.all().order_by(order)

	if request.POST:
		search_form = SearchTextForm(request.user.language_id, request.POST)
		filters = Q()

		if search_form.data['header']:
			filters &= Q(header__icontains=search_form.data['header'])
		if search_form.data['user']:
			filters &= Q(user_id=search_form.data['user'])
		if search_form.data['language']:
			filters &= Q(language_id=search_form.data['language'])
		if search_form.data['create_date']:
			filters &= Q(create_date=search_form.data['create_date'])
		if search_form.data['error_tag_check']:
			filters &= Q(error_tag_check=search_form.data['error_tag_check'])
		if search_form.data['emotional']:
			filters &= Q(emotional=search_form.data['emotional'])
		if search_form.data['write_place']:
			filters &= Q(write_place=search_form.data['write_place'])
		if search_form.data['text_type']:
			text_type_ids = TblTextType.objects.filter(text_type_name=search_form.data['text_type']).values('id_text_type')
			filters &= Q(text_type_id__in=text_type_ids)

		text_list = text_list.filter(filters)

	else:
		search_form = SearchTextForm(language_id=request.user.language_id)

	return (render(request, "corpus_search.html",
				   context={'search_form': search_form, 'text_list': text_list, 'reverse': reverse, 'order_by': order}))



def new_text(request):
	if not (request.user.is_authenticated and (request.user.is_teacher() or request.user.is_student())):
		return render(request, 'access_denied.html', status=403)

	text_form = TextCreationForm(request.user)

	if request.method == 'POST':
		text_form = TextCreationForm(request.user, request.POST)

		group = request.POST['group']
		if (group is None) or (group == '-1'):
			text_form.add_error('group', 'Выберите группу')

		if text_form.is_valid():
			text_type_name = text_form.cleaned_data['text_type']
			text_type = TblTextType.objects.filter(text_type_name=text_type_name).first()
			text = text_form.save(commit=False)
			text.text_type_id = text_type.id_text_type
			text = text.save()

			group = text_form.cleaned_data['group']
			textgroup = TblTextGroup(
				group_id=group,
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

			return redirect('tasks_info', user_id=text.user_id)
		
	language = TblLanguage.objects.filter(id_language=request.user.language_id).values_list('language_name', flat=True).first()

	return render(request, 'new_text.html', {'form_text': text_form, 'is_teacher': request.user.is_teacher(), 'language': language})


def delete_text(request):
	"""Function for delete student's text

	Args:
		request (_type_): _description_

	Returns:
		html: redirect to back page
	"""

	if not (request.user.is_authenticated and check_is_superuser(request.user.id_user)):
		return render(request, 'access_denied.html', status=403)

	if request.method == 'POST':
		text_id = request.POST['text_id']

		TblTokenMarkup.objects.filter(
			token_id__sentence_id__text_id=text_id).delete()
		TblMarkup.objects.filter(
			token_id__sentence_id__text_id=text_id).delete()
		TblToken.objects.filter(sentence_id__text_id=text_id).delete()
		TblSentence.objects.filter(text_id=text_id).delete()
		TblTextGroup.objects.filter(text_id=text_id).delete()
		TblText.objects.filter(id_text=text_id).delete()

	return redirect('corpus')


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
			'group_id__group_name', 'group_id__enrollment_date')[0]
		group_number = group_number['group_id__group_name'] + ' (' \
					   + str(group_number['group_id__enrollment_date'].year) + ' / ' + \
					   str(group_number['group_id__enrollment_date'].year + 1) + ')'

	else:
		group_number = 'Отсутствует'

	raw_info = _drop_none(
		raw_info, ['assessment', 'pos_check', 'error_tag_check'])

	raw_info['assessment'] = False if not raw_info['assessment'] \
									  or raw_info['assessment'] not in ASSESSMENT_CHOICES.keys() else \
	ASSESSMENT_CHOICES[raw_info['assessment']]

	raw_info['completeness'] = 'Не указано' if not raw_info['completeness'] \
											   or raw_info['completeness'] not in ASSESSMENT_CHOICES.keys() else \
	ASSESSMENT_CHOICES[raw_info['completeness']]

	raw_info['structure'] = 'Не указано' if not raw_info['structure'] \
											or raw_info['structure'] not in ASSESSMENT_CHOICES.keys() else \
	ASSESSMENT_CHOICES[raw_info['structure']]

	raw_info['coherence'] = 'Не указано' if not raw_info['coherence'] \
											or raw_info['coherence'] not in ASSESSMENT_CHOICES.keys() else \
	ASSESSMENT_CHOICES[raw_info['coherence']]

	assessment_name = str(raw_info['teacher_id__user_id__name']) + ' ' + \
					  str(raw_info['teacher_id__user_id__last_name'])
	assessment_name = 'Не указано' if assessment_name == 'Не указано Не указано' else assessment_name

	pos_name = str(raw_info['pos_check_user_id__name']) + ' ' + \
			   str(raw_info['pos_check_user_id__last_name'])
	pos_name = 'Не указано' if pos_name == 'Не указано Не указано' else pos_name

	error_name = str(raw_info['error_tag_check_user_id__name']) + ' ' + \
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
			+ ' (' + str(raw_info['user_id__login']) + ')',
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
def assessment_form(request, text_id):
	if check_permissions_work_with_annotations(request.user.id_user, text_id):

		initial_values = TblText.objects.filter(id_text=text_id).values(
			'assessment',
			'completeness',
			'structure',
			'coherence',
			'pos_check',
			'error_tag_check',
			'teacher',
			'error_tag_check_user',
			'pos_check_user',
			'pos_check_date',
			'error_tag_check_date').first()

		instance = TblText.objects.get(id_text=text_id)

		if request.method == "POST":
			form = AssessmentModify(initial_values, request.user.is_teacher(),
									request.POST or None,
									instance=instance)

			if form.is_valid():
				if (initial_values['teacher']):
					form.instance.teacher = TblTeacher.objects.get(id_teacher=initial_values['teacher'])
				if (initial_values['error_tag_check_user']):
					form.instance.error_tag_check_user = TblUser.objects.get(id_user=initial_values['error_tag_check_user'])	
				if (initial_values['pos_check_user']):
					form.instance.pos_check_user = TblUser.objects.get(id_user=initial_values['pos_check_user'])	
			
				assessment = form.cleaned_data['assessment']
				completeness = form.cleaned_data['completeness']
				structure = form.cleaned_data['structure']
				coherence = form.cleaned_data['coherence']

				pos_check = form.cleaned_data['pos_check']
				error_tag_check = form.cleaned_data['error_tag_check']

				if request.user.is_teacher() and (
						assessment != initial_values['assessment'] or
						completeness != initial_values['completeness'] or
						structure != initial_values['structure'] or
						coherence != initial_values['coherence']):
					teacher = TblTeacher.objects.get(user_id=request.user.id_user)
					form.instance.teacher = teacher

				if pos_check != initial_values['pos_check']:
					form.instance.pos_check_user = TblUser.objects.get(id_user=request.user.id_user)
					form.instance.pos_check_date = datetime.date.today()  # .strftime('%Y-%M-%d')
				else:
					form.instance.pos_check_user = instance.pos_check_user
					form.instance.pos_check_date = instance.pos_check_date

				if error_tag_check != initial_values['error_tag_check']:
					form.instance.error_tag_check_user = TblUser.objects.get(id_user=request.user.id_user)
					form.instance.error_tag_check_date = datetime.date.today()  # .strftime('%Y-%M-%d')
				else:
					form.instance.error_tag_check_user = instance.error_tag_check_user
					form.instance.error_tag_check_date = instance.error_tag_check_date

				form.save()

			return (redirect(show_text, text_id))
		else:
			form = AssessmentModify(initial_values, request.user.is_teacher())
			return (render(request, 'assessment_form.html', {
				'form': form
			}))

	else:
		return render(request, 'access_denied.html', status=403)


# Form for meta modify
def meta_form(request, text_id):
	if request.user.id_user == TblText.objects.filter(id_text=text_id).values('user_id').first()['user_id']:
		initial_values = TblText.objects.filter(id_text=text_id).values(
			'emotional',
			'write_tool',
			'write_place',
			'education_level',
			'self_rating',
			'student_assesment').first()

		if request.method == "POST":
			instance = TblText.objects.get(id_text=text_id)
			form = MetaModify(initial_values,
							  request.POST or None,
							  instance=instance)

			if form.is_valid():
				education_level = form.cleaned_data['education_level']
				if (education_level and (education_level < 0 or education_level > 100)):
					form.add_error('education_level', 'Некорректное значение')
				else:
					form.save()
					return (redirect(show_text, text_id))
		else:
			form = MetaModify(initial_values)

		return (render(request, 'meta_form.html', {
			'form': form
		}))
	else:
		return render(request, 'access_denied.html', status=403)


def show_text_legacy(request, text_id):
	if not request.user.is_authenticated:
		return redirect('login')

	text = TblText.objects.filter(id_text=text_id).first()
	language = TblLanguage.objects.filter(id_language=text.language_id).first()
	text_type = TblTextType.objects.filter(id_text_type=text.text_type_id).first()

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

def show_text(request, text_id):
	if not request.user.is_authenticated:
		return redirect('login')

	text = TblText.objects.filter(id_text=text_id).values('language_id', 'text_type_id', 'user_id')
	if not text.exists():
		return render(request, 'work_area.html', context={ 'exists': False })
	
	text = text.first()
	
	if not check_permissions_show_text(request.user.id_user, text_id):
		return render(request, 'access_denied.html', status=403)

	language = TblLanguage.objects.filter(id_language=text['language_id']).first()
	text_type = TblTextType.objects.filter(id_text_type=text['text_type_id']).first()
	tags = TblTag.objects.filter(tag_language_id=language.id_language).values('id_tag', 'tag_text', 'tag_text_russian', 'tag_parent', 'tag_color').all()

	tags_info = []
	if tags.exists():
			for element in tags:
				parent_id = 0
				if element['tag_parent'] and element['tag_parent'] != 0:
					parent_id = element['tag_parent']
				
				spoiler = False
				for child in tags:
					if child['tag_parent'] == element['id_tag']:
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

	reasons = TblReason.objects.filter(reason_language_id=language.id_language).values('id_reason', 'reason_name')
	grades = TblGrade.objects.filter(grade_language_id=language.id_language).values('id_grade', 'grade_name')
	annotation_form = get_annotation_form(grades, reasons)

	annotation_right = check_permissions_work_with_annotations(request.user.id_user, text_id)
	text_owner_right = request.user.id_user == text['user_id']

	text_meta_info = _get_text_info(text_id)

	context = {
		'exists': True,
		'ann_right': annotation_right,
		'teacher': request.user.is_teacher(),
		'superuser': check_is_superuser(request.user.id_user),
		'text_owner': text_owner_right,
		'user_id': request.user.id_user,
		'annotation_form': annotation_form,
		'text_id': text_id,
		'lang_name': language.language_name,
		'text_info': text_meta_info,
		'language': language,
		'text_type': text_type,
		'auto_degree': False
	}

	if request.user.is_teacher() and language.id_language == 1:
		cursor = connection.cursor()
		cursor.execute(
			f'CALL getallMarks({text_id}, @g0, @g1, @g2, @mg, @l0, @l1, @l2, @ml, @p0, @p1, @p2, @mp, @dis, @skip, @extra);')
		cursor.execute(
			"SELECT @g0, @g1, @g2, @mg, @l0, @l1, @l2, @ml, @p0, @p1, @p2, @mp, @dis, @skip, @extra;")
		
		auto_degree = cursor.fetchone()
		context['auto_grammatik'] = auto_degree[0:4]
		context['auto_lexik'] = auto_degree[4:8]
		context['auto_orth'] = auto_degree[8:12]
		context['count_dis'] = auto_degree[12]
		context['count_skip'] = auto_degree[13]
		context['count_extra'] = auto_degree[14]
		context['auto_degree'] = True
		cursor.close()

	return render(request, 'work_area.html', context=context)

def author_form(request, text_id):
	is_student = True

	options = []
	initial = ('   ', 'Отсутствует')
	
	text = TblText.objects.filter(id_text=text_id)
	if not text.exists():
		return redirect(corpus)

	text = text.first()

	current_group = TblTextGroup.objects.filter(text_id=text_id)
	author = TblText.objects.filter(id_text=text_id)


	if request.user.is_teacher() and request.user.language_id == text.language_id:
		labels = TblStudentGroup.objects.filter(student_id__user_id__language_id=request.user.language_id) \
			.order_by(
			'student_id__user_id__last_name',
			'student_id__user_id__name',
			'student_id__user_id__patronymic',
			'group_id__group_name',
			'-group_id__enrollment_date'
		) \
			.values(
			'student_id__user_id',
			'group_id',
			'student_id__user_id__login',
			'student_id__user_id__last_name',
			'student_id__user_id__name',
			'student_id__user_id__patronymic',
			'group_id__group_name',
			'group_id__enrollment_date'
		)
		
		if labels.exists():
			for label in labels:
				options.append(
					(
						str(label['student_id__user_id']) + ' ' + str(label['group_id']), 
      					str(label['student_id__user_id__last_name']) + ' ' + str(label['student_id__user_id__name']) + ' ' +
						(str(label['student_id__user_id__patronymic']) if label['student_id__user_id__patronymic'] else '') +
						' (' + str(label['student_id__user_id__login']) + ')' +
						' Группа: ' +
						str(label['group_id__group_name']) +
						' (' + str(label['group_id__enrollment_date'].year) + ' / ' + str(label['group_id__enrollment_date'].year + 1) + ')'
					)
				)

		if author.exists() and current_group.exists():
			student = TblStudent.objects.filter(
				user_id=author.first().user_id)

			if student.exists():
				student = student.values(
					'user_id', 'user_id__login', 'user_id__last_name', 'user_id__name', 'user_id__patronymic').first()
				current_group = current_group.values(
					'group_id',
					'group_id__group_name',
					'group_id__enrollment_date')[0]

				initial = (str(student['user_id']) + ' '
						   + str(current_group['group_id']),
						   str(student['user_id__last_name']) + ' ' +
						   str(student['user_id__name']) + ' ' +
						   str(student['user_id__patronymic']) + ' (' +
						   str(student['user_id__login']) + ') Группа: ' +
						   str(current_group['group_id__group_name']) + ' (' +
						   str(current_group['group_id__enrollment_date'].year) + ' / ' + str(current_group['group_id__enrollment_date'].year + 1) + ')'
						   )

	elif author.exists() and author.first().user_id == request.user.id_user:
		student = TblStudent.objects.filter(
			user_id=author.first().user_id)

		if student.exists():
			labels = TblStudentGroup.objects. \
				filter(student_id=student.first().id_student). \
				order_by('group_id__group_name', '-group_id__enrollment_date'). \
				values('group_id', 'group_id__group_name', 'group_id__enrollment_date')

			if labels.exists():
				for label in labels:
					options.append((
						label['group_id'],
						str(label['group_id__group_name']) + ' ('
						+ str(label['group_id__enrollment_date'].year) + ' / ' + str(label['group_id__enrollment_date'].year + 1) + ')'
					))
			
			if current_group.exists():
				current_group = current_group.values(
					'group_id', 'group_id__group_name', 'group_id__enrollment_date')[0]
				initial = (str(current_group['group_id']),
						   str(current_group['group_id__group_name']) + ' ('
						   + str(current_group['group_id__enrollment_date'].year) + ' / ' + str(current_group['group_id__enrollment_date'].year + 1) + ')') 

		else:
			is_student = False
	else:
		return render(request, 'access_denied.html', status=403)


	if request.method == 'POST':
		form = AuthorModify(options, initial, request.POST or None)
		if form.is_valid():
			user_value = form.cleaned_data['user']

			if request.user.is_teacher():
				if user_value and ' ' in user_value \
						and user_value.split(' ')[0].isnumeric() \
						and user_value.split(' ')[1].isnumeric():

					user_id = int(user_value.split(' ')[0])
					group_id = int(user_value.split(' ')[1])

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

			elif author.exists() and author.first().user_id == request.user.id_user:
				if user_value.isnumeric():
					group_id = int(user_value)

					group = TblTextGroup.objects.filter(text_id=text_id)
					if group.exists():
						group = TblTextGroup.objects.get(text_id=text_id)
						group.group_id = group_id
						group.save()
					else:
						group = TblTextGroup(
							text_id=text_id, group_id=group_id)
						group.save()

			return redirect(show_text, text_id)

	return (render(request, 'author_modify.html', context={
			'author_is_student': is_student,
			'is_teacher': request.user.is_teacher(),
			'form': AuthorModify(options, initial),
		}))

def show_raw(request, text_id: int):
	if not check_permissions_show_text(request.user.id_user, text_id):
		return render(request, 'access_denied.html', status=403)
	
	text = TblText.objects.filter(id_text=text_id).values(
		'user_id',
		'language_id__language_name',
		'text_type_id__text_type_name',
		'header')
	
	context = {}

	if text.exists():
		text = text.first()
		context['exists'] = True
		context['language'] = text['language_id__language_name']
		context['text_type'] = text['text_type_id__text_type_name']
		context['header'] = text['header']

		sentences = TblSentence.objects \
			.filter(text_id=text_id) \
			.order_by('order_number') \
			.values('text')
		if sentences.exists():
			context['sentences'] = [
				[i + 1, sentence['text'].replace('-EMPTY-', '')] for i, sentence in enumerate(sentences)
			]

		author = TblUser.objects.filter(id_user=text['user_id'])
		if author.exists():
			author = author.first()
			context['author'] = author.name + " " + author.last_name
	else:
		context['exists'] = False

	return (render(request, 'raw_text_show.html', context=context))
