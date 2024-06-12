from text_app.models import TblTag, TblToken, TblText, TblTextType, TblGrade, TblEmotional
from .models import TblLanguage, TblGroup
from django.db.models import Q
from django.db.models import Count, F, Value, IntegerField
import numpy as np
import scipy
import pandas as pd
import math


def get_levels_dfs(v, level, max_level, h, tags):
    h[v] = 1
    level += 1

    for i in range(len(tags)):
        if tags[i]["tag_parent"] == tags[v]["id_tag"] and h[i] == 0:
            max_level = get_levels_dfs(i, level, max_level, h, tags)

    if max_level < level:
        max_level = level

    return max_level


def get_levels():
    languages = list(TblLanguage.objects.values('id_language'))
    levels = []

    for language in languages:
        tags = list(TblTag.objects.values('id_tag', 'tag_parent').filter(
            Q(markup_type=1) & Q(tag_language=language['id_language'])))

        n = len(tags)
        h = [0 for _ in range(n)]
        max_level = 0

        for i in range(n):
            if h[i] == 0 and tags[i]["tag_parent"] is None:
                level = get_levels_dfs(i, 0, -1, h, tags)
                if level > max_level:
                    max_level = level

        for i in range(max_level):
            if i == 0:
                levels.append(
                    {'id_level': i, 'level_text': f'{i} - верхний уровень', 'level_language': language['id_language']})
            elif i == max_level - 1:
                levels.append(
                    {'id_level': i, 'level_text': f'{i} - нижний уровень', 'level_language': language['id_language']})
            else:
                levels.append(
                    {'id_level': i, 'level_text': f'{i} - подуровень {i}', 'level_language': language['id_language']})

    return levels


def get_texts_id_keys(data_count, texts_id, label_language):
    for data in data_count:
        if data[label_language] not in texts_id.keys():
            texts_id[data[label_language]] = []

    return texts_id


def get_texts_id_and_data_on_tokens(data_count, texts_id, id_data, label_language):
    data_count_on_tokens = []
    id_data_count_on_tokens = []

    for data in data_count:
        if data['sentence__text_id'] not in texts_id[data[label_language]]:
            texts_id[data[label_language]].append(data['sentence__text_id'])

        if data[id_data] not in id_data_count_on_tokens:
            id_data_count_on_tokens.append(data[id_data])
            del data['sentence__text_id']
            data_count_on_tokens.append(data)
        else:
            idx = 0
            while data_count_on_tokens[idx][id_data] != data[id_data]:
                idx += 1
            data_count_on_tokens[idx]['count_data'] += data['count_data']

    return data_count_on_tokens, texts_id


def get_on_tokens(texts_id, data_count, label_language):
    count_tokens = {}
    for language in texts_id.keys():
        count_tokens_language = TblToken.objects.filter(sentence__text_id__in=texts_id[language]).aggregate(
            res=Count('sentence__text_id'))
        count_tokens[language] = count_tokens_language['res']

    for data in data_count:
        data['count_data_on_tokens'] = data['count_data'] * 100 / count_tokens[data[label_language]]

    return data_count


def get_data_on_tokens(data_count, id_data, label_language, is_unique_data, is_for_one_group):
    texts_id = {}
    texts_id = get_texts_id_keys(data_count, texts_id, label_language)

    if is_for_one_group:
        count_errors = 0

        for data in data_count:
            if data['sentence__text_id'] not in texts_id[data[label_language]]:
                texts_id[data[label_language]].append(data['sentence__text_id'])
            count_errors += data['count_data']

        count_tokens = {}
        for language in texts_id.keys():
            count_tokens_language = TblToken.objects.filter(sentence__text_id__in=texts_id[language]).aggregate(
                res=Count('sentence__text_id'))
            count_tokens[language] = count_tokens_language['res']

        data_count[0]['count_data'] = count_errors
        data_count[0]['count_data_on_tokens'] = count_errors * 100 / count_tokens[data_count[0][label_language]]

        return [data_count[0]]

    if is_unique_data:
        data_count_on_tokens, texts_id = get_texts_id_and_data_on_tokens(data_count, texts_id, id_data, label_language)
        data_count_on_tokens = get_on_tokens(texts_id, data_count_on_tokens, label_language)
        return data_count_on_tokens

    for data in data_count:
        count_tokens = TblToken.objects.filter(sentence__text_id=data['sentence__text_id']).aggregate(
            res=Count('sentence__text_id'))
        data['count_data_on_tokens'] = data['count_data'] * 100 / count_tokens['res']

    return data_count


