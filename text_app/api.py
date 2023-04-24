import logging
import os
import re
import subprocess
import tempfile

from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
import json

from pakt_work_tools import settings
from .models import TblGrade, TblReason, TblTextType, TblText, TblSentence, TblMarkup, TblTag, TblTokenMarkup, TblToken
from user_app.models import TblUser, TblLanguage
from .api_src import past_in_template
from datetime import datetime


def get_classification(query):
    if query.method == 'POST':
        text_id = json.loads(query.body.decode('utf-8'))['text_id']
    else:
        return (HttpResponseBadRequest('Query should be POST'))
    text_info = TblText.objects.filter(id_text=text_id).values('language_id').all()
    if not text_info.exists:
        return (JsonResponse({}))
    else:
        text_language = text_info[0]['language_id']

    tags = TblTag.objects.filter(tag_language_id=text_language).values('id_tag', 'tag_text', 'tag_text_russian',
                                                                       'tag_text_abbrev', 'tag_parent', 'tag_color',
                                                                       'markup_type_id').order_by('markup_type_id',
                                                                                                  'tag_parent').all()

    tags_info = []
    if tags.exists():
        for element in tags:
            parent_id = 0
            if element['tag_parent'] and element['tag_parent'] > 0:
                parent_id = element['tag_parent']
            spoiler = False
            for child in tags:
                if element['id_tag'] == child['tag_parent']:
                    spoiler = True
                    break
            tags_info.append({
                'isspoiler': spoiler,
                'tag_type': element['markup_type_id'],
                'tag_id': element['id_tag'],
                'tag_text': element['tag_text'],
                'tag_text_russian': element['tag_text_russian'],
                'tag_text_abbrev': element['tag_text_abbrev'],
                'parent_id': parent_id,
                'tag_color': element['tag_color']
            })
    tags_info = {'tags': tags_info}
    return (JsonResponse(tags_info))


# ----Получение текста и аннотаций------
def get_text(query):
    if query.method == 'POST':
        text_id = json.loads(query.body.decode('utf-8'))['text_id']
    else:
        return (HttpResponseBadRequest('Query should be POST'))
    sentences = TblSentence.objects.filter(text_id=text_id).values('id_sentence', 'order_number', 'text').order_by(
        'order_number').all()
    if not sentences.exists():
        return (JsonResponse({}))  # TODO Ошибку бы сюда прописать, а то вдруг, а то как
    sentences_id = [element['id_sentence'] for element in sentences]
    # * Получение инфы о маркапах
    markup_info = {
        element['id_markup']: {
            'tag_text': element['tag_id__tag_text'],
            'tag_text_russian': element['tag_id__tag_text_russian'],
            'tag_text_abbrev': element['tag_id__tag_text_abbrev'],
            'tag_id': element['tag_id'],
            'markup_type': element['tag_id__markup_type_id'],
            'tag_color': element['tag_id__tag_color'],
            'reason_id': element['reason_id'],
            'reason_text': element['reason_id__reason_name'],
            'grade_id': element['grade_id'],
            'grade_text': element['grade_id__grade_name'],
            'user_last_name': element['user_id__last_name'],
            'user_name': element['user_id__name'],
            'correct': element['correct'],
            'comment': element['comment']
        } for element in TblMarkup.objects.filter(sentence_id__in=sentences_id).values(
            'id_markup',
            'tag_id__tag_text',
            'tag_id__tag_text_russian',
            'tag_id__tag_text_abbrev',
            'tag_id',
            'tag_id__markup_type_id',
            'tag_id__tag_color',
            'reason_id',
            'reason_id__reason_name',
            'grade_id',
            'grade_id__grade_name',
            'user_id__last_name',
            'user_id__name',
            'correct',
            'comment'
        ).all()}
    # TODO Добавить обработку комментария
    # *Получение информации о токенах
    tokens = TblToken.objects.filter(sentence_id__in=sentences_id).values('id_token', 'text', 'sentence_id',
                                                                          'order_number',
                                                                          'sentence_id__order_number').order_by(
        'sentence_id', 'order_number').all()

    # all_markups_id = [element['id_markup'] for element in TblMarkup.objects.filter(sentence_id__in = sentences_id).values('id_markup').all()]

    res_sents = []  # * Итоговые предложения
    all_token_markups_id = []  # * Id всех разметок токенов

    for sentence in sentences:
        # Сборка всех токенов
        tokens_markups = list(TblTokenMarkup.objects.filter(token_id__sentence_id=sentence['id_sentence']).values(
            'token_id',
            'markup_id',
            'position',
            'id_token_markup',
            'markup_id__tag_id__markup_type_id__markup_type_name',  # Название типа разметки
            'token_id__order_number',
            'markup_id__change_date',
            'markup_id__reason_id__reason_name',
            'markup_id__grade_id__grade_name',
            'markup_id__correct',
            'markup_id__comment'
        ).order_by('markup_id__change_date').all())

        for i in range(len(tokens_markups)):
            tokens_markups[i]['last'] = TblTokenMarkup.objects.filter(
                markup_id=tokens_markups[i]['markup_id']).count() - 1

        all_token_markups_id += [element['id_token_markup'] for element in tokens_markups]
        sent_tokens = []
        for token in tokens:
            if token['sentence_id__order_number'] == sentence['order_number']:
                markups_ids = ''
                for token_markup in tokens_markups:
                    if token_markup['token_id'] == token['id_token']:
                        markups_ids += str(token_markup['markup_id']) + ' '
                token_text = token['text']
                if token_text == '-EMPTY-':
                    token_text = ''
                sent_tokens.append({
                    'token_id': token['id_token'],
                    'order_number': token['order_number'],

                    'sent_order_number': token['sentence_id__order_number'],
                    'markups_ids': markups_ids,
                    'text': token_text
                })

        ann_templates = past_in_template(tokens_markups, len(sent_tokens))
        res_sents.append(
            {
                'annotations': ann_templates,  # markup_templates,
                'tokens': sent_tokens
            }
        )

    return (
        JsonResponse({'sentences': res_sents, 'token_markups_ids': all_token_markups_id, 'markup_info': markup_info}))


