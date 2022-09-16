from datetime import datetime
from faulthandler import disable
from django import forms
from text_app.models import TblLanguage, TblText, TblTextType
from user_app.models import TblUser, TblStudent, TblGroup


class StatisticForm(forms.Form):


    fields = {'group', 'course_number'}

    output_type = forms.ChoiceField(choices=[(1, 'Общая сводка'), (2, 'По каждому студенту')])
    stat_by = forms.ChoiceField(choices = [(1, 'Только по ошибкам'), (2, 'Только по метаданным'), (3, 'По всем')])
    end_date = forms.DateField(initial =datetime.today,  widget = forms.widgets.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        groups = TblGroup.objects.order_by('enrollement_date').values('id_group', 'group_name', 'enrollement_date')
        if groups.exists():
            options = []        
            for group in groups:
                options.append(
                    (group['id_group'],
                    group['group_name']+\
                        ' '+str(group['enrollement_date'].year)+' \ '\
                            +str(group['enrollement_date'].year+1)
                    ))

        self.fields['group'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                        choices=options)

        self.fields['course_number'] = forms.ChoiceField(
        choices = [[-2, 'Любой']] + list(TblText.objects.all().order_by('creation_course').values_list("creation_course","creation_course").distinct()),
        required=True)

        year_ = datetime.today().year
        month_ = datetime.today().month 

        if month_ < 9:
            initial_start_date = datetime(year_-1, 9, 1)
        else:
            initial_start_date = datetime(year_, 9, 1)

        self.fields['start_date'] = forms.DateField(initial =initial_start_date,  widget = forms.widgets.DateInput(attrs={'type': 'date'}))