def get_data_errors_dfs(v, d, d_on_tokens, level, level_input, h, flags_levels, data):
    h[v] = 1
    level += 1

    for i in range(len(data)):
        if data[i]["tag__tag_parent"] == data[v]["tag__id_tag"] and h[i] == 0:
            c, c_on_tokens = get_data_errors_dfs(i, d, d_on_tokens, level, level_input, h, flags_levels, data)
            d = c
            d_on_tokens = c_on_tokens

    if level > level_input:
        return data[v]["count_data"] + d, data[v]["count_data_on_tokens"] + d_on_tokens
    else:
        flags_levels[v] = True
        data[v]["count_data"] += d
        data[v]['count_data_on_tokens'] += d_on_tokens
        return 0, 0


def get_data_errors(data_count_errors, level, is_sorted):
    list_tags_id_in_markup = []
    for data in data_count_errors:
        list_tags_id_in_markup.append(data["tag__id_tag"])

    data_tags_not_in_errors = list(TblTag.objects.annotate(tag__id_tag=F('id_tag'), tag__tag_parent=F('tag_parent'),
                                                           tag__tag_language=F('tag_language'),
                                                           tag__tag_text=F('tag_text'),
                                                           tag__tag_text_russian=F('tag_text_russian')).values(
        'tag__id_tag', 'tag__tag_parent', 'tag__tag_language', 'tag__tag_text', 'tag__tag_text_russian').filter(
        Q(markup_type=1) & ~Q(id_tag__in=list_tags_id_in_markup)).annotate(
        count_data=Value(0, output_field=IntegerField()), count_data_on_tokens=Value(0, output_field=IntegerField())))

    data = data_count_errors + data_tags_not_in_errors

    n = len(data)
    h = [0 for _ in range(n)]
    flags_levels = [False for _ in range(n)]

    for i in range(n):
        if h[i] == 0 and data[i]["tag__tag_parent"] is None:
            get_data_errors_dfs(i, 0, 0, -1, level, h, flags_levels, data)

    data_grouped = []
    for i in range(n):
        if flags_levels[i]:
            if data[i]["tag__tag_parent"] is None:
                data[i]["tag__tag_parent"] = -1
            data_grouped.append(data[i])

    if is_sorted:
        data = sorted(data_grouped, key=lambda d: d['count_data'], reverse=True)
    else:
        data = sorted(data_grouped, key=lambda d: d['tag__id_tag'])

    return data


def get_enrollment_date(list_filters):
    group = list_filters['group']
    text = list_filters['text']
    text_type = list_filters['text_type']

    if text and text_type:
        enrollment_date = list(TblGroup.objects.values('enrollment_date').filter(
            Q(group_name=group) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                tbltextgroup__text_id__header=text) & Q(
                tbltextgroup__text_id__text_type=text_type)).distinct().order_by('enrollment_date'))
    elif text:
        enrollment_date = list(TblGroup.objects.values('enrollment_date').filter(
            Q(group_name=group) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                tbltextgroup__text_id__header=text)).distinct().order_by('enrollment_date'))
    elif text_type:
        enrollment_date = list(TblGroup.objects.values('enrollment_date').filter(
            Q(group_name=group) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                tbltextgroup__text_id__text_type=text_type)).distinct().order_by('enrollment_date'))
    else:
        enrollment_date = list(
            TblGroup.objects.values('enrollment_date').filter(group_name=group).distinct().order_by(
                'enrollment_date'))

    for date in enrollment_date:
        date['enrollment_date'] = str(date['enrollment_date'].year) + ' \ ' \
                                  + str(date['enrollment_date'].year + 1)

    return enrollment_date


