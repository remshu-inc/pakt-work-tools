from email.policy import default
from faulthandler import disable
from django import forms
from .models import TblText, TblTextType, TblTextGroup
from user_app.models import TblUser, TblStudent, TblStudentGroup, TblLanguage
import datetime
from right_app.views import check_permissions_new_text, check_permissions_work_with_annotations

class TextTypeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return super().label_from_instance(obj)
        # return "TblLanguage #%s) %s" % (obj.id_language, obj.language_name)

        
class DateInput(forms.DateInput):
    input_type = 'date'


class TextCreationForm(forms.ModelForm):
    
    create_date = forms.DateField(initial=datetime.date.today, widget=DateInput(attrs={'class': 'form-control'}))
    modified_date = forms.DateField(initial=datetime.date.today, widget = forms.HiddenInput())
    # asd = forms.Model
    
    class Meta:
        model = TblText
        fields = (
            'header',
            'user',
            'create_date',
            'modified_date',
            'text',
            'creation_course',
            'language',
            'text_type',
            'emotional',
            'write_tool',
            'write_place',
            'education_level',
            'self_rating',
            'student_assesment'
            )
        
        widgets = {
            'header': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 14}),
            'emotional': forms.Select(attrs={'class': 'form-control'}),
            'write_tool': forms.Select(attrs={'class': 'form-control'}),
            'write_place': forms.Select(attrs={'class': 'form-control'}),
            'education_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'self_rating': forms.Select(attrs={'class': 'form-control'}),
            'student_assesment': forms.Select(attrs={'class': 'form-control'}),
            'creation_course': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, user=None, language=None, text_type=None, *args, **kwargs):
        super(TextCreationForm, self).__init__(*args, **kwargs)    
        if user != None and language != None and text_type != None:
            
            # Если у пользователя нет прав загружать текст от чужого лица
            user_object = TblUser.objects.filter(id_user = user.id_user)
            self.fields['user'] = forms.ModelChoiceField(queryset=user_object, widget=forms.Select(attrs={'class': 'form-control'}))
            self.fields['user'].initial = user_object[0]
            self.fields['user'].widget.attrs['readonly'] = "readonly" 
                
            language_object = TblLanguage.objects.filter(language_name = language)
            self.fields['language'] = forms.ModelChoiceField(queryset=language_object, widget=forms.Select(attrs={'class': 'form-control'}))
            self.fields['language'].initial = language_object[0]
            self.fields['language'].widget.attrs['readonly'] = "readonly" 
            
            text_type_object = TblTextType.objects.filter(text_type_name = text_type, language_id = language_object[0].id_language)
            self.fields['text_type'] = forms.ModelChoiceField(queryset=text_type_object, widget=forms.Select(attrs={'class': 'form-control'}))
            self.fields['text_type'].initial = text_type_object[0]
            self.fields['text_type'].widget.attrs['readonly'] = "readonly" 
            
    def save(self, commit=True):
        text = super().save(commit=False)
        
        if commit:
            text.save()
            
        return text
            
            
def get_annotation_form(Grades, Reasons):
    grades = [('0','Не указано')]
    for element in Grades:
        grades.append((element["id_grade"], element["grade_name"]))

    reasons = [('0','Не указано')]
    for element in Reasons:
        reasons.append((element["id_reason"], element["reason_name"]))
    class AnnotatioCreateForm(forms.Form):
        nonlocal reasons
        nonlocal grades

        query_type = forms.IntegerField(widget=forms.HiddenInput(attrs={"id":"query-type-field"}))
        classification_tag = forms.IntegerField(widget=forms.HiddenInput(attrs={"id":"selected-classif-tag"}))
        tokens = forms.CharField(widget=forms.HiddenInput(attrs={"id":"selected-tokens"}))
        markup_id = forms.IntegerField(widget=forms.HiddenInput(attrs={"id":"selected-markup-id"}))
        reason = forms.ChoiceField(widget=forms.Select(attrs={"id":"selected_reason","class":"only-errors"}), choices=reasons, label = "Причина",required=False)
        grade = forms.ChoiceField(widget=forms.Select(attrs={"id":"selected_grade","class":"only-errors"}), choices=grades, label = "Степень грубости:", required=False)
        del reasons
        del grades
        correct = forms.CharField(widget = forms.Textarea(attrs={"id":"correct-text", "class":"only-errors"}), label = "Исправление:", max_length=255,required=False)#TODO: Уточнить
        comment = forms.CharField(widget = forms.Textarea(attrs={"id":"comment-text"}), label = "Комментарий:", max_length=255,required=False)#TODO: Уточнить
    
    return(AnnotatioCreateForm)
            
            
class SearchTextForm(forms.ModelForm):
    
    create_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    modified_date = forms.DateField(widget=DateInput(attrs={'class': 'form-control'}))
    # text_type = forms.ModelMultipleChoiceField(queryset=None, widget=Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = TblText
        fields = ('header', 'user', 'create_date', 'modified_date', 'creation_course', 'language', 'text_type', 'emotional', 'write_tool', 'write_place', 'education_level', 'self_rating', 'student_assesment', 'creation_course', 'pos_check', 'error_tag_check')
        
        CHOICES_CHECK = (
            ('0', 'Не указано'),
            ('1', 'Проверенно'),
        )
        
        widgets = {
            'header': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название текста', 'aria-describedby': 'button-addon'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control', 'v-on:change': 'ChangeTypes'}),
            'text_type': forms.Select(attrs={'class': 'form-control'}),
            'emotional': forms.Select(attrs={'class': 'form-control'}),
            'write_tool': forms.Select(attrs={'class': 'form-control'}),
            'write_place': forms.Select(attrs={'class': 'form-control'}),
            'education_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'self_rating': forms.Select(attrs={'class': 'form-control'}),
            'student_assesment': forms.Select(attrs={'class': 'form-control'}),
            'creation_course': forms.Select(attrs={'class': 'form-control'}),
            'pos_check': forms.Select(attrs={'class': 'form-control'}, choices=CHOICES_CHECK),
            'error_tag_check': forms.Select(attrs={'class': 'form-control'}, choices=CHOICES_CHECK),
        }

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
        rates = ((1,'1'),
            (2,'2-'),
            (3,'2'),
            (4,'2+'),
            (5,'3-'),
            (6,'3'),
            (7,'3+'),
            (8,'4-'),
            (9,'4'),
            (10,'4+'),
            (11,'5-'),
            (12,'5')		 
        )

        widgets = {
            'assessment': forms.Select(attrs={'class': 'form-control'}, choices = rates),
            'completeness': forms.Select(attrs={'class': 'form-control'}, choices = rates),
            'structure': forms.Select(attrs={'class': 'form-control'}, choices = rates),
            'coherence': forms.Select(attrs={'class': 'form-control'}, choices = rates),

            'pos_check': forms.Select(attrs={'class': 'form-control'}, choices = [(True,'Проверенно'),\
                (False,'Не указано')]),
            'error_tag_check': forms.Select(attrs={'class': 'form-control'}, choices = [(True,\
                'Проверенно'), (False,'Не указано')]),
            'teacher': forms.HiddenInput(),
            'pos_check_user':forms.HiddenInput(),
            'error_tag_check_user':forms.HiddenInput(),
            'pos_check_date':forms.HiddenInput(),
            'error_tag_check_date':forms.HiddenInput()
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

class  AuthorModify(forms.Form):
    fields = ['user']
    
    def __init__(self, options:list, init:tuple, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'] = forms.ChoiceField(widget=forms.Select,
                                        choices=options, initial=init)
        

                    

            
            
