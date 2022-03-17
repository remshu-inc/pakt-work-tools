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


def show_text(request, text_id = 1):
    
    # TODO: дописать получение определенных сталбцов
    sentences = TblSentence.objects.filter(text_id=text_id).all()
    # sentences = session.query(TblSentence.id_sentence, TblSentence.order_number).filter(TblSentence.text_id == text_id)
    
    # TODO: переписать проверку
    # if sentences.count()>0:
    #     sentences = sentences.all()
    # else:
    #     return(render(request, "corpus.html", context = {'text_html':'Text is not Found', 'found':False}))
    
    res_sents = []
    all_markups_id = []
    for sent_index, sent in enumerate(sentences):

        tokens = TblToken.objects.filter(sentence_id = sent.id_sentence).values('order_number', 'text', 'id_token')
        # tokens = [element._asdict() for element in session.query(TblToken.order_number, TblToken.text, TblToken.id_token).filter(TblToken.sentence_id == sent[0])]
        
        #Поиск аннотаций
        
        # markups = [] 
        # appuser__group_id=group_id
        
        markups = TblMarkup.objects.filter(sentence_id = sent.id_sentence).values(
            'start_token_id__order_number', 'start_token', 'end_token', 'id_markup', 'tag_id__markup_type_id__markup_type_name', 'tag_id__tag_text', 'tag_id__tag_text_russian'
        )
        
        # markups = [element._asdict() for element in 
        #         session.query(
        #             TblToken.order_number,
        #             TblMarkup.start_token,
        #             TblMarkup.end_token,
        #             TblMarkup.id_markup,
        #             TblMarkupType.markup_type_name,
        #             TblTag.tag_text,
        #             TblTag.tag_text_russian).filter(
        #                 and_(
        #                     TblMarkup.sentence_id == sent[0],
        #                     TblTag.id_tag == TblMarkup.tag_id,
        #                     TblTag.markup_type_id == TblMarkupType.id_markup_type,
        #                     TblToken.id_token == TblMarkup.start_token
        #                 )
        #             )
        # ]
        all_markups_id += [element['id_markup'] for element in markups]

        templates = []
        blocked_markup = [] 
        
        for index, markup in enumerate(markups):
            if index not in blocked_markup:
                start = markup['order_number']
                end = start + markup['end_token'] - markup['start_token']

                blocked_intervals = [[start,end]]
                blocked_markup.append(index)
                ann_template = [{'isann':False} for i in range(len(tokens))]
                ann_template = past_in_template(markup, start,end, ann_template)
                
                for sub_index, sub_markup in enumerate(markups):
                    if sub_index not in blocked_markup:
                        start = sub_markup['order_number']  
                        end = start + sub_markup['end_token'] - sub_markup['start_token']
                        
                        flag = True
                        for interval in blocked_intervals:
                            if not(start > interval[1] or end < interval[0]):
                                flag = False
                                break
                        
                        if flag:
                            blocked_intervals.append([start,end])
                            blocked_markup.append(sub_index)
                            ann_template = past_in_template(sub_markup, start,end, ann_template)
                
                templates.append(ann_template)

        for token_index in range(len(tokens)):
            tokens[token_index]['markups_ids'] = ""
            for template in templates:
                if template[token_index]['isann']:
                    tokens[token_index]['markups_ids'] += str(template[token_index]['ann_id'])+' '
                    


# annotation_template[markup['order_number']] = {
#     'isann': True,
#     'display':True,
#     'ann_position': start_position,
#     'ann_id': markup['id_markup'],
#     'tag_text': markup['tag_text'],
#     'tag_text_rus': markup['tag_text_russian'],
#     'tag_type': markup['markup_type_name']
# }



        #Формирования списка предложений
        res_sents.append(
            {
            'number': sent_index,
            'annotations':templates,
            'tokens': tokens
            }
        )

    return render(request, "index1.html", context= {'sentences': res_sents, 'markups_ids': all_markups_id, 'found':True})