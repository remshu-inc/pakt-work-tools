# from django.views import generic
# from .models import TblText
from .models import TblLanguage, TblTextType, TblText, TblSentence, TblMarkup, TblTag, TblTokenMarkup, TblToken
from .forms import TextCreationForm, SearchTextForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from copy import deepcopy
from django.db.models import F, Q
from right_app.views import check_permissions_show_text
from user_app.models import TblTeacher, TblUser


# Test

# class TextList(generic.ListView):
#     queryset = TblText.objects
#     template_name = 'corpus.html'

def show_files(request, language = None, text_type = None):
    # Для выбора языка
    if not request.user.is_authenticated:
        return redirect('home')
    elif request.user.is_teacher:
        form_search = SearchTextForm()
        
    # if request.POST['corpus_search']:
        # return redirect(request) 
    
    if language == None:
        try:
            list_language = TblLanguage.objects.all()
            print(list_language)
            return render(request, "corpus.html", context= {'list_language': list_language, 'form_search': form_search})
            
        # except TblLanguage.DoesNotExist:
        # TODO: прописать исключение для каждой ошибки?
        except:
            return(render(request, "corpus.html", context = {'error': True, 'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))

    # Для выбора типа текста
    elif text_type == None:
        language_object = TblLanguage.objects.filter(language_name=language)
        if len(language_object) == 0:
            return(render(request, "corpus.html", context = {'error': True, 'text_html':'Language not found'}))
        else:
            language_id = language_object.first().id_language
        
        list_text_type = TblTextType.objects.filter(language_id=language_id)
        if len(list_text_type) == 0:
            return(render(request, "corpus.html", context = {'error': True, 'text_html':'Text type not found'}))
        else:
            return(render(request, "corpus.html", context= {'list_text_type': list_text_type, 'form_search': form_search}))
        
    # Для выбора текста
    else:
        language_object = TblLanguage.objects.filter(language_name=language)
        if len(language_object) == 0:
            return(render(request, "corpus.html", context = {'error': True, 'text_html':'Language not found'}))
        else:
            language_id = language_object.first().id_language

        text_type_object = TblTextType.objects.filter(language_id=language_id, text_type_name=text_type)
        if len(text_type_object) == 0:
            return(render(request, "corpus.html", context = {'error': True, 'text_html':'Text type not found'}))
        else:
            text_type_id = text_type_object.first().id_text_type
        
        order_by = ''
        if request.GET:
            order_by = request.GET.get('order_by', 'defaultOrderField')
        if check_permissions_show_text(request.user.id_user):
            if order_by == '':
                list_text = TblText.objects.filter(language_id=language_id, text_type_id=text_type_id)
            else:
                list_text = TblText.objects.filter(language_id=language_id, text_type_id=text_type_id).order_by(order_by)
        else:
            if order_by == '':
                list_text = TblText.objects.filter(language_id=language_id, text_type_id=text_type_id, user_id=request.user.id_user)
            else:
                list_text = TblText.objects.filter(language_id=language_id, text_type_id=text_type_id, user_id=request.user.id_user).order_by(order_by)
            
        list_text_and_user = []
        for text in list_text:
            user = TblUser.objects.filter(id_user=text.user_id).first()
            if user.name == 'empty':
                list_text_and_user.append([text, ''])
            else:
                list_text_and_user.append([text, user.last_name + ' ' + user.name])
            
        return(render(request, "corpus.html", context= {'work_with_file': True, 'list_text_and_user': list_text_and_user, 'language_selected': language, 'form_search': form_search}))
    
    return(render(request, "corpus.html", context = {'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))
 
def corpus_search(request):
    if request.POST:
        form_search = SearchTextForm(request.POST)
        # Entry.objects.all().filter(pub_date__year=2006)
        filters = Q()
        if form_search.data['header']:
            filters &= Q(header = form_search.data['header'])
        if form_search.data['user']:
            filters &= Q(user_id = form_search.data['user'])
        if form_search.data['language']:
            filters &= Q(language_id = form_search.data['language'])
        if form_search.data['text_type']:
            filters &= Q(text_type_id = form_search.data['text_type'])
        if form_search.data['create_date']:
            filters &= Q(create_date = form_search.data['create_date'])
        if form_search.data['modified_date']:
            filters &= Q(modified_date = form_search.data['modified_date'])
        
        list_text = TblText.objects.filter(filters)
        
    else:
        form_search = SearchTextForm()
        
    return(render(request, "corpus_search.html", context= {'form_search': form_search, 'list_text': list_text}))
        
 
def new_text(request, language = None, text_type = None):
    
    # Проверка на выбранный язык и тип текста
    if language != None and text_type != None:
        
        language_object = TblLanguage.objects.filter(language_name = language)
        if len(language_object) != 0:
            language_id = language_object[0].id_language
        else:
            return render(request, 'corpus.html')
            
        text_type_objects = TblTextType.objects.filter(language_id = language_id, text_type_name = text_type)
        if len(text_type_objects) == 0:
            return render(request, 'corpus.html')
    else:
        return render(request, 'corpus.html')
    
    if request.method == 'POST':
        from nltk.tokenize import sent_tokenize, word_tokenize
        form_text = TextCreationForm(request.user, language_object[0], text_type_objects[0], data=request.POST)
        
        if form_text.is_valid():
            text = form_text.save()
            count_sent = 0
            for sent in sent_tokenize(text.text):
                sent_object = TblSentence(
                    text_id = text,
                    text = sent,
                    order_number = count_sent
                )
                print(sent_object)
                sent_object.save()
                print(sent_object)
                count_sent += 1
                
                count_token = 0
                for token in word_tokenize(sent):
                    token_object = TblToken(
                        sentence_id = sent_object.id_sentence,
                        text = token,
                        order_number = count_token
                    )
                    token_object.save()
                    
                    count_token += 1

            return redirect('/corpus/' + language + '/' + text_type)
        else:
            # print(form_text.errors)
            pass
            
    else:
        form_text = TextCreationForm(request.user, language_object[0], text_type_objects[0])
        
    return render(request, 'new_text.html', {'form_text': form_text})

#Функция подстановки аннотаций в шаблон
def past_in_template(markup, start, end, template):
    if start == end:
        position = 'single'
    else:
        position = 'start'

    template[start] =  {
            'isann': True,
            'display':True,
            'ann_position': position,
            'ann_id': markup['id_markup'],
            'tag_text': markup['tag_text'],
            'tag_text_rus': markup['tag_text_russian'],
            'tag_type': markup['markup_type_name']
        }
        
    for index in range(start+1, end+1):
        template[index] = deepcopy(template[start])
        template[index]['display'] = False
        if index == end:
            template[index]['ann_position'] = 'end'
        else:
            template[index]['ann_position'] = 'middle'
    return(template)


def show_text(request, language_test = None, text_type_test = None, text_id = 1, pos = 1, error = 1, language = 'foreign'):
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