def add_empty_token(query):
    if query.method == 'POST':
        data = json.loads(query.body.decode('utf-8'))
        token_id = int(data['parent_token'])
        if data['append_position'] == 'left':
            append_position = 0
        else:
            append_position = 1
        token_info = TblToken.objects.filter(id_token=token_id).values('sentence_id', 'order_number').all()
        if not token_info.exists():
            return (HttpResponseBadRequest('parent token not found'))
        else:
            token_info = token_info[0]
        order_number = token_info['order_number'] + append_position
        sentence_id = token_info['sentence_id']

        update_tokens = TblToken.objects.filter(sentence_id=sentence_id,
                                                order_number__gte=order_number)  # .update(border_number = change_value('order_number'))
        for element in update_tokens:
            if element.order_number >= order_number:
                element.order_number += 1
            element.save()
        new_row = TblToken(sentence_id=sentence_id, text="-EMPTY-", order_number=order_number)
        new_row.save()
    return (HttpResponse('successfully'))


def annotation_edit(query):
    if query.method == 'POST':
        data = json.loads(query.body.decode('utf-8'))
        time = datetime.now()
        if data['query_type'] == '1':
            if data['tokens'][0] == '[' and data['tokens'][-1] == ']':
                tokens = json.loads(data['tokens'])
                if len(tokens) == 0:
                    return (JsonResponse({'status': 'false',
                                          'message': "Критическая ошибка создания аннотации #1, обратитесь к администратору"},
                                         status=500))  # Если возникнет - проблема на фронте

                # Получение доп. информации о токенах, по совместительству проверка на корректность входа
                tokens_info = TblToken.objects.filter(id_token__in=tokens).values('id_token', 'sentence_id',
                                                                                  'sentence_id__order_number',
                                                                                  'order_number').order_by(
                    'sentence_id__order_number', 'order_number')

                if not tokens_info.exists() or len(tokens_info) != len(tokens):
                    return (JsonResponse({'status': 'false',
                                          'message': "Критическая ошибка создания аннотации #2, обратитесь к администратору"},
                                         status=500))  # Не правильно определены id-токенов

                # Информация о позиции
                start_token = TblToken.objects.get(id_token=tokens_info[0]['id_token'])
                # end_token = TblToken.objects.get(id_token = tokens_info[len(tokens_info)-1]['id_token'])
                sentence = TblSentence.objects.get(id_sentence=tokens_info[0]['sentence_id'])
                if not data['classification_tag'].isdigit():
                    return (JsonResponse({'status': 'false', 'message': "Не указан тег разметки"}, status=500))
                # Информация о теге
                try:
                    tag = TblTag.objects.get(id_tag=int(data['classification_tag']))
                except:
                    return (JsonResponse({'status': 'false', 'message': "Не корректное значение тега разметки"},
                                         status=500))
                # Информация о пользователе
                try:
                    user = TblUser.objects.get(id_user=int(data['user_id']))
                except:
                    return (JsonResponse({'status': 'false', 'message': "Не корректное значение id пользователя"},
                                         status=500))
                # Получаем информацию о степени и критичности
                if data['reason'] != '0' and data['reason'].isdigit():
                    reason = TblReason.objects.get(id_reason=int(data['reason']))
                else:
                    reason = None

                if data['grade'] != '0' and data['grade'].isdigit():
                    grade = TblGrade.objects.get(id_grade=int(data['grade']))
                else:
                    grade = None
                new_row = TblMarkup(
                    token=start_token,
                    tag=tag,
                    sentence=sentence,
                    user=user,
                    # start_token = start_token,
                    # end_token = end_token,
                    comment=data['comment'],
                    correct=data['correct'],
                    change_date=time,
                    grade=grade,
                    reason=reason
                )
                new_row.save()
                for index, token in enumerate(tokens_info):
                    new_token_markup = TblTokenMarkup(
                        position=index,
                        token=TblToken.objects.get(id_token=token['id_token']),
                        markup=new_row
                    )
                    new_token_markup.save()
        elif data['query_type'] == '2':
            if data['markup_id'].isdigit():
                try:
                    update_row = TblMarkup.objects.get(id_markup=int(data['markup_id']))
                except:
                    return (JsonResponse({'status': 'false',
                                          'message': "Критическая ошибка обновления аннотации #1, обратитесь к администратору"}))

                try:
                    tag = TblTag.objects.get(id_tag=int(data['classification_tag']))
                except:
                    return (JsonResponse({'status': 'false', 'message': "Не корректное значение тега разметки"},
                                         status=500))

                if data['reason'] != '0' and data['reason'].isdigit():
                    reason = TblReason.objects.get(id_reason=int(data['reason']))
                else:
                    reason = None
                try:
                    user = TblUser.objects.get(id_user=int(data['user_id']))
                except:
                    return (JsonResponse({'status': 'false', 'message': "Не корректное значение id пользователя"},
                                         status=500))
                if data['grade'] != '0' and data['grade'].isdigit():
                    grade = TblGrade.objects.get(id_grade=int(data['grade']))
                else:
                    grade = None

                update_row.reason = reason
                update_row.grade = grade
                update_row.tag = tag
                update_row.correct = data['correct']
                update_row.comment = data['comment']
                update_row.user = user
                update_row.change_date = time

                update_row.save()
        elif data['query_type'] == '3':
            if data['markup_id'].isdigit():
                TblMarkup.objects.filter(id_markup=int(data['markup_id'])).delete()

    return HttpResponse()


