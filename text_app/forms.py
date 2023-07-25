'''
Project: pakt-work-tools
File name: urls.py
Description: Перечень форм для функций работы с текстами
'''

from email.policy import default
from faulthandler import disable
from django import forms
from .models import TblText, TblTextType, TblTextGroup, TblWritePlace, TblEmotional
from user_app.models import TblUser, TblStudent, TblStudentGroup, TblLanguage, TblGroup
import datetime
from right_app.views import check_permissions_new_text, check_permissions_work_with_annotations


class TextTypeChoiceField(forms.ModelChoiceField):
	'''
	Неявная форма выбора типа текста
	'''
	def label_from_instance(self, obj):
		return super().label_from_instance(obj)
		# return "TblLanguage #%s) %s" % (obj.id_language, obj.language_name)


class DateInput(forms.DateInput):
	"""
	Поле выбора даты (???)
	"""
	input_type = 'date'


# Database stores same text types for diffetent languages as different entities. This workaround is to avoid choice duplication
def distinct_text_type_name_choices():
	text_type_names = [(choice['text_type_name'], choice['text_type_name']) for choice in TblTextType.objects.values('text_type_name').distinct()]
	return text_type_names

class TextCreationForm(forms.ModelForm):
	"""
	Форма создания нового текста
	"""
	# Фиксация даты последнего изменения
	modified_date = forms.DateField(initial=datetime.date.today(), widget=forms.HiddenInput())
	create_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
	text_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=distinct_text_type_name_choices(), initial='Не указано')

	class Meta:
		"""
		Описание полей информации о тексте
		"""
		# Модель используемой таблицы БД
		model = TblText
		# Названия полей
		fields = (
			'header',
			'user',
			'create_date',
			'modified_date',
			'text',
			'creation_course',
			'language',
			'emotional',
			'write_place',
			'education_level',
			'self_rating',
			'student_assesment',
		)
		# Описание виджетов полей
		"""
			- Формат выбора пользователя определяется при инициализации 
			родительского класса
			- Выбор языка и типа текста происходит на основе скрытых полей
			(значения для них передается в URL запроса)
		"""
		widgets   = {
			'header': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
			'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 14}),
			'emotional': forms.Select(attrs={'class': 'form-control'}),
			'write_place': forms.Select(attrs={'class': 'form-control'}),
			'education_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '200'}),
			'self_rating': forms.Select(attrs={'class': 'form-control'}),
			'student_assesment': forms.Select(attrs={'class': 'form-control'}),
			'creation_course': forms.Select(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
		}

		error_messages = {
			'header': {
				'required': 'Введите название текста'
			},
			
			'text': {
				'required': 'Введите текст'
			},
			
			'creation_course': {
				'required': 'Выберите номер курса'
			}
		}


	def __init__(self, user=None, *args, **kwargs):
		"""
			Инициализация формы создания текста
		Args:
			user (_type_, optional): Объект пользователя загружающего работу (не обязательно автора).
			language (_type_, optional): Название языкового корпуса (~язык текста).
			text_type (_type_, optional): Название типа загружаемого текста.
		"""
		super(TextCreationForm, self).__init__(*args, **kwargs)
		
		groups = TblGroup.objects.filter(language_id=user.language_id)

		if user.is_teacher():
			students = TblStudent.objects.all().values('user_id')
			user_list = TblUser.objects.filter(language_id=user.language_id, id_user__in=students)

			self.fields['user'] = forms.ModelChoiceField(queryset=user_list, empty_label='Выберите студента', widget=forms.Select(attrs={'class': 'form-control select2'}))
			self.fields['user'].error_messages={'required': 'Выберите студента'}

		elif user.is_student():
			student = TblStudent.objects.filter(user_id=user.id_user).first()

			user_list = TblUser.objects.filter(id_user=user.id_user)
			self.fields['user'] = forms.ModelChoiceField(queryset=user_list, initial=user, widget=forms.Select(attrs={'readonly': True, 'class': 'form-control'}))

			student_groups = TblStudentGroup.objects.filter(student_id=student.id_student).values('group_id')
			groups = groups.filter(id_group__in=student_groups)
		
		
		language = TblLanguage.objects.filter(id_language=user.language_id)
		self.fields['language'] = forms.ModelChoiceField(queryset=language,
				initial=language.first(), widget=forms.Select(attrs={'class':'form-control', 'readonly':True}))

		self.fields['write_place'].empty_label = None
		self.fields['write_place'].initial = TblWritePlace.objects.filter(write_place_name='Не указано').first()
		
		self.fields['emotional'].empty_label = None
		self.fields['emotional'].initial = TblEmotional.objects.filter(emotional_name='Не указано').first()

		self.fields['create_date'].initial = datetime.date.today()
		self.fields['create_date'].error_messages = {'required': 'Введите дату'}

		self.fields['group'] = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control select2', 'required':True}), choices=[(None, 'Выберите группу')] + [(group.id_group, group.group_name + ' (' + str(group.enrollment_date) + ')') for group in groups], initial=None)
		self.fields['group'].error_messages={'required': 'Выберите группу'}


	def save(self, commit=True):
		"""
		Создание записи в БД
		"""
		text = super().save(commit=False)
		
		if commit:
			text.save()

		return text


def get_annotation_form(Grades, Reasons):
	"""
	Генерация формы создания
	Args:
		Grades (_type_): _description_
		Reasons (_type_): _description_

	Returns:
		_type_: _description_
	"""
	grades = [('0', 'Не указано')]
	for element in Grades:
		grades.append((element["id_grade"], element["grade_name"]))

	reasons = [('0', 'Не указано')]
	for element in Reasons:
		reasons.append((element["id_reason"], element["reason_name"]))

	class AnnotatioCreateForm(forms.Form):
		nonlocal reasons
		nonlocal grades

		query_type = forms.IntegerField(
			widget=forms.HiddenInput(attrs={"id": "query-type-field"}))
		classification_tag = forms.IntegerField(
			widget=forms.HiddenInput(attrs={"id": "selected-classif-tag"}))
		tokens = forms.CharField(widget=forms.HiddenInput(
			attrs={"id": "selected-tokens"}))
		markup_id = forms.IntegerField(
			widget=forms.HiddenInput(attrs={"id": "selected-markup-id"}))
		reason = forms.ChoiceField(widget=forms.Select(
			attrs={"id": "selected_reason", "class": "only-errors"}), choices=reasons, label="Причина", required=False)
		grade = forms.ChoiceField(widget=forms.Select(
			attrs={"id": "selected_grade", "class": "only-errors"}), choices=grades, label="Степень грубости:", required=False)
		del reasons
		del grades
		correct = forms.CharField(widget=forms.Textarea(
			attrs={"id": "correct-text", "class": "only-errors"}), label="Исправление:", max_length=255, required=False)  # TODO: Уточнить
		comment = forms.CharField(widget=forms.Textarea(
			attrs={"id": "comment-text"}), label="Комментарий:", max_length=255, required=False)  # TODO: Уточнить

	return (AnnotatioCreateForm)


class SearchTextForm(forms.ModelForm):
	create_date = forms.DateField(
		 widget=DateInput(attrs={'class': 'form-control'}))
	modified_date = forms.DateField(
		widget=DateInput(attrs={'class': 'form-control'}))
	
	text_type_choices = [('', 'Все тексты')] + distinct_text_type_name_choices()

	text_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=text_type_choices, initial='')

	class Meta:
		model = TblText
		fields = ('header', 'user', 'create_date', 'language', 'emotional',
				  'write_place', 'self_rating', 'student_assesment', 'error_tag_check')

		CHOICES_CHECK = (
			(None, 'Все тексты'),
			('0', 'Не проверено'),
			('1', 'Проверено'),
		)

		widgets = {
			'header': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название текста', 'autocomplete': 'off'}),
			'user': forms.Select(attrs={'class': 'form-control select2 d-none'}),
			'language': forms.Select(attrs={'class': 'form-control'}),
			'emotional': forms.Select(attrs={'class': 'form-control'}),
			'write_place': forms.Select(attrs={'class': 'form-control'}),
			'self_rating': forms.Select(attrs={'class': 'form-control'}),
			'student_assesment': forms.Select(attrs={'class': 'form-control'}),
			'error_tag_check': forms.Select(attrs={'class': 'form-control'}, choices=CHOICES_CHECK),
		}

	def __init__(self, language_id=None, *args, **kwargs):
		super(SearchTextForm, self).__init__(*args, **kwargs)
		if not language_id is None:
			self.fields['language'].initial = TblLanguage.objects.filter(id_language=language_id).first()

		self.fields['error_tag_check'].initial = None
		self.fields['language'].empty_label = 'Любой'
		self.fields['emotional'].empty_label = 'Все тексты'
		self.fields['write_place'].empty_label = 'Все тексты'

		students = TblStudent.objects.all().values('user_id')
		users_students = TblUser.objects.filter(id_user__in=students)
		self.fields['user'].queryset=users_students
		self.fields['user'].empty_label = 'Все студенты'


