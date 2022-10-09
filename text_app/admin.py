from django.contrib import admin

from user_app.models import TblLanguage
from text_app.models import TblEmotional, TblTextType, TblWritePlace, TblWriteTool, TblText

@admin.register(TblLanguage)
class TblLanguageAdmin(admin.ModelAdmin):
    model = TblLanguage
    
@admin.register(TblTextType)
class TblTextTypeAdmin(admin.ModelAdmin):
    model = TblTextType
    
@admin.register(TblEmotional)
class TblEmotionalAdmin(admin.ModelAdmin):
    model = TblEmotional
    
@admin.register(TblWritePlace)
class TblWritePlaceAdmin(admin.ModelAdmin):
    model = TblWritePlace
    
@admin.register(TblWriteTool)
class TblWriteToolAdmin(admin.ModelAdmin):
    model = TblWriteTool
    
@admin.register(TblText)
class TblTextAdmin(admin.ModelAdmin):
    model = TblText  