def get_filters_for_choice_all(list_filters):
    text = list_filters['text']
    text_type = list_filters['text_type']

    if text_type:
        texts = list(TblText.objects.values('header', 'language').filter(
            Q(error_tag_check=1) & Q(text_type=text_type)).distinct().order_by('header'))
    else:
        texts = list(
            TblText.objects.values('header', 'language').filter(error_tag_check=1).distinct().order_by(
                'header'))

    if text:
        text_types = list(TblTextType.objects.values().filter(
            Q(tbltext__error_tag_check=1) & Q(tbltext__header=text)).distinct().order_by('id_text_type'))
    else:
        text_types = list(
            TblTextType.objects.values().filter(tbltext__error_tag_check=1).distinct().order_by('id_text_type'))

    return texts, text_types


def get_filters_for_choice_group(list_filters):
    group = list_filters['group']
    text = list_filters['text']
    text_type = list_filters['text_type']

    date = list_filters['enrollment_date']
    group_date = date[:4] + '-09-01'

    if text_type:
        texts = list(TblText.objects.values('header', 'language').filter(
            Q(error_tag_check=1) & Q(tbltextgroup__group__group_name=group) & Q(
                tbltextgroup__group__enrollment_date=group_date) & Q(text_type=text_type)).distinct().order_by(
            'header'))
    else:
        texts = list(TblText.objects.values('header', 'language').filter(
            Q(error_tag_check=1) & Q(tbltextgroup__group__group_name=group) & Q(
                tbltextgroup__group__enrollment_date=group_date)).distinct().order_by('header'))

    if text:
        text_types = list(TblTextType.objects.values().filter(
            Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__group_name=group) & Q(
                tbltext__tbltextgroup__group__enrollment_date=group_date) & Q(
                tbltext__header=text)).distinct().order_by('id_text_type'))
    else:
        text_types = list(TblTextType.objects.values().filter(
            Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__group_name=group) & Q(
                tbltext__tbltextgroup__group__enrollment_date=group_date)).distinct().order_by('id_text_type'))

    return texts, text_types


def get_filters_for_choice_student(list_filters):
    surname = list_filters['surname']
    name = list_filters['name']
    patronymic = list_filters['patronymic']
    text = list_filters['text']
    text_type = list_filters['text_type']

    if patronymic:
        if text:
            text_types = list(TblTextType.objects.values().filter(
                Q(tbltext__error_tag_check=1) & Q(tbltext__user__last_name=surname) & Q(tbltext__user__name=name) & Q(
                    tbltext__user__patronymic=patronymic) & Q(tbltext__header=text)).distinct().order_by(
                'id_text_type'))
        else:
            text_types = list(TblTextType.objects.values().filter(
                Q(tbltext__error_tag_check=1) & Q(tbltext__user__last_name=surname) & Q(tbltext__user__name=name) & Q(
                    tbltext__user__patronymic=patronymic)).distinct().order_by('id_text_type'))

        if text_type:
            texts = list(TblText.objects.values('header', 'language').filter(
                Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                    user__patronymic=patronymic) & Q(text_type=text_type)).distinct().order_by('header'))
        else:
            texts = list(TblText.objects.values('header', 'language').filter(
                Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                    user__patronymic=patronymic)).distinct().order_by('header'))
    else:
        if text:
            text_types = list(TblTextType.objects.values().filter(
                Q(tbltext__error_tag_check=1) & Q(tbltext__user__last_name=surname) & Q(tbltext__user__name=name) & Q(
                    tbltext__header=text)).distinct().order_by('id_text_type'))
        else:
            text_types = list(TblTextType.objects.values().filter(
                Q(tbltext__error_tag_check=1) & Q(tbltext__user__last_name=surname) & Q(
                    tbltext__user__name=name)).distinct().order_by('id_text_type'))

        if text_type:
            texts = list(TblText.objects.values('header', 'language').filter(
                Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                    text_type=text_type)).distinct().order_by('header'))
        else:
            texts = list(TblText.objects.values('header', 'language').filter(
                Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name)).distinct().order_by('header'))

    return texts, text_types


