import logging
from os import remove
import re
from wsgiref.util import FileWrapper
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.db.models import Q
from text_app.models import TblMarkup, TblToken, TblTag, TblSentence, TblText, TblTextType
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


def cql_faq(request):
    """ Рендер FAQ по CQL

    Args:
        request: http-запрос с пользовательской информацией

    Returns:
        HttpResponse: html FQL по CQL
    """

    return render(request, "cql_faq.html")


def _filter_shaping(cql):
    """Формирование фильтра на основе cql

    Keyword arguments:
    cql -- Запроса пользователя

    """

    # Получение аттрибута запроса
    word = re.search(r'[\'\"\”].*[\'\"\”]', cql).group(0)[1:-1]

    # Удаление всех пробелов
    cql = cql.replace(" ", "")

    # Обработка токенов соответсвующих словоформе
    if 'word=' in cql:
        # REGEX
        if word[0:2] == '.*' and word[-2:] == '.*':
            return Q(token_id__text__contains=word[2:-2])
        elif word[-2:] == '.*':
            return Q(token_id__text__startswith=word[:-2])
        elif word[0:2] == '.*':
            return Q(token_id__text__endswith=word[2:])
        else:
            return Q(token_id__text__iexact=word)

    # Обрабокта токенов с указанными тегами ошибок и частеречной разметки
    elif 'error=' in cql or 'pos=' in cql:
        return Q(Q(tag_id__tag_text = word) | Q(tag_id__tag_text_russian = word) | Q(tag_id__tag_text_abbrev = word))

    # Обработка токенов с указанными степенями грубости ошибки
    elif 'grade=' in cql:
        return Q(Q(grade_id__grade_name = word) | Q(grade_id__grade_abbrev = word))

    # Обработка токенов с указанными причинами ошибки
    elif 'reason=' in cql:
        return Q(Q(reason_id__reason_name = word) | Q(reason_id__reason_abbrev = word))
        
    # Обработка токенов не соответсвующих словоформе
    if 'word!=' in cql:
        # REGEX
        if word[0:2] == '.*' and word[-2:] == '.*':
            return ~Q(token_id__text__contains=word[2:-2])
        elif word[-2:] == '.*':
            return ~Q(token_id__text__startswith=word[:-2])
        elif word[0:2] == '.*':
            return ~Q(token_id__text__endswith=word[2:])
        else:
            return ~Q(token_id__text__iexact=word)

    # Обрабокта токенов без указанных тегов ошибок и частеречной разметки
    elif 'error!=' in cql or 'pos!=' in cql:
        return ~Q(Q(tag_id__tag_text = word) | Q(tag_id__tag_text_russian = word) | Q(tag_id__tag_text_abbrev = word) )

    # Обрабокта токенов без указанных степеней грубости ошибки
    elif 'grade!=' in cql:
        return ~Q(Q(grade_id__grade_name = word) | Q(grade_id__grade_abbrev = word))

    # Обрабокта токенов без указанных причин ошибки
    elif 'reason!=' in cql:
        return ~Q(Q(reason_id__reason_name = word) | Q(reason_id__reason_abbrev = word))
    
    return None


