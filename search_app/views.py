import re
import urllib
from os import remove
from wsgiref.util import FileWrapper

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from pakt_work_tools.custom_settings import AUTO_STAT
from text_app.models import TblMarkup, TblToken, TblTag, TblText, TblGrade, TblReason
from user_app.models import TblLanguage
from .forms import StatisticForm
from .models import TblSystemMetric
from .stat_src import built_group_stat


def index(request):
    """ Рендер главной страницы

    Args:
        request: http-запрос с пользовательской информацией

    Returns:
        HttpResponse: html главной страницы
    """
    current_time = timezone.now()
    out_time = current_time
    out_metrics = []
    metrics = TblSystemMetric.objects.filter(
        metric_name='token_counter').order_by('id_metric').values().all()

    if len(metrics) == 0:
        # если метрик еще нет, то считаем по всем языкам
        langs = TblLanguage.objects.all()
        for lang in langs:
            try:
                out_metrics.append(int(TblToken.objects.filter(
                    Q(sentence_id__text_id__language_id=lang.id_language) & ~Q(text='-EMPTY-')).count()))
            except:
                out_metrics.append(0)

        for lang in langs:
            token_counter = TblSystemMetric(metric_name='token_counter',
                                            language_id=lang.id_language,
                                            metric_value=out_metrics[lang.id_language - 1],
                                            metric_update_time=current_time)
            token_counter.save()

    elif (current_time - metrics[0]['metric_update_time']).total_seconds() >= AUTO_STAT['update_interval']:
        # если метрики устарели
        for idx in range(len(metrics)):
            try:
                out_metrics.append(int(TblToken.objects.filter(
                    Q(sentence_id__text_id__language_id=metrics[idx]['language_id']) & ~Q(text='-EMPTY-')).count()))
            except:
                out_metrics.append(0)

        TblSystemMetric.objects.filter(metric_name='token_counter').update(
            metric_update_time=current_time)
        TblSystemMetric.objects.filter(Q(metric_name='token_counter') & Q(language_id=1)).update(
            metric_value=out_metrics[0])
        TblSystemMetric.objects.filter(Q(metric_name='token_counter') & Q(language_id=2)).update(
            metric_value=out_metrics[1])

    else:
        # если метрики актуальны
        out_metrics = [int(metrics[index]['metric_value'])
                       for index in range(len(metrics))]
        out_time = metrics[0]['metric_update_time']

    if len(out_metrics) == 0:  # если метрики еще не созданы
        out_metrics = [0, 0]

    return render(request, "home.html", context={
        'tokens_count': {1: out_metrics[0], 2: out_metrics[1]},
        'update_time': out_time.strftime("%d.%m.%Y %H:%M:%S")
    })


def cql_faq(request):
    """ Рендер FAQ по CQL

    Args:
        request: http-запрос с пользовательской информацией

    Returns:
        HttpResponse: html FQL по CQL
    """

    return render(request, "cql_faq.html")


def tag_list(request):
    """ Рендер справочника по тегам

    Args:
        request: http-запрос с пользовательской информацией

    Returns:
        HttpResponse: html Справочник тегов
    """

    deutsche_reasons = TblReason.objects.filter(reason_language_id=1).values(
        'reason_name', 'reason_abbrev')

    deutsche_grades = TblGrade.objects.filter(grade_language_id=1).values(
        'grade_name', 'grade_abbrev')

    deutsche_error_tags = TblTag.objects.filter(markup_type_id=1, tag_language_id=1).values(
        'tag_text', 'tag_text_russian', 'tag_text_abbrev')

    deutsche_pos_tags = TblTag.objects.filter(markup_type_id=2, tag_language_id=1).values(
        'tag_text')

    return render(request, "tag_list.html", {'deutsche_reasons': deutsche_reasons, 'deutsche_grades': deutsche_grades, 'deutsche_error_tags': deutsche_error_tags, 'deutsche_pos_tags': deutsche_pos_tags, })