def get_filters_for_choice_course(list_filters):
    course = list_filters['course']
    text = list_filters['text']
    text_type = list_filters['text_type']

    if text_type:
        texts = list(TblText.objects.values('header', 'language').filter(
            Q(error_tag_check=1) & Q(tbltextgroup__group__course_number=course) & Q(
                text_type=text_type)).distinct().order_by('header'))
    else:
        texts = list(TblText.objects.values('header', 'language').filter(
            Q(error_tag_check=1) & Q(tbltextgroup__group__course_number=course)).distinct().order_by('header'))

    if text:
        text_types = list(TblTextType.objects.values().filter(
            Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__course_number=course) & Q(
                tbltext__header=text)).distinct().order_by('id_text_type'))
    else:
        text_types = list(TblTextType.objects.values().filter(Q(tbltext__error_tag_check=1) & Q(
            tbltext__tbltextgroup__group__course_number=course)).distinct().order_by('id_text_type'))

    return texts, text_types


def get_filters_for_choice_text(list_filters):
    group = list_filters['group']
    date = list_filters['enrollment_date']
    surname = list_filters['surname']
    name = list_filters['name']
    patronymic = list_filters['patronymic']
    course = list_filters['course']
    text = list_filters['text']
    text_type = list_filters['text_type']

    if 'emotion' in list_filters:
        emotion = list_filters['emotion']
    else:
        emotion = ''

    if 'self_rating' in list_filters:
        self_rating = list_filters['self_rating']
    else:
        self_rating = ''

    if emotion:
        if text:
            if group:
                group_date = date[:4] + '-09-01'
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__group_name=group) & Q(
                        tbltext__tbltextgroup__group__enrollment_date=group_date) & Q(tbltext__header=text) & Q(
                        tbltext__emotional=emotion)).distinct().order_by('id_text_type'))
            elif surname and name and patronymic:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name) & Q(tbltext__user__patronymic=patronymic) & Q(
                        tbltext__emotional=emotion)).distinct().order_by('id_text_type'))
            elif surname and name:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name) & Q(tbltext__emotional=emotion)).distinct().order_by('id_text_type'))
            elif course:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(
                        tbltext__tbltextgroup__group__course_number=course) & Q(
                        tbltext__emotional=emotion)).distinct().order_by('id_text_type'))
            else:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(
                        tbltext__emotional=emotion)).distinct().order_by('id_text_type'))

            if text_type:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text) & Q(tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('course_number'))
        else:
            if group:
                group_date = date[:4] + '-09-01'
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__group_name=group) & Q(
                        tbltext__tbltextgroup__group__enrollment_date=group_date) & Q(
                        tbltext__emotional=emotion)).distinct().order_by('id_text_type'))
            elif surname and name and patronymic:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name) & Q(tbltext__user__patronymic=patronymic) & Q(
                        tbltext__emotional=emotion)).distinct().order_by('id_text_type'))
            elif surname and name:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name) & Q(tbltext__emotional=emotion)).distinct().order_by('id_text_type'))
            elif course:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__course_number=course) & Q(
                        tbltext__emotional=emotion)).distinct().order_by('id_text_type'))
            else:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__emotional=emotion)).distinct().order_by('id_text_type'))

            if text_type:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('group_name'))
                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    tbltextgroup__text__emotional=emotion).distinct().order_by('group_name'))
                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text__emotional=emotion)).distinct().order_by(
                    'course_number'))
    elif self_rating:
        if text:
            if group:
                group_date = date[:4] + '-09-01'
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__group_name=group) & Q(
                        tbltext__tbltextgroup__group__enrollment_date=group_date) & Q(tbltext__header=text) & Q(
                        tbltext__self_rating=self_rating)).distinct().order_by('id_text_type'))
            elif surname and name and patronymic:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name) & Q(tbltext__user__patronymic=patronymic) & Q(
                        tbltext__self_rating=self_rating)).distinct().order_by('id_text_type'))
            elif surname and name:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name) & Q(tbltext__self_rating=self_rating)).distinct().order_by(
                    'id_text_type'))
            elif course:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(
                        tbltext__tbltextgroup__group__course_number=course) & Q(
                        tbltext__self_rating=self_rating)).distinct().order_by('id_text_type'))
            else:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(
                        tbltext__self_rating=self_rating)).distinct().order_by('id_text_type'))

            if text_type:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text) & Q(tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('course_number'))
        else:
            if group:
                group_date = date[:4] + '-09-01'
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__group_name=group) & Q(
                        tbltext__tbltextgroup__group__enrollment_date=group_date) & Q(
                        tbltext__self_rating=self_rating)).distinct().order_by('id_text_type'))
            elif surname and name and patronymic:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name) & Q(tbltext__user__patronymic=patronymic) & Q(
                        tbltext__self_rating=self_rating)).distinct().order_by('id_text_type'))
            elif surname and name:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name) & Q(tbltext__self_rating=self_rating)).distinct().order_by(
                    'id_text_type'))
            elif course:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__course_number=course) & Q(
                        tbltext__self_rating=self_rating)).distinct().order_by('id_text_type'))
            else:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__self_rating=self_rating)).distinct().order_by(
                    'id_text_type'))

            if text_type:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('group_name'))
                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    tbltextgroup__text__self_rating=self_rating).distinct().order_by('group_name'))
                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text__self_rating=self_rating)).distinct().order_by(
                    'course_number'))
    else:
        if text:
            if group:
                group_date = date[:4] + '-09-01'
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__group_name=group) & Q(
                        tbltext__tbltextgroup__group__enrollment_date=group_date) & Q(
                        tbltext__header=text)).distinct().order_by('id_text_type'))
            elif surname and name and patronymic:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name) & Q(tbltext__user__patronymic=patronymic)).distinct().order_by(
                    'id_text_type'))
            elif surname and name:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name)).distinct().order_by('id_text_type'))
            elif course:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text) & Q(
                        tbltext__tbltextgroup__group__course_number=course)).distinct().order_by('id_text_type'))
            else:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__header=text)).distinct().order_by('id_text_type'))

            if text_type:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text_id__text_type=text_type)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text_id__text_type=text_type)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text)).distinct().order_by('course_number'))
        else:
            if group:
                group_date = date[:4] + '-09-01'
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__tbltextgroup__group__group_name=group) & Q(
                        tbltext__tbltextgroup__group__enrollment_date=group_date)).distinct().order_by('id_text_type'))
            elif surname and name and patronymic:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name) & Q(tbltext__user__patronymic=patronymic)).distinct().order_by(
                    'id_text_type'))
            elif surname and name:
                text_types = list(TblTextType.objects.values().filter(
                    Q(tbltext__error_tag_check=1) & Q(tbltext__user__last_name=surname) & Q(
                        tbltext__user__name=name)).distinct().order_by('id_text_type'))
            elif course:
                text_types = list(TblTextType.objects.values().filter(Q(tbltext__error_tag_check=1) & Q(
                    tbltext__tbltextgroup__group__course_number=course)).distinct().order_by('id_text_type'))
            else:
                text_types = list(
                    TblTextType.objects.values().filter(tbltext__error_tag_check=1).distinct().order_by('id_text_type'))

            if text_type:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').distinct().order_by('group_name'))
                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    course_number__gt=0).distinct().order_by('course_number'))

    return groups, courses, text_types


