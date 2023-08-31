from datetime import datetime
from faulthandler import disable
from django import forms
from text_app.models import  TblText, TblTextType
from user_app.models import TblUser, TblStudent, TblGroup, TblLanguage


class StatisticForm(forms.Form):
    fields = {'group'}

    def __init__(self, language_id:int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        groups = TblGroup.objects.filter(language_id = language_id).order_by('-enrollment_date').values('id_group', 'group_name', 'enrollment_date')
        options = []
        if groups.exists():
            for group in groups:
                options.append(
                    (
                    group['id_group'],
                    group['group_name']+\
                        ' ('+str(group['enrollment_date'].year)+' \ '\
                            +str(group['enrollment_date'].year+1)+')'
                    ))

        self.fields['group'] = forms.ChoiceField(choices=options)
        self.fields['group'].widget.attrs.update({'class': 'form-control'})
        