def _convert_tags(rftagger_map):
    """
    Преобразование частей речи RF Tagger в части речи Tree Tagger (STTS)
    """
    result = []

    for item in rftagger_map:
        if item[1].startswith("ADJA"):
            result.append((item[0], "ADJA"))
        elif item[1].startswith("ADJD"):
            result.append((item[0], "ADJD"))
        elif item[1].startswith("ADV"):
            result.append((item[0], "ADV"))
        elif item[1].startswith("APPR"):
            result.append((item[0], "APPR"))
        elif item[1].startswith("APPRART"):
            result.append((item[0], "APPRART"))
        elif item[1].startswith("APPO"):
            result.append((item[0], "APPO"))
        elif item[1].startswith("APZR"):
            result.append((item[0], "APZR"))
        elif item[1].startswith("ART"):
            result.append((item[0], "ART"))
        elif item[1].startswith("CARD"):
            result.append((item[0], "CARD"))
        elif item[1].startswith("FM"):
            result.append((item[0], "FM"))
        elif item[1].startswith("ITJ"):
            result.append((item[0], "ITJ"))
        elif item[1].startswith("CONJ.Coord"):
            result.append((item[0], "KON"))
        elif item[1].startswith("CONJ.Comp"):
            result.append((item[0], "KOKOM"))
        elif item[1].startswith("CONJ.SubInf"):
            result.append((item[0], "KOUI"))
        elif item[1].startswith("CONJ.SubFin"):
            result.append((item[0], "KOUS"))
        elif item[1].startswith("N.Reg"):
            result.append((item[0], "NN"))
        elif item[1].startswith("N.Name"):
            result.append((item[0], "NE"))
        elif item[1].startswith("PRO.Dem.Attr"):
            result.append((item[0], "PDAT"))
        elif item[1].startswith("PRO.Dem.Subst"):
            result.append((item[0], "PDS"))
        elif item[1].startswith("PRO.Indef.Attr"):
            result.append((item[0], "PIAT"))
        elif item[1].startswith("PRO.Indef.Subst"):
            result.append((item[0], "PIS"))
        elif item[1].startswith("PRO.Pers"):
            result.append((item[0], "PPER"))
        elif item[1].startswith("PRO.Inter.Subst"):
            result.append((item[0], "PWS"))
        elif item[1].startswith("PRO.Inter.Attr"):
            result.append((item[0], "PWAT"))
        elif item[1].startswith("PRO.Poss.Subst"):
            result.append((item[0], "PPOSS"))
        elif item[1].startswith("PRO.Poss.Attr"):
            result.append((item[0], "PPOSAT"))
        elif item[1].startswith("PRO.Rel.Subst"):
            result.append((item[0], "PRELS"))
        elif item[1].startswith("PRO.Rel.Attr"):
            result.append((item[0], "PRELAT"))
        elif item[1].startswith("PRO.Refl"):
            result.append((item[0], "PRF"))
        elif item[1].startswith("PROADV"):
            result.append((item[0], "PROAV"))
        elif item[1].startswith("PART.Zu"):
            result.append((item[0], "PTKZU"))
        elif item[1].startswith("PART.Neg"):
            result.append((item[0], "PTKNEG"))
        elif item[1].startswith("PART.Verb"):
            result.append((item[0], "PTKVZ"))
        elif item[1].startswith("PART.Ans"):
            result.append((item[0], "PTKANT"))
        elif item[1].startswith("PART.Deg"):
            result.append((item[0], "PTKA"))
        elif item[1].startswith("TRUNC"):
            result.append((item[0], "TRUNC"))
        elif item[1].startswith("VFIN.Aux"):
            result.append((item[0], "VAFIN"))
        elif item[1].startswith("VFIN.Mod"):
            result.append((item[0], "VMFIN"))
        elif item[1].startswith("VFIN.Sein") or item[1].startswith("VFIN.Haben") or item[1].startswith(
                "VFIN.Full"):  # Other: VFIN.Sein.1.Sg.Past.Ind
            result.append((item[0], "VVFIN"))
        elif item[1].startswith("VINF.Aux"):
            result.append((item[0], "VAINF"))
        elif item[1].startswith("VINF.Mod"):
            result.append((item[0], "VMINF"))
        elif item[1].startswith("VINF.Full.zu") or item[1].startswith("VINF.Sein.zu") or item[1].startswith("VINF.Haben.zu"):
            result.append((item[0], "VVIZU"))
        elif item[1].startswith("VINF.Full") or item[1].startswith("VINF.Sein") or item[1].startswith("VINF.Haben"):
            result.append((item[0], "VVINF"))
        elif item[1].startswith("VIMP.Full"):
            result.append((item[0], "VVIMP"))
        elif item[1].startswith("VPP.Full"):
            result.append((item[0], "VVPP"))
        elif item[1].startswith("VPP.Aux"):
            result.append((item[0], "VAPP"))
        elif item[1].startswith("VPP.Mod"):
            result.append((item[0], "VMPP"))
        elif item[1].startswith("SYM.Pun.Comma"):
            result.append((item[0], "$,"))
        elif item[1].startswith("SYM.Other.XY"):
            result.append((item[0], "XY"))
        elif item[1].startswith("SYM.Pun.Sent"):
            result.append((item[0], "$."))
        elif item[1].startswith("SYM.Paren") or item[1].startswith("SYM.Pun.Hyph") or item[1].startswith("SYM.Pun.Colon"):
            result.append((item[0], "$("))
        else:
            print(f"ERROR!!!: Unknown tag {item[1]}")
            result.append(item)

    return result