def get_filters_for_choice_text_type(list_filters):
    group = list_filters['group']
    date = list_filters['enrollment_date']
    surname = list_filters['surname']
    name = list_filters['name']
    patronymic = list_filters['patronymic']
    course = list_filters['course']
    text_type = list_filters['text_type']
    text = list_filters['text']

    if 'emotion' in list_filters:
        emotion = list_filters['emotion']
    else:
        emotion = ''

    if 'self_rating' in list_filters:
        self_rating = list_filters['self_rating']
    else:
        self_rating = ''

    if emotion:
        if text_type:
            if group:
                group_date = date[:4] + '-09-01'
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(tbltextgroup__group__group_name=group) & Q(
                        tbltextgroup__group__enrollment_date=group_date) & Q(emotional=emotion)).distinct().order_by(
                    'header'))
            elif surname and name and patronymic:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                        user__patronymic=patronymic) & Q(emotional=emotion)).distinct().order_by('header'))
            elif surname and name:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                        emotional=emotion)).distinct().order_by('header'))
            elif course:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(tbltextgroup__group__course_number=course) & Q(
                        emotional=emotion)).distinct().order_by('header'))
            else:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(emotional=emotion)).distinct().order_by('header'))

            if text:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('course_number'))
        else:
            if group:
                group_date = date[:4] + '-09-01'
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(tbltextgroup__group__group_name=group) & Q(
                        tbltextgroup__group__enrollment_date=group_date) & Q(emotional=emotion)).distinct().order_by(
                    'header'))
            elif surname and name and patronymic:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                        user__patronymic=patronymic) & Q(emotional=emotion)).distinct().order_by('header'))
            elif surname and name:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                        emotional=emotion)).distinct().order_by('header'))
            elif course:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(tbltextgroup__group__course_number=course) & Q(
                        emotional=emotion)).distinct().order_by('header'))
            else:
                texts = list(
                    TblText.objects.values('header', 'language').filter(Q(error_tag_check=1) & Q(
                        emotional=emotion)).distinct().order_by('header'))

            if text:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__emotional=emotion)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    tbltextgroup__text__emotional=emotion).distinct().order_by('group_name'))
                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text__emotional=emotion)).distinct().order_by(
                    'course_number'))
    elif self_rating:
        if text_type:
            if group:
                group_date = date[:4] + '-09-01'
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(tbltextgroup__group__group_name=group) & Q(
                        tbltextgroup__group__enrollment_date=group_date) & Q(
                        self_rating=self_rating)).distinct().order_by('header'))
            elif surname and name and patronymic:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                        user__patronymic=patronymic) & Q(self_rating=self_rating)).distinct().order_by('header'))
            elif surname and name:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                        self_rating=self_rating)).distinct().order_by('header'))
            elif course:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(tbltextgroup__group__course_number=course) & Q(
                        self_rating=self_rating)).distinct().order_by('header'))
            else:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(self_rating=self_rating)).distinct().order_by(
                    'header'))

            if text:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('course_number'))
        else:
            if group:
                group_date = date[:4] + '-09-01'
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(tbltextgroup__group__group_name=group) & Q(
                        tbltextgroup__group__enrollment_date=group_date) & Q(
                        self_rating=self_rating)).distinct().order_by('header'))
            elif surname and name and patronymic:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                        user__patronymic=patronymic) & Q(self_rating=self_rating)).distinct().order_by('header'))
            elif surname and name:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                        self_rating=self_rating)).distinct().order_by('header'))
            elif course:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(tbltextgroup__group__course_number=course) & Q(
                        self_rating=self_rating)).distinct().order_by('header'))
            else:
                texts = list(
                    TblText.objects.values('header', 'language').filter(Q(error_tag_check=1) & Q(
                        self_rating=self_rating)).distinct().order_by('header'))

            if text:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text) & Q(
                        tbltextgroup__text__self_rating=self_rating)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    tbltextgroup__text__self_rating=self_rating).distinct().order_by('group_name'))
                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text__self_rating=self_rating)).distinct().order_by(
                    'course_number'))
    else:
        if text_type:
            if group:
                group_date = date[:4] + '-09-01'
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(tbltextgroup__group__group_name=group) & Q(
                        tbltextgroup__group__enrollment_date=group_date)).distinct().order_by('header'))
            elif surname and name and patronymic:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                        user__patronymic=patronymic)).distinct().order_by('header'))
            elif surname and name:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(user__last_name=surname) & Q(
                        user__name=name)).distinct().order_by('header'))
            elif course:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type) & Q(
                        tbltextgroup__group__course_number=course)).distinct().order_by('header'))
            else:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(text_type=text_type)).distinct().order_by('header'))

            if text:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text_id__header=text)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type) & Q(
                        tbltextgroup__text_id__header=text)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__text_type=text_type)).distinct().order_by('course_number'))
        else:
            if group:
                group_date = date[:4] + '-09-01'
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(tbltextgroup__group__group_name=group) & Q(
                        tbltextgroup__group__enrollment_date=group_date)).distinct().order_by('header'))
            elif surname and name and patronymic:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name) & Q(
                        user__patronymic=patronymic)).distinct().order_by('header'))
            elif surname and name:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(user__last_name=surname) & Q(user__name=name)).distinct().order_by(
                    'header'))
            elif course:
                texts = list(TblText.objects.values('header', 'language').filter(
                    Q(error_tag_check=1) & Q(tbltextgroup__group__course_number=course)).distinct().order_by(
                    'header'))
            else:
                texts = list(
                    TblText.objects.values('header', 'language').filter(error_tag_check=1).distinct().order_by(
                        'header'))

            if text:
                groups = list(TblGroup.objects.values('group_name', 'language').filter(
                    Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text)).distinct().order_by('group_name'))

                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    Q(course_number__gt=0) & Q(tbltextgroup__text_id__error_tag_check=1) & Q(
                        tbltextgroup__text_id__header=text)).distinct().order_by('course_number'))
            else:
                groups = list(TblGroup.objects.values('group_name', 'language').distinct().order_by('group_name'))
                courses = list(TblGroup.objects.values('course_number', 'language').filter(
                    course_number__gt=0).distinct().order_by('course_number'))

    return groups, courses, texts


