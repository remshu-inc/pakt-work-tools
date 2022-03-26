# from django.views import generic
# from .models import TblText
from pickle import TRUE
from .models import TblLanguage, TblReason, TblGrade, TblTextType, TblText, TblSentence, TblMarkup, TblTag, TblTokenMarkup, TblToken
from .forms import TextCreationForm, get_annotation_form
from django.shortcuts import render
from django.http import HttpResponse
from copy import deepcopy
from django.db.models import F

# Test

# class TextList(generic.ListView):
#     queryset = TblText.objects
#     template_name = 'corpus.html'

def show_files(request, language = None, text_type = None):

    # print(request.user.get_user_permissions)
    
    if language == None:
        try:
            list_language = TblLanguage.objects.all()
            return render(request, "corpus.html", context= {'list_language': list_language})
            
        # except TblLanguage.DoesNotExist:
        # TODO: прописать исключение для каждой ошибки?
        except:
            return(render(request, "corpus.html", context = {'error': True, 'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))

    
    elif text_type == None:
        try:
            language_id = TblLanguage.objects.all().filter(language_name=language)[0]
            
        except:
            return(render(request, "corpus.html", context = {'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))
        
        try:
            list_text_type = TblTextType.objects.all().filter(language_id=language_id)
            return(render(request, "corpus.html", context= {'list_text_type': list_text_type}))
            
        except TblLanguage.DoesNotExist:
            return(render(request, "corpus.html", context = {'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))
    
    else:
        try:
            language_id = TblLanguage.objects.all().filter(language_name=language)[0]
            
        except TblLanguage.DoesNotExist:
            return(render(request, "corpus.html", context = {'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))
        
        try:
            text_type_id = TblTextType.objects.all().filter(language_id=language_id, text_type_name=text_type)[0]
            
        except TblLanguage.DoesNotExist:
            return(render(request, "corpus.html", context = {'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))
        
        list_text = TblText.objects.all().filter(language_id=language_id, text_type_id=text_type_id)
        if list_text.count() == 0:
            return(render(request, "corpus.html", context = {'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))
        
        return(render(request, "corpus.html", context= {'list_text': list_text, 'language_selected': language}))
    
    return(render(request, "corpus.html", context = {'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))

def new_file(request, language = None, text_type = None):  
    # if language == None or text_type == None:
        # return(render(request, "corpus.html", context = {'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))
    
    if request.method == 'POST':
        form_text = TextCreationForm(request.POST)
        
        if form_text.is_valid():
            texts = form_text.save(commit=False)
            
    else:
        form_text = TextCreationForm()
        
    return render(request, 'new_text.html', {'form_text': form_text})


def show_text(request, text_id = 1, pos = 1, error = 1, language = 'foreign'):
    text_info  = TblText.objects.filter(id_text = text_id).values('header','language_id', 'language_id__language_name').all()
    if text_info.exists():
        header = text_info[0]['header']
        text_language_name = text_info[0]['language_id__language_name']
        text_language = text_info[0]['language_id']
        tags = TblTag.objects.filter(tag_language_id = text_language).values('id_tag','tag_text','tag_text_russian', 'tag_parent','tag_color').all()
        tags_info = []
        if tags.exists():
            for element in tags:
                parent_id = 0
                if element['tag_parent']>0:
                    parent_id = element['tag_parent']
                spoiler = False
                for child in tags:
                    if element['id_tag'] == child['tag_parent']:
                        spoiler = True
                        break
                tags_info.append({
                    'isspoiler':spoiler,
                    'tag_id':element['id_tag'],
                    'tag_text':element['tag_text'],
                    'tag_text_russian':element['tag_text_russian'],
                    'parent_id':parent_id,
                    'tag_color':element['tag_color']
                })
        reasons = TblReason.objects.filter(reason_language_id = text_language).values('id_reason','reason_name')
        grades = TblGrade.objects.filter(grade_language_id = text_language).values('id_grade','grade_name')
        annotation_form = get_annotation_form(grades,reasons)
        if pos == 1:
            pos = True
        else:
            pos = False
        if error == 1:
            error = True
        else:
            error = False

        return render(request, "work_area.html", context= {'founded':True,'ann_right':True, 'tags_info':tags_info, 'annotation_form':annotation_form, 'text_id':text_id,'header':header, 'pos':pos, 'error':error, 'lang_name':text_language_name})
    else:
        return render(request, 'work_area.html', context={'founded':False})