def process_part_of_speech(query):
    """
    Функция обработки запроса на обновление частей речи.
    """
    if query.method == 'POST':

        data = json.loads(query.body.decode('utf-8'))
        language = data.get("language")
        text_type = data.get("text_type")
        text_id = data.get("text_id")

        # Информация о пользователе
        if query.user is not None:
            user = query.user

        if language is None or text_type is None or text_id is None:
            return JsonResponse({'status': 'false',
                                 'message': "Ошибка разбора параметров"},
                                status=400)

        if language != 'Deutsche':
            return JsonResponse({
                'status': 'false',
                'message': 'Неподдерживаемый язык разметки'
            }, status=400)

        data_dir = tempfile.mkdtemp(prefix="pact_" + text_id + "_")

        # Вытаскиваем предложения из БД
        sentences = TblSentence.objects \
            .filter(text_id=text_id) \
            .order_by('order_number') \
            .values('id_sentence', 'text').all()
        if not sentences.exists():
            os.removedirs(data_dir)
            return JsonResponse({
                'status': 'false',
                'message': 'Текст не найден'
            }, status=404)

        # TODO: вставить привязку к таблицам типов тегов и языка
        part_of_speeches_data = TblTag.objects.filter(markup_type_id=2, tag_language_id=1).all()
        part_of_speeches = {}
        for item in part_of_speeches_data:
            tag_name = item.tag_text_abbrev if item.tag_text_abbrev else item.tag_text
            part_of_speeches[str(tag_name)] = item
        # print(part_of_speeches.keys())

        # бежим по предложениям: для каждого предложения делаем тегирование, мапим с токенами и записываем теги
        time = datetime.now()
        for sentence in sentences:
            with open(data_dir + "/input.txt", "w", encoding="UTF-8") as input_file:
                input_file.write(sentence['text'].replace('-EMPTY-', '') + "\n")

            # Запускаем обработку таггером.
            # 1. Токенизация
            ret_code = subprocess.run(["perl", settings.RFTAGGER_PATH + "/cmd/tokenize.perl", "-a "
                                       + settings.RFTAGGER_PATH + "/lib/german-abbreviations", data_dir + "/input.txt"],
                                      check=True, cwd=settings.RFTAGGER_PATH, capture_output=True, text=True, errors='backslashreplace')
            if ret_code.returncode != 0:
                return JsonResponse({'status': 'false',
                                     'message': "Ошибка запуска таггера: " + ret_code.stderr},
                                    status=400)

            # 2. Удаляем строки из точек и запятых
            tags = re.sub("\n[.]?\n", "\n", ret_code.stdout)

            with open(data_dir + "/tags.txt", "w", encoding="UTF-8") as input_file:
                input_file.write(tags)

            # 3. Аннотирование текста
            ret_code = subprocess.run(
                [settings.RFTAGGER_PATH + "/bin/rft-annotate", settings.RFTAGGER_PATH + "/lib/german.par",
                 data_dir + "/tags.txt"],
                check=True, cwd=settings.RFTAGGER_PATH, capture_output=True, text=True)

            tagger_tokens = []
            for tagger_token in ret_code.stdout.split("\n"):
                if tagger_token == "":
                    continue
                items = tagger_token.split("\t")
                if len(items) != 2:
                    print("ERROR!!!: " + tagger_token)
                else:
                    tagger_tokens.append((items[0], items[1]))
            # print(tagger_tokens)
            # 4. читаем токены и начинаем маппить
            sentence_tokens = list(TblToken.objects.filter(sentence_id=sentence['id_sentence']).values(
                'id_token',
                'text',
            ).order_by('order_number').all())
            map_result, error_score = _map_lists(tagger_tokens, sentence_tokens, 0, 0)
            # print(map_result)
            if error_score > 0:
                print(f"Ошибка разбора предложения {sentence['id_sentence']} RUTagger: {error_score}")
            # if error_score > 0:
            #     print(ret_code.stdout)
            #     print("=================")
            #     print(sentence['text'].replace('-EMPTY-', ''))
            #     print(sentence_tokens)
            # 5. Удаляем все токены частеречной разметки этого предложения
            deleted_count = TblMarkup.objects.filter(sentence_id=sentence['id_sentence'],
                                                     tag_id__markup_type_id=2).delete()
            # print("Deleted " + str(deleted_count))
            # 6. Добавляем новые токены частеречной разметки
            map_result = _convert_tags(map_result)

            text_sentence = TblSentence.objects.get(id_sentence=sentence['id_sentence'])
            for item in map_result:
                # print(f"token_id={item[0]}, tag_id={item[1]}")
                text_token = TblToken.objects.get(id_token=item[0])
                markup = TblMarkup(
                    token= text_token,
                    tag=part_of_speeches[item[1]],
                    sentence=text_sentence,
                    user=user,
                    change_date = time,
                    comment="авторазметка RFTagger"
                )
                markup.save()
                token_markup = TblTokenMarkup(
                    position=0,
                    token=text_token,
                    markup=markup
                )
                token_markup.save()
        return HttpResponse()

    # TODO: сделать отображение таблицы частей речи для GET запроса
    logging.debug("NOT IMPLEMENTED!")
    return HttpResponse()