def get_zero_count_grade_errors(data_count_errors):
    list_grades_id_in_markup = []
    for data in data_count_errors:
        list_grades_id_in_markup.append(data["grade__id_grade"])

    data_grades_not_in_errors = list(
        TblGrade.objects.annotate(grade__id_grade=F('id_grade'), grade__grade_name=F('grade_name'),
                                  grade__grade_language=F('grade_language')).values('grade__id_grade',
                                                                                    'grade__grade_name',
                                                                                    'grade__grade_language').filter(
            ~Q(id_grade__in=list_grades_id_in_markup)).annotate(count_data=Value(0, output_field=IntegerField()),
                                                                count_data_on_tokens=Value(0,
                                                                                           output_field=IntegerField())))

    data = data_count_errors + data_grades_not_in_errors

    return data


def get_tag_children(tag_parent):
    tags = list(TblTag.objects.values('id_tag', 'tag_parent').filter(markup_type=1).order_by('id_tag'))
    grouped_tags = [tag_parent]

    for tag_in_group in grouped_tags:
        for tag in tags:
            if tag['tag_parent'] == tag_in_group:
                grouped_tags.append(tag['id_tag'])

    return grouped_tags


def get_dict_children():
    tag_parents = list(TblTag.objects.values('id_tag', 'tag_language', 'tag_text', 'tag_text_russian').filter(
        Q(markup_type=1) & Q(tag_parent__isnull=True)).order_by('id_tag'))

    dict_children = {}
    for tag in tag_parents:
        grouped_tags = get_tag_children(tag['id_tag'])
        dict_children[tag['id_tag']] = grouped_tags

    return tag_parents, dict_children


