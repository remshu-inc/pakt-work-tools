from datetime import datetime
from faulthandler import disable
from django import forms
from text_app.models import TblLanguage, TblText, TblTextType
from user_app.models import TblUser, TblStudent


class StatisticForm(forms.Form):


    fields = {'group_number', 'course_number'}
    # group_number = forms.MultipleChoiceField()
    # course_number = forms.ChoiceField()

    output_type = forms.ChoiceField(choices=[(1, 'Общая сводка'), (2, 'По каждому студенту')])
    stat_by = forms.ChoiceField(choices = [(1, 'Только по ошибкам'), (2, 'Только по метаданным'), (3, 'По всем')])
    start_date = forms.DateField(initial =datetime(1, 1, 1, 0, 0),  widget = forms.widgets.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(initial =datetime.today,  widget = forms.widgets.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['group_number'] = forms.MultipleChoiceField(
        choices=TblStudent.objects.all().order_by("group_number").values_list("group_number","group_number").distinct(), required=True, 
        widget=forms.SelectMultiple,
        initial=113)         
        self.fields['course_number'] = forms.ChoiceField(
        choices = [[-2, 'Любой']] + list(TblText.objects.all().order_by('creation_course').values_list("creation_course","creation_course").distinct()),
        required=True)

    

