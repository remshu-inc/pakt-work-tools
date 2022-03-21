# from django.views import generic
# from .models import TblText
from .models import TblLanguage, TblTextType, TblText, TblSentence, TblMarkup, TblTag, TblTokenMarkup, TblToken
from .forms import TextCreationForm
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
    if pos == 1:
        pos = True
    else:
        pos = False
    if error == 1:
        error = True
    else:
        error = False
    if language == 'foreign':
        language = 0
    elif language == 'russian':
        language = 1
    else:
        language = 0


    return render(request, "text_show.html", context= {'text_id':text_id, 'found':True, 'pos':pos, 'error':error, 'lang':language})