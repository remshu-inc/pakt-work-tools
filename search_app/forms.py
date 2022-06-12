from faulthandler import disable
from django import forms
from text_app.models import TblLanguage, TblText, TblTextType
from user_app.models import TblUser, TblStudent


class StatisticForm(forms.Form):


    fields = {'group_number', 'course_number'}
    # group_number = forms.MultipleChoiceField()
    # course_number = forms.ChoiceField()

    output_type = forms.ChoiceField(choices=[(1, 'Суммарно по всей группе'), (2, 'По каждому студенту группы')])
    stat_by = forms.ChoiceField(choices = [(1, 'Только по ошибкам'), (2, 'Только по метаданным'), (3, 'По всем')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['group_number'] = forms.MultipleChoiceField(
        choices=TblStudent.objects.all().order_by("group_number").values_list("group_number","group_number").distinct(), required=True, 
        widget=forms.SelectMultiple,
        initial=113)         
        self.fields['course_number'] = forms.ChoiceField(
        choices = [[-2, 'Любой']] + list(TblText.objects.all().order_by('creation_course').values_list("creation_course","creation_course").distinct()),
        required=True)

    