class AssessmentModify(forms.ModelForm):
	class Meta:
		model = TblText
		fields = (
			'assessment',
			'completeness',
			'structure',
			'coherence',
			'pos_check',
			'error_tag_check',
			'teacher',
			'pos_check_user',
			'error_tag_check_user',
			'pos_check_date',
			'error_tag_check_date'
		)
		rates = ((1, '1'),
				 (2, '2-'),
				 (3, '2'),
				 (4, '2+'),
				 (5, '3-'),
				 (6, '3'),
				 (7, '3+'),
				 (8, '4-'),
				 (9, '4'),
				 (10, '4+'),
				 (11, '5-'),
				 (12, '5')
				 )

		widgets = {
			'assessment': forms.Select(attrs={'class': 'form-control'}, choices=rates),
			'completeness': forms.Select(attrs={'class': 'form-control'}, choices=rates),
			'structure': forms.Select(attrs={'class': 'form-control'}, choices=rates),
			'coherence': forms.Select(attrs={'class': 'form-control'}, choices=rates),

			'pos_check': forms.Select(attrs={'class': 'form-control'}, choices=[(True, 'Проверенно'),
																				(False, 'Не указано')]),
			'error_tag_check': forms.Select(attrs={'class': 'form-control'}, choices=[(True,
																					   'Проверенно'), (False, 'Не указано')]),
			'teacher': forms.HiddenInput(),
			'pos_check_user': forms.HiddenInput(),
			'error_tag_check_user': forms.HiddenInput(),
			'pos_check_date': forms.HiddenInput(),
			'error_tag_check_date': forms.HiddenInput()
		}

	def __init__(self, initial, is_teacher, *args, **kwargs):
		super().__init__(*args, **kwargs)

		for key in initial:
			self.fields[key].initial = initial[key]

		if not is_teacher:
			self.fields['assessment'].widget.attrs['readonly'] = "readonly"
			self.fields['completeness'].widget.attrs['readonly'] = "readonly"
			self.fields['structure'].widget.attrs['readonly'] = "readonly"
			self.fields['coherence'].widget.attrs['readonly'] = "readonly"


class MetaModify(forms.ModelForm):
	class Meta:
		model = TblText
		fields = (
			'emotional',
			'write_tool',
			'write_place',
			'education_level',
			'self_rating',
			'student_assesment'
		)

		widgets = {
			'emotional': forms.Select(attrs={'class': 'form-control'}),
			'write_tool': forms.Select(attrs={'class': 'form-control'}),
			'write_place': forms.Select(attrs={'class': 'form-control'}),
			'education_level': forms.NumberInput(attrs={'class': 'form-control'}),
			'self_rating': forms.Select(attrs={'class': 'form-control'}),
			'student_assesment': forms.Select(attrs={'class': 'form-control'}),
		}

	def __init__(self, initial, *args, **kwargs):
		super().__init__(*args, **kwargs)

		for key in initial:
			self.fields[key].initial = initial[key]


class AuthorModify(forms.Form):
	fields = ['user']

	def __init__(self, options: list, init: tuple, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['user'] = forms.ChoiceField(widget=forms.Select,
												choices=options, initial=init)