def _parse_cql(user_query=None):
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
            return render(request, "search.html",
                          context={'error_search': 'Text not Found', 'search_value': request.POST['corpus_search']})

        # Получение строк по заданным условиям
        sentence_objects = TblMarkup.objects.filter(filters).values(
            'token_id', 'token_id__sentence_id', 'token_id__sentence_id__text_id__header',
            'token_id__sentence_id__text_id__create_date'
        )

        # TODO: пропписать исключение
        if len(sentence_objects) == 0:
            return render(request, "search.html",
                          context={'error_search': 'Text not Found', 'search_value': request.POST['corpus_search']})

        # Количество найденных предложений
        count_search = len(sentence_objects)

        sentence_objects = sentence_objects[:100]

        list_search = []
        for sentence in sentence_objects:
            tokens = TblToken.objects.filter(
                sentence_id=sentence['token_id__sentence_id']
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

        return render(request, "search.html",
                      context={'search_value': request.POST['corpus_search'], 'list_search': list_search,
                               'count_search': count_search})

    else:
        return redirect(request, 'home')


def get_stat(request):
    if request.user.is_teacher():
        if request.method != 'POST':
            return (render(request, 'stat_form.html',
                           {'right': True, 'form': StatisticForm(request.user.language_id), 'no_data': False}))
        else:
            form = StatisticForm(request.user.language_id, request.POST or None)
            if form.is_valid():

                group_id = int(form.cleaned_data['group'])

                stat_res = built_group_stat(group_id, request.user.id_user)
                if stat_res['state']:

                    response = HttpResponse(FileWrapper(open(stat_res['folder_link'], 'rb')),
                                            content_type='application/zip')

                    filename = stat_res['file_name'].replace(" ", "_")
                    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

                    remove(stat_res['folder_link'])
                    return response

                else:
                    return render(request, 'stat_form.html',
                                  {'right': True, 'form': StatisticForm(request.user.language_id), 'no_data': True})
    else:
        return render(request, 'stat_form.html', {'right': False, 'no_data': False})


def get_error_stats(request_data):
    # получаем список ошибок
    tags = TblTag.objects.filter(tag_language_id=1)
    data = []
    for tag_item in tags:
        stat_item = {'id_tag': tag_item.id_tag, 'tag_name': tag_item.tag_text, 'tag_desc': tag_item.tag_text_russian}
        # ищем использование ошибки
        degree1 = TblMarkup.objects.filter(tag_id=tag_item.id_tag, grade_id=1)
        stat_item["degree1_count"] = len(degree1)
        stat_item["degree1_sample"] = ""
        if len(degree1) != 0:
            token = TblToken.objects.filter(id_token=degree1[0].token_id).get()
            sentence = TblSentence.objects.filter(Q(id_sentence=token.sentence_id)).get()
            text = TblText.objects.filter(Q(header=sentence.text_id)).get()
            text_type = TblTextType.objects.filter(Q(id_text_type=text.text_type_id)).get()
            stat_item["degree1_sample"] = f"/corpus/Deutsche/{text_type.text_type_name}/{text.id_text}?token={degree1[0].token_id}"

        degree2 = TblMarkup.objects.filter(tag_id=tag_item.id_tag, grade_id=2)
        stat_item["degree2_count"] = len(degree2)
        if len(degree2) != 0:
            token = TblToken.objects.filter(id_token=degree2[0].token_id).get()
            sentence = TblSentence.objects.filter(Q(id_sentence=token.sentence_id)).get()
            text = TblText.objects.filter(Q(header=sentence.text_id)).get()
            text_type = TblTextType.objects.filter(Q(id_text_type=text.text_type_id)).get()
            stat_item["degree2_sample"] = f"/corpus/Deutsche/{text_type.text_type_name}/{text.id_text}?token={degree2[0].token_id}"

        degree3 = TblMarkup.objects.filter(tag_id=tag_item.id_tag, grade_id=3)
        stat_item["degree3_count"] = len(degree3)
        if len(degree3) != 0:
            text = TblToken.objects.filter(id_token=degree3[0].token_id).values(
                'sentence_id__text_id',
                'sentence_id__text_id__text_type_id__text_type_name'
            )
            stat_item["degree3_sample"] = f"/corpus/Deutsche/{text.sentence_id__text_id}/{text.sentence_id__text_id__text_type_id__text_type_name}?token={degree3[0].token_id}"

        stat_item['is_normal'] = "none"
        if stat_item['degree1_count'] != 0 and stat_item['degree2_count'] != 0 and stat_item['degree3_count'] != 0:
            stat_item['is_normal'] = "coral"
        elif (stat_item['degree1_count'] != 0 and stat_item['degree2_count'] != 0) or \
                (stat_item['degree1_count'] != 0 and stat_item['degree3_count'] != 0) or \
                (stat_item['degree2_count'] != 0 and stat_item['degree3_count'] != 0):
            stat_item['is_normal'] = "khaki"

        data.append(stat_item)
    return render(request_data, 'error_stats.html', {'error_data': data})
