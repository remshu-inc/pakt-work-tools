from django import forms
from .models import TblLanguage, TblText, TblTextType

class TextTypeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return super().label_from_instance(obj)
        # return "TblLanguage #%s) %s" % (obj.id_language, obj.language_name)
    

class TextCreationForm(forms.ModelForm):
    
    class Meta:
        model = TblText
        fields = ('__all__')
        