def get_stat(data_relation, param_one_text, param_one_name, param_two_text, param_two_name, is_emotion):
    asses_types = TblText.TASK_RATES
    list_emotions = list(TblEmotional.objects.values())

    param_one = {}
    param_two = {}

    for data in data_relation:
        if data['language'] not in param_one.keys():
            param_one[data['language']] = []

        if data['language'] not in param_two.keys():
            param_two[data['language']] = []

    for data in data_relation:
        param_one[data['language']].append(data[param_one_text])
        param_two[data['language']].append(data[param_two_text])

    relation = {}
    data = []
    critical_stat_level = 0.05
    method = 'Pirson'
    data_fisher = []

    for language in param_one.keys():
        param_one_language = np.array(param_one[language])
        param_two_language = np.array(param_two[language])

        contingency_table = pd.crosstab(param_one_language, param_two_language, dropna=False, margins=True)

        num_rows = len(contingency_table) - 1
        num_col = len(contingency_table.columns) - 1
        N = contingency_table['All'].iloc[num_rows]

        except_values = np.zeros((num_rows, num_col))

        for row in range(num_rows):
            row_name = contingency_table.index[row]

            if is_emotion:
                emotion = ''

                for item in list_emotions:
                    if item['id_emotional'] == row_name:
                        emotion = item['emotional_name']

                for col in range(num_col):
                    count = contingency_table.iloc[row, col]
                    col_name = contingency_table.columns[col]

                    dict_item = {'language': language, param_one_text: int(row_name), param_two_text: int(col_name),
                                 param_one_name: emotion,
                                 param_two_name: asses_types[col_name - 1][1], 'count': int(count)}

                    data.append(dict_item)
                    except_values[row][col] = contingency_table.iloc[row, num_col] * contingency_table.iloc[
                        num_rows, col] / N

            else:
                for col in range(num_col):
                    count = contingency_table.iloc[row, col]
                    col_name = contingency_table.columns[col]

                    dict_item = {'language': language, param_one_text: int(row_name), param_two_text: int(col_name),
                                 param_one_name: asses_types[row_name - 1][1],
                                 param_two_name: asses_types[col_name - 1][1], 'count': int(count)}

                    data.append(dict_item)
                    except_values[row][col] = contingency_table.iloc[row, num_col] * contingency_table.iloc[
                        num_rows, col] / N

        count = 0
        for row in range(num_rows):
            for col in range(num_col):
                if except_values[row][col] < 5:
                    count += 1

        per_less = count * 100 / (num_rows * num_col)

        n = len(param_one_language)
        if n < 2:
            relation[language] = {'res': '-', 'stat': '-', 'pvalue': '-', 'N': n}
        else:
            if N <= 20 or per_less > 20:
                sum_0_0 = 0
                sum_0_1 = 0
                sum_1_0 = 0
                sum_1_1 = 0

                for row in range(num_rows):
                    row_name = contingency_table.index[row]

                    for col in range(num_col):
                        count = contingency_table.iloc[row, col]
                        col_name = contingency_table.columns[col]

                        if is_emotion:
                            if row_name in [3, 5] and col_name > 7:
                                sum_0_0 += count
                            elif row_name in [3, 5] and col_name < 8:
                                sum_0_1 += count
                            elif row_name in [1, 4, 6, 7] and col_name > 7:
                                sum_1_0 += count
                            else:
                                sum_1_1 += count
                        else:
                            if row_name > 7 and col_name > 7:
                                sum_0_0 += count
                            elif row_name > 7 and col_name < 8:
                                sum_0_1 += count
                            elif row_name < 8 and col_name > 7:
                                sum_1_0 += count
                            else:
                                sum_1_1 += count

                table = np.array([[sum_0_0, sum_0_1], [sum_1_0, sum_1_1]])
                result = scipy.stats.fisher_exact(table)
                method = 'Fisher'

                if is_emotion:
                    data_fisher.append(
                        {'language': language, 'param_one': 1, 'param_one_text': 'Положительные', 'param_two': 2,
                         'param_two_text': 'Успешно', 'count': int(table[0][0])})
                    data_fisher.append(
                        {'language': language, 'param_one': 2, 'param_one_text': 'Отрицательные', 'param_two': 2,
                         'param_two_text': 'Успешно', 'count': int(table[0][1])})
                    data_fisher.append(
                        {'language': language, 'param_one': 1, 'param_one_text': 'Положительные', 'param_two': 1,
                         'param_two_text': 'Не успешно', 'count': int(table[1][0])})
                    data_fisher.append(
                        {'language': language, 'param_one': 2, 'param_one_text': 'Отрицательные', 'param_two': 1,
                         'param_two_text': 'Не успешно', 'count': int(table[1][1])})
                else:
                    data_fisher.append(
                        {'language': language, 'param_one': 1, 'param_one_text': 'Успешно', 'param_two': 2,
                         'param_two_text': 'Успешно', 'count': int(table[0][0])})
                    data_fisher.append(
                        {'language': language, 'param_one': 2, 'param_one_text': 'Не успешно', 'param_two': 2,
                         'param_two_text': 'Успешно', 'count': int(table[0][1])})
                    data_fisher.append(
                        {'language': language, 'param_one': 1, 'param_one_text': 'Успешно', 'param_two': 1,
                         'param_two_text': 'Не успешно', 'count': int(table[1][0])})
                    data_fisher.append(
                        {'language': language, 'param_one': 2, 'param_one_text': 'Не успешно', 'param_two': 1,
                         'param_two_text': 'Не успешно', 'count': int(table[1][1])})

            else:
                result = scipy.stats.chi2_contingency(contingency_table)

            if math.isinf(result.statistic):
                stat = 'Inf'
            elif math.isnan(result.statistic):
                stat = 'Nan'
            else:
                stat = result.statistic

            if result.pvalue < critical_stat_level:
                relation[language] = {'result': 'связь между признаками есть, они не независимы', 'stat': stat,
                                      'pvalue': result.pvalue, 'N': n, 'method': method}
            else:
                relation[language] = {'result': 'связи между признаками нет, они независимы', 'stat': stat,
                                      'pvalue': result.pvalue, 'N': n, 'method': method}

    return data, relation, data_fisher
