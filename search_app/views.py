from os import remove
import re
from wsgiref.util import FileWrapper
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.db.models import Q
from text_app.models import TblMarkup, TblToken
from .forms import StatisticForm
from .stat_src import built_group_stat

def index(request):
    """ Рендер главной страницы

    Args:
        request: http-запрос с пользовательской информацией

    Returns:
        HttpResponse: html главной страницы
    """
    
    return render(request, "index.html")


def _filter_shaping(cql):
    """Формирование фильтра на основе cql

    Keyword arguments:
    cql -- Запроса пользователя

    """
    
    # Получение аттрибута запроса
    word = re.search(r'[\'\"].*[\'\"]', cql).group(0)[1:-1]
    
    # Удаление всех пробелов
    cql = cql.replace(" ", "")
    
    # Обработка токенов соответсвующих словоформе
    if 'word=' in cql:
        # REGEX
        if word[0:2] == '.*' and word[-2:] == '.*':
            return Q(token_id__text__contains = word[2:-2])
        elif word[-2:] == '.*':
            return Q(token_id__text__startswith = word[:-2])
        elif word[0:2] == '.*':
            return Q(token_id__text__endswith = word[2:])
        else:
            return Q(token_id__text__iexact = word)
        
    # Обрабокта токенов с указанными тегами ошибок и частеречной разметки
    elif 'error=' in cql or 'pos=' in cql:
        return Q(Q(tag_id__tag_text = word) | Q(tag_id__tag_text_russian = word))
        
    # Обработка токенов не соответсвующих словоформе
    if 'word!=' in cql:
        # REGEX
        if word[0:2] == '.*' and word[-2:] == '.*':
            return ~Q(token_id__text__contains = word[2:-2])
        elif word[-2:] == '.*':
            return ~Q(token_id__text__startswith = word[:-2])
        elif word[0:2] == '.*':
            return ~Q(token_id__text__endswith = word[2:])
        else:
            return ~Q(token_id__text__iexact = word)
        
    # Обрабокта токенов без указанных тегов ошибок и частеречной разметки
    elif 'error!=' in cql or 'pos!=' in cql:
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
        
        # TODO: парсить word не из tblmarkup
        # Парсинг нескольких параметров
        if "&" in token_cql:
            parts_token_cql = token_cql[1:-1].split('&')
            for part in parts_token_cql:

                if _filter_shaping(part) is not None:
                    filters &= _filter_shaping(part)

        
        # Парсинг альтернативных вариантов
        # TODO: Исправить вывод дублированных текстов(где совпадает и токен, и тег)
        elif "|" in token_cql:
            parts_token_cql = token_cql[1:-1].split('|')
            alt_filters = Q()
            for part in parts_token_cql:
                
                if _filter_shaping(part) is not None:
                    alt_filters |= _filter_shaping(part)

            filters &= alt_filters
                
        
        else:
            if _filter_shaping(token_cql) is not None:
                filters &= _filter_shaping(token_cql)
                
    if filters == Q():
        return None
        
    return filters
                    
                    
def search(request):
    """ Обработка поискового запроса пользователя и генерация результата

    Args:
        request: http-запрос с пользовательской информацией

    Returns:
        HttpResponse: html страница с результатом поиска
    """
    if request.POST:
        user_query = request.POST['corpus_search']
        filters = _parse_cql(user_query)
        if filters is None:
            return render(request, "search.html", context={'error_search': 'Text not Found', 'search_value': request.POST['corpus_search']})
        
        # Получение строк по заданным условиям
        sentence_objects = TblMarkup.objects.filter(filters).values(
            'token_id', 'token_id__sentence_id', 'token_id__sentence_id__text_id__header', 'token_id__sentence_id__text_id__create_date'
        )[:100]
        
        # TODO: пропписать исключение
        if len(sentence_objects) == 0:
            return render(request, "search.html", context={'error_search': 'Text not Found', 'search_value': request.POST['corpus_search']})
        
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
    if request.user.is_teacher():
        if request.method != 'POST':
            return(render(request, 'stat_form.html', {'right':True, 'form': StatisticForm(), 'no_data':False}))
        else:
            form = StatisticForm(request.POST or None)
            if form.is_valid():

                value = [int(element) for element in form.cleaned_data['group']]
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