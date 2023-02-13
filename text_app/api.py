from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
import json

from .models import TblGrade, TblReason, TblTextType, TblText, TblSentence, TblMarkup, TblTag, TblTokenMarkup, TblToken
from user_app.models import TblUser, TblLanguage
from .api_src import past_in_template
from datetime import datetime


def get_classification(query):
    if query.method == 'POST':
        text_id = json.loads(query.body.decode('utf-8'))['text_id']
    else:
        return(HttpResponseBadRequest('Query should be POST'))
    text_info = TblText.objects.filter(id_text = text_id).values('language_id').all()
    if not text_info.exists:
        return(JsonResponse({}))
    else:
        text_language = text_info[0]['language_id']

    tags = TblTag.objects.filter(tag_language_id = text_language).values('id_tag','tag_text','tag_text_russian','tag_text_abbrev', 'tag_parent','tag_color','markup_type_id').order_by('markup_type_id','tag_parent').all()

    tags_info = []
    if tags.exists():
        for element in tags:
            parent_id = 0
            if element['tag_parent'] and element['tag_parent']>0:
                parent_id = element['tag_parent']
            spoiler = False
            for child in tags:
                if element['id_tag'] == child['tag_parent']:
                    spoiler = True
                    break
            tags_info.append({
                'isspoiler':spoiler,
                'tag_type':element['markup_type_id'],
                'tag_id':element['id_tag'],
                'tag_text':element['tag_text'],
                'tag_text_russian':element['tag_text_russian'],
                'tag_text_abbrev':element['tag_text_abbrev'],
                'parent_id':parent_id,
                'tag_color':element['tag_color']
            })
    tags_info = {'tags':tags_info}
    return(JsonResponse(tags_info))



#----Получение текста и аннотаций------
def get_text(query):
    if query.method == 'POST':
        text_id = json.loads(query.body.decode('utf-8'))['text_id']
    else:
        return(HttpResponseBadRequest('Query should be POST'))
    sentences = TblSentence.objects.filter(text_id=text_id).values('id_sentence', 'order_number','text').order_by('order_number').all()
    if not sentences.exists():
        return(JsonResponse({}))#TODO Ошибку бы сюда прописать, а то вдруг, а то как
    sentences_id = [element['id_sentence'] for element in sentences]
    #* Получение инфы о маркапах
    markup_info = {
        element['id_markup']:{
        'tag_text':element['tag_id__tag_text'],
        'tag_text_russian':element['tag_id__tag_text_russian'],
        'tag_text_abbrev':element['tag_id__tag_text_abbrev'],
        'tag_id':element['tag_id'],
        'markup_type':element['tag_id__markup_type_id'],
        'tag_color':element['tag_id__tag_color'],
        'reason_id':element['reason_id'],
        'reason_text':element['reason_id__reason_name'],
        'grade_id':element['grade_id'],
        'grade_text':element['grade_id__grade_name'],
        'user_last_name':element['user_id__last_name'],
        'user_name':element['user_id__name'],
        'correct':element['correct'],
        'comment':element['comment']
        } for element in TblMarkup.objects.filter(sentence_id__in = sentences_id).values(
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
            #TODO Добавить обработку комментария
    #*Получение информации о токенах
    tokens = TblToken.objects.filter(sentence_id__in = sentences_id).values('id_token', 'text', 'sentence_id', 'order_number','sentence_id__order_number').order_by('sentence_id', 'order_number').all()

    # all_markups_id = [element['id_markup'] for element in TblMarkup.objects.filter(sentence_id__in = sentences_id).values('id_markup').all()]


    res_sents = [] #* Итоговые предложения
    all_token_markups_id = [] #* Id всех разметок токенов

    for sentence in sentences:
        #Сборка всех токенов
        tokens_markups = list(TblTokenMarkup.objects.filter(token_id__sentence_id = sentence['id_sentence']).values(
        'token_id',
        'markup_id',
        'position',
        'id_token_markup',
        'markup_id__tag_id__markup_type_id__markup_type_name', #Название типа разметки
        'token_id__order_number',
        'markup_id__change_date',
        'markup_id__reason_id__reason_name',
        'markup_id__grade_id__grade_name',
        'markup_id__correct',
        'markup_id__comment'
        ).order_by('markup_id__change_date').all())

        for i in range(len(tokens_markups)):
            tokens_markups[i]['last'] = TblTokenMarkup.objects.filter(markup_id = tokens_markups[i]['markup_id']).count()-1

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
                    'token_id':token['id_token'],
                    'order_number':token['order_number'],

                    'sent_order_number':token['sentence_id__order_number'],
                    'markups_ids': markups_ids,
                    'text': token_text
                })

        ann_templates = past_in_template(tokens_markups, len(sent_tokens))
        res_sents.append(
            {
            'annotations':ann_templates,#markup_templates,
            'tokens': sent_tokens
            }
        )


    return(JsonResponse({'sentences':res_sents, 'token_markups_ids':all_token_markups_id, 'markup_info':markup_info}))


