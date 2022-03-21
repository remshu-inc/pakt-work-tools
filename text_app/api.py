from turtle import update
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
import json
from .models import TblLanguage, TblTextType, TblText, TblSentence, TblMarkup, TblTag, TblTokenMarkup, TblToken
from .api_src import past_in_template
from django.db.models import F as change_value
 
#----Получение текста и аннотаций------
def get_text(query):
    if query.method == 'POST':
        text_id = json.loads(query.body.decode('utf-8'))['text_id']
    else:
        return(HttpResponseBadRequest('Query should be POST'))
    sentences = TblSentence.objects.filter(text_id=text_id).values('id_sentence', 'order_number').order_by('order_number').all()
    if not sentences.exists():
        return(JsonResponse([]))
    #* id имеющихся предложений
    sentences_id = [element['id_sentence'] for element in sentences]

    #*Получение информации о токенах
    tokens = TblToken.objects.filter(sentence_id__in = sentences_id).values('id_token', 'text', 'sentence_id', 'order_number','sentence_id__order_number').order_by('sentence_id', 'order_number').all()

    all_markups_id = [element['id_markup'] for element in TblMarkup.objects.filter(sentence_id__in = sentences_id).values('id_markup').all()]

    res_sents = [] #* Итоговые предложения
    all_token_markups_id = [] #* Id всех разметок токенов

    for sentence in sentences:
        #Сборка всех токенов
        tokens_markups = list(TblTokenMarkup.objects.filter(token_id__sentence_id = sentence['id_sentence']).values(
        'token_id',
        'markup_id',
        'id_token_markup',
        'markup_id__start_token', #id-начального токена
        'markup_id__end_token', #id - конечного токена
        'markup_id__tag_id__markup_type_id__markup_type_name', #Название типа разметки
        'markup_id__tag_id__tag_text', #Название тега на иностранном
        'markup_id__tag_id__tag_text_russian', #Название тега на русском
        'markup_id__tag_id__tag_color', #Цвет тега
        'token_id__order_number', #Номер токена в предложении,
        ).all())
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

    return(JsonResponse({'sentences':res_sents, 'token_markups_ids':all_token_markups_id}))

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