from faulthandler import disable
from django import forms
from .models import TblLanguage, TblText, TblTextType
from user_app.models import TblUser, TblStudent
import datetime

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
        fields = ('header', 'user', 'create_date', 'modified_date', 'text', 'creation_course', 'language', 'text_type', 'emotional', 'write_tool', 'write_place', 'education_level', 'self_rating', 'student_assesment')
        
        widgets = {
            'header': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 12}),
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
            
            # Если пользователь студент
            student = TblStudent.objects.filter(user_id = user.id_user)
            if len(student) != 0:
                user_object = TblUser.objects.filter(id_user = user.id_user)
                self.fields['user'] = forms.ModelChoiceField(queryset=user_object, widget=forms.Select(attrs={'class': 'form-control'}))
                self.fields['user'].initial = user_object[0]
                self.fields['user'].widget.attrs['readonly'] = "readonly" 
                
            else:
                self.fields['user'] = forms.ModelChoiceField(queryset=TblUser.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
                
            language_object = TblLanguage.objects.filter(language_name = language)
            self.fields['language'] = forms.ModelChoiceField(queryset=language_object, widget=forms.Select(attrs={'class': 'form-control'}))
            self.fields['language'].initial = language_object[0]
            self.fields['language'].widget.attrs['readonly'] = "readonly" 
            
            text_type_object = TblTextType.objects.filter(text_type_name = text_type, language_id = language_object[0].id_language)
            self.fields['text_type'] = forms.ModelChoiceField(queryset=text_type_object, widget=forms.Select(attrs={'class': 'form-control'}))
            self.fields['text_type'].initial = text_type_object[0]
            self.fields['text_type'].widget.attrs['readonly'] = "readonly" 
            
            