def add_empty_token(query):
    if query.method == 'POST':
        data = json.loads(query.body.decode('utf-8'))
        token_id = int(data['parent_token'])
        if data['append_position'] == 'left':
            append_position = 0
        else:
            append_position = 1
        token_info = TblToken.objects.filter(id_token = token_id).values('sentence_id', 'order_number').all()
        if not token_info.exists():
            return(HttpResponseBadRequest('parent token not found'))
        else:
            token_info = token_info[0]
        order_number = token_info['order_number'] + append_position
        sentence_id = token_info['sentence_id']

        update_tokens = TblToken.objects.filter(sentence_id = sentence_id, order_number__gte = order_number)#.update(border_number = change_value('order_number'))
        for element in update_tokens:
            if element.order_number >= order_number:
                element.order_number+=1
            element.save()
        new_row = TblToken(sentence_id = sentence_id, text = "-EMPTY-", order_number = order_number)
        new_row.save()
    return(HttpResponse('successfully'))

def annotation_edit(query):
    if query.method == 'POST':
        data = json.loads(query.body.decode('utf-8'))
        time = datetime.now()
        if data['query_type'] == '1':
            if data['tokens'][0] == '[' and data['tokens'][-1] ==']':
                tokens = json.loads(data['tokens'])
                if len(tokens) ==0:
                    return(JsonResponse({'status':'false','message':"Критическая ошибка создания аннотации #1, обратитесь к администратору"}, status=500)) # Если возникнет - проблема на фронте

                #Получение доп. информации о токенах, по совместительству проверка на корректность входа
                tokens_info = TblToken.objects.filter(id_token__in=tokens).values('id_token','sentence_id','sentence_id__order_number','order_number').order_by('sentence_id__order_number','order_number')

                if not tokens_info.exists() or len(tokens_info) != len(tokens):
                    return(JsonResponse({'status':'false','message':"Критическая ошибка создания аннотации #2, обратитесь к администратору"}, status=500))# Не правильно определены id-токенов
                
                #Информация о позиции
                start_token = TblToken.objects.get(id_token = tokens_info[0]['id_token'])
                # end_token = TblToken.objects.get(id_token = tokens_info[len(tokens_info)-1]['id_token'])
                sentence = TblSentence.objects.get(id_sentence = tokens_info[0]['sentence_id'])
                if not data['classification_tag'].isdigit():
                    return(JsonResponse({'status':'false','message':"Не указан тег разметки"}, status=500))
                #Информация о теге
                try:
                    tag = TblTag.objects.get(id_tag = int(data['classification_tag']))
                except:
                    return(JsonResponse({'status':'false','message':"Не корректное значение тега разметки"}, status=500))
                #Информация о пользователе
                try:
                    user = TblUser.objects.get(id_user = int(data['user_id']))
                except:
                    return(JsonResponse({'status':'false','message':"Не корректное значение id пользователя"}, status=500))
                #Получаем информацию о степени и критичности
                if data['reason'] != '0' and data['reason'].isdigit():
                    reason = TblReason.objects.get(id_reason = int(data['reason']))
                else:
                    reason = None
                
                if data['grade'] != '0' and data['grade'].isdigit():
                    grade = TblGrade.objects.get(id_grade = int(data['grade']))
                else:
                    grade = None
                new_row = TblMarkup(
                token = start_token,
                tag = tag,
                sentence = sentence,
                user = user,
                # start_token = start_token,
                # end_token = end_token,
                comment = data['comment'],
                correct = data['correct'],
                change_date = time,
                grade = grade,
                reason = reason
                 )
                new_row.save()
                for index, token in enumerate(tokens_info):
                    new_token_markup = TblTokenMarkup(
                        position = index,
                        token = TblToken.objects.get(id_token = token['id_token']),
                        markup = new_row
                    )   
                    new_token_markup.save()
        elif data['query_type'] == '2':
            if data['markup_id'].isdigit():
                try:
                    update_row = TblMarkup.objects.get(id_markup = int(data['markup_id']))
                except:
                    return(JsonResponse({'status':'false','message':"Критическая ошибка обновления аннотации #1, обратитесь к администратору"}))

                try:
                    tag = TblTag.objects.get(id_tag = int(data['classification_tag']))
                except:
                    return(JsonResponse({'status':'false','message':"Не корректное значение тега разметки"}, status=500))
                
                if data['reason'] != '0' and data['reason'].isdigit():
                    reason = TblReason.objects.get(id_reason = int(data['reason']))
                else:
                    reason = None
                try:
                    user = TblUser.objects.get(id_user = int(data['user_id']))
                except:
                    return(JsonResponse({'status':'false','message':"Не корректное значение id пользователя"}, status=500))
                if data['grade'] != '0' and data['grade'].isdigit():
                    grade = TblGrade.objects.get(id_grade = int(data['grade']))
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
                TblMarkup.objects.filter(id_markup = int(data['markup_id'])).delete()
            
            
    return(HttpResponse())

