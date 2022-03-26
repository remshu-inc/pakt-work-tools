from django import forms
from .models import TblLanguage, TblText, TblTextType

class TextTypeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return super().label_from_instance(obj)
        # return "TblLanguage #%s) %s" % (obj.id_language, obj.language_name)

# class AnnotationToolForm(forms.ModelForm):

class TextCreationForm(forms.ModelForm):
    
    class Meta:
        model = TblText
        fields = ('__all__')


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



        
