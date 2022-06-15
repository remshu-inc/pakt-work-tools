from django.shortcuts import redirect, render
from django.http import HttpResponse
from text_app.models import TblTag, TblMarkup, TblToken, TblSentence
from django.db.models import Q
import re
from .forms import StatisticForm
from .stat_src import built_group_stat
from wsgiref.util import FileWrapper
from os import remove

def index(request):
    return render(request, "index.html")


def _filter_shaping(cql):
    """Формирование филтра на основе cql

    Keyword arguments:
    cql -- Запроса пользователя

    """
    
    # Получение аттрибута запроса
    word = re.search(r'[\'\"].*[\'\"]', cql).group(0)[1:-1]
    
    # Удаление всех пробелов
    cql = cql.replace(" ", "")
    
    # Обработка словоформ
    if 'word=' in cql:
        return Q(token_id__text__iexact = word)
        
    # Обрабокта тегов ошибок и частеречной разметки
    elif 'error=' in cql or 'pos=' in cql:
        return Q(Q(tag_id__tag_text = word) | Q(tag_id__tag_text_russian = word))
        
    # Обработка словоформ
    if 'word!=' in cql:
        return ~Q(token_id__text__iexact = word)
        
    # Обрабокта тегов ошибок и частеречной разметки
    elif 'error!=' in cql or 'pos=' in cql:
        return ~Q(Q(tag_id__tag_text = word) | Q(tag_id__tag_text_russian = word))
    
    return None
        

def _parse_cql(user_query = None):
    """Парсинг Corpus Query Language из запроса пользователя

    Keyword arguments:
    user_query -- Запрос пользователя (default None)

    """
    
    # Получение cql из запроса пользователя
    cql = re.findall(r'\[[^\[\]]+\]', user_query)
    
    # Формирование фильтра для поиска в БД
    filters = Q()
    
    for token_cql in cql:
        
        # Парсинг нескольких параметров
        if "&" in token_cql:
            parts_token_cql = token_cql[1:-1].split('&')
            for part in parts_token_cql:
                
                filters &= _filter_shaping(part)
            # print(filters)
        
        # Парсинг альтернативных вариантов
        # TODO: Исправить вывод дублированных текстов(где совпадает и токен, и тег)
        elif "|" in token_cql:
            parts_token_cql = token_cql[1:-1].split('|')
            alt_filters = Q()
            for part in parts_token_cql:
                
                alt_filters |= _filter_shaping(part)


            filters &= alt_filters
                
        
        else:
            filters &= _filter_shaping(token_cql)
    
    return filters
                    
                    
def search(request):
    if request.POST:
        user_query = request.POST['corpus_search']
        filters = _parse_cql(user_query)
        
        # Получение строк по заданным условиям
        sentence_objects = TblMarkup.objects.filter(filters).values(
            'token_id', 'token_id__sentence_id', 'token_id__sentence_id__text_id__header', 'token_id__sentence_id__text_id__create_date'
        )[:100]
        
        # TODO: пропписать исключение
        if len(sentence_objects) == 0:
            pass
        
        list_search = []
        for sentence in sentence_objects:
            tokens = TblToken.objects.filter(
                sentence_id = sentence['token_id__sentence_id']
            ).order_by('order_number')
            
            list_token = []
            for token in tokens:
                if token.text == '-EMPTY-':
                    continue
                if token.id_token == sentence['token_id']:
                    list_token.append({'text': token.text, 'primary': True})
                else:
                    list_token.append({'text': token.text})
            
            list_search.append({
                'header': sentence['token_id__sentence_id__text_id__header'],
                'tokens': list_token,
                'create_date': sentence['token_id__sentence_id__text_id__create_date']
            })
        
        # Для неточного поиска
        # MyClass.objects.filter(name__iexact=my_parameter)

        return render(request, "search.html", context={'search_value': request.POST['corpus_search'],'list_search': list_search})

    else:
        return redirect(request, 'home')


def get_stat(request):
    if request.user.is_teacher:
        if request.method != 'POST':
            return(render(request, 'stat_form.html', {'right':True, 'form': StatisticForm(), 'no_data':False}))
        else:
            form = StatisticForm(request.POST or None)
            if form.is_valid():

                value = [int(element) for element in form.cleaned_data['group_number']]
                course_number = int(form.cleaned_data['course_number'])
                detalization = int(form.cleaned_data['output_type'])
                stat_by = int(form.cleaned_data['stat_by'])
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']

                stat_res = built_group_stat(value, course_number,detalization, stat_by, request.user.id_user, start_date, end_date)
                if stat_res['state']:

                    response = HttpResponse(FileWrapper(open(stat_res['folder_link'],'rb')), content_type='application/zip')
                    
                    filename = stat_res['file_name'].replace(" ", "_")
                    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

                    remove(stat_res['folder_link'])
                    return(response)
                else:
                    return(render(request, 'stat_form.html', {'right':True, 'form': StatisticForm(), 'no_data':True}))
    else:
        return(render(request, 'stat_form.html', {'right':False, 'no_data':False}))