def _filter_shaping(cql):
    """Формирование фильтра на основе cql

    Keyword arguments:
    cql -- Запроса пользователя

    """

    # Получение аттрибута запроса
    content = re.search(r'[\'\"\”].*[\'\"\”]', cql)
    if content is not None:
        word = content.group(0)[1:-1]
    else:
        word = content

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
        return Q(Q(tag_id__tag_text=word) | Q(tag_id__tag_text_russian=word) | Q(tag_id__tag_text_abbrev=word))

    # Обработка токенов с указанными степенями грубости ошибки
    elif 'grade=' in cql:
        return Q(Q(grade_id__grade_name=word) | Q(grade_id__grade_abbrev=word))

    # Обработка токенов с указанными причинами ошибки
    elif 'reason=' in cql:
        return Q(Q(reason_id__reason_name=word) | Q(reason_id__reason_abbrev=word))

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
        return ~Q(Q(tag_id__tag_text=word) | Q(tag_id__tag_text_russian=word) | Q(tag_id__tag_text_abbrev=word))

    # Обрабокта токенов без указанных степеней грубости ошибки
    elif 'grade!=' in cql:
        return ~Q(Q(grade_id__grade_name=word) | Q(grade_id__grade_abbrev=word))

    # Обрабокта токенов без указанных причин ошибки
    elif 'reason!=' in cql:
        return ~Q(Q(reason_id__reason_name=word) | Q(reason_id__reason_abbrev=word))

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
    user_query = ""

    if request.POST:
        user_query = request.POST.get('corpus_search', "")
    else:
        user_query = request.GET.get('corpus_search', "")

    filters = _parse_cql(user_query)
    if filters is None:
        return render(request, "search.html",
                      context={'error_search': 'Text not Found', 'search_value': user_query})

    # Получение строк по заданным условиям
    sentence_objects = TblMarkup.objects.filter(filters).values(
        'token_id', 'token_id__sentence_id', 'token_id__sentence_id__text_id__header',
        'token_id__sentence_id__text_id__language_id__language_name',
        'token_id__sentence_id__text_id__text_type_id__text_type_name',
        'token_id__sentence_id__text_id__create_date', 'token_id__sentence_id__text_id'
    )

    # TODO: пропписать исключение
    if len(sentence_objects) == 0:
        return render(request, "search.html",
                      context={'error_search': 'Text not Found', 'search_value': user_query})

    # Количество найденных предложений
    count_search = len(sentence_objects)

    sentence_objects = sentence_objects

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
            'language': sentence['token_id__sentence_id__text_id__language_id__language_name'],
            'text_type': sentence['token_id__sentence_id__text_id__text_type_id__text_type_name'],
            'tokens': list_token,
            'create_date': sentence['token_id__sentence_id__text_id__create_date'],
            'text_id': sentence['token_id__sentence_id__text_id'],
        })

    # Для неточного поиска
    # MyClass.objects.filter(name__iexact=my_parameter)

    return render(request, "search.html",
                  context={'search_value': user_query, 'list_search': list_search,
                           'count_search': count_search, 'is_registered': hasattr(request.user, 'id_user')})


def text(request, text_id=None):
    text_obj = TblText.objects.filter(id_text=text_id).values(
        'text', 'header', 'language_id__language_name', 'text_type_id__text_type_name'
    )

    if len(text_obj) == 0:
        return render(request, "corpus.html", context={'error_search': 'Text not Found'}, status=404)

    text_obj = text_obj[0]
    text_data = re.sub(" -EMPTY- ", " ", text_obj['text'])
    header = text_obj['header']
    language = text_obj['language_id__language_name']
    text_type = text_obj['text_type_id__text_type_name']
    text_path = str(language) + '/' + str(text_type) + '/' + str(header)

    return (render(request, "search_text.html", context={'text': text_data, 'text_path': text_path, 'text_id': text_id,
                                                         'language_name': language, 'text_type_name': text_type}))