def _map_lists(tagger_tokens, sentence_tokens, tagger_index, sentence_index, error_score=0):
    ret = []
    error_count = 0

    if sentence_index >= len(sentence_tokens):
        return ret, error_count + len(tagger_tokens) - tagger_index

    while tagger_index < len(tagger_tokens):
        # убираем пустые токены
        while True:
            if sentence_tokens[sentence_index]["text"] != "-EMPTY-":
                break
            sentence_index += 1
            if sentence_index >= len(sentence_tokens):
                return ret, error_count + len(tagger_tokens) - tagger_index

        # если токены совпадают, то все ок
        if sentence_tokens[sentence_index]["text"] == tagger_tokens[tagger_index][0]:
            part = tagger_tokens[tagger_index][1]
            ret.append((sentence_tokens[sentence_index]["id_token"], part))
            tagger_index += 1
            sentence_index += 1
        elif sentence_index + 1 < len(sentence_tokens) and sentence_tokens[sentence_index + 1]["text"] == "." and \
                sentence_tokens[sentence_index]["text"] + "." == tagger_tokens[tagger_index][0]:
            # если токен с точкой, а в тексте он без точки, то тоже все ок
            part = tagger_tokens[tagger_index][1]
            ret.append((sentence_tokens[sentence_index]["id_token"], part))
            # TODO: вставить часть речи точки
            tagger_index += 1
            sentence_index += 2
        else:
            # если слишком много ошибок маппинга, то не глядим дальше
            if error_count + error_score > 5:
                return ret, error_count
            # print(f"Process {tagger_index} in {len(tagger_tokens)}")
            # print(tagger_tokens)
            # print(sentence_tokens)
            # print(f"Test with tagger={tagger_index} and sentence={sentence_index}")
            ret1, err1 = _map_lists(tagger_tokens, sentence_tokens, tagger_index + 1, sentence_index, error_score + 1)
            ret2, err2 = _map_lists(tagger_tokens, sentence_tokens, tagger_index, sentence_index + 1, error_score + 1)
            if err1 > err2:
                # print("NOT FOUND: " + sentence_tokens[sentence_index]["text"] + " in sentence tokens")
                error_count += err2 + 1
                ret.extend(ret2)
            else:
                # print("NOT FOUND: " + tagger_tokens[tagger_index][0] + " in tagger tokens")
                error_count += err1 + 1
                ret.extend(ret1)
            # print(f"Return {ret}, {error_count}")
            return ret, error_count
    return ret, error_count