def get_stat(request):
    if hasattr(request.user, 'is_teacher') and request.user.is_teacher():
        if request.method != 'POST':
            return (render(request, 'stat_form.html',
                           {'right': True, 'form': StatisticForm(request.user.language_id), 'no_data': False}))
        else:
            form = StatisticForm(request.user.language_id,
                                 request.POST or None)
            if form.is_valid():

                group_id = int(form.cleaned_data['group'])

                stat_res = built_group_stat(group_id, request.user.id_user)
                if stat_res['state']:

                    response = HttpResponse(FileWrapper(open(stat_res['folder_link'], 'rb')),
                                            content_type='application/zip')

                    filename = stat_res['file_name'].replace(" ", "_")
                    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
                        filename)

                    remove(stat_res['folder_link'])
                    return response

                else:
                    return render(request, 'stat_form.html',
                                  {'right': True, 'form': StatisticForm(request.user.language_id), 'no_data': True})
    else:
        return render(request, 'stat_form.html', {'right': False, 'no_data': False}, status=403)


def get_error_stats(request_data):
    # получаем список ошибок
    tags = TblTag.objects.filter(tag_language_id=1)
    grades = TblGrade.objects.filter(grade_language_id=1)
    grade1 = ""
    grade2 = ""
    grade3 = ""
    for grade in grades:
        if grade.id_grade == 1:
            grade1 = grade.grade_abbrev
            if grade1 is None:
                grade1 = grade.grade_name
        if grade.id_grade == 2:
            grade2 = grade.grade_abbrev
            if grade2 is None:
                grade2 = grade.grade_name
        if grade.id_grade == 3:
            grade3 = grade.grade_abbrev
            if grade3 is None:
                grade3 = grade.grade_name

    data = []
    for tag_item in tags:
        stat_item = {'id_tag': tag_item.id_tag, 'tag_name': tag_item.tag_text, 'tag_desc': tag_item.tag_text_russian,
                     'tag_text_abbrev': tag_item.tag_text_abbrev}
        # ищем использование ошибки
        degree1 = TblMarkup.objects.filter(tag_id=tag_item.id_tag, grade_id=1)
        stat_item["degree1_count"] = len(degree1)
        stat_item["degree1_name"] = grade1
        if len(degree1) != 0:
            stat_item["degree1_sample"] = "corpus_search=" + urllib.parse.quote(
                f"[grade=\"{grade1}\" & error=\"{tag_item.tag_text_abbrev}\"]")

        degree2 = TblMarkup.objects.filter(tag_id=tag_item.id_tag, grade_id=2)
        stat_item["degree2_count"] = len(degree2)
        stat_item["degree2_name"] = grade2
        if len(degree2) != 0:
            stat_item["degree2_sample"] = "corpus_search=" + urllib.parse.quote(
                f"[grade=\"{grade2}\" & error=\"{tag_item.tag_text_abbrev}\"]")

        degree3 = TblMarkup.objects.filter(tag_id=tag_item.id_tag, grade_id=3)
        stat_item["degree3_count"] = len(degree3)
        stat_item["degree3_name"] = grade3
        if len(degree3) != 0:
            stat_item["degree3_sample"] = "corpus_search=" + urllib.parse.quote(
                f"[grade=\"{grade3}\" & error=\"{tag_item.tag_text_abbrev}\"]")

        stat_item['is_normal'] = "none"
        if stat_item['degree1_count'] != 0 and stat_item['degree2_count'] != 0 and stat_item['degree3_count'] != 0:
            stat_item['is_normal'] = "coral"
        elif (stat_item['degree1_count'] != 0 and stat_item['degree2_count'] != 0) or \
                (stat_item['degree1_count'] != 0 and stat_item['degree3_count'] != 0) or \
                (stat_item['degree2_count'] != 0 and stat_item['degree3_count'] != 0):
            stat_item['is_normal'] = "khaki"

        data.append(stat_item)
    return render(request_data, 'error_stats.html', {'error_data': data})
