# from django.views import generic
# from .models import TblText

from .models import TblLanguage, TblReason, TblGrade, TblTextType, TblText, TblSentence, TblMarkup, TblTag, TblTokenMarkup, TblToken
from .forms import TextCreationForm, get_annotation_form
from django.shortcuts import render
from django.http import HttpResponse
from copy import deepcopy
from django.db.models import F
from right_app.views import check_permissions_work_with_annotations, check_permissions_show_text
from user_app.models import TblTeacher, TblUser

# Test

# class TextList(generic.ListView):
#     queryset = TblText.objects
#     template_name = 'corpus.html'

def show_files(request, language = None, text_type = None):
    # Для выбора языка
    if language == None:
        try:
            list_language = TblLanguage.objects.all()
            return render(request, "corpus.html", context= {'list_language': list_language})
            
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
            return(render(request, "corpus.html", context= {'list_text_type': list_text_type}))
        
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
            
        return(render(request, "corpus.html", context= {'work_with_file': True, 'list_text_and_user': list_text_and_user, 'language_selected': language}))
    
    return(render(request, "corpus.html", context = {'text_html':'<div id = "Text_found_err">404 Not Found<\div>'}))

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
  
def show_text(request, text_id = 1, language = None, text_type = None):
    text_info  = TblText.objects.filter(id_text = text_id).values('header','language_id', 'language_id__language_name').all()
    if text_info.exists() and check_permissions_show_text(request.user.id_user, text_id):
        header = text_info[0]['header']
        text_language_name = text_info[0]['language_id__language_name']
        text_language = text_info[0]['language_id']
        tags = TblTag.objects.filter(tag_language_id = text_language).values('id_tag','tag_text','tag_text_russian', 'tag_parent','tag_color').all()
        tags_info = []
        if tags.exists():
            for element in tags:
                parent_id = 0
                if element['tag_parent']>0:
                    parent_id = element['tag_parent']
                spoiler = False
                for child in tags:
                    if element['id_tag'] == child['tag_parent']:
                        spoiler = True
                        break
                tags_info.append({
                    'isspoiler':spoiler,
                    'tag_id':element['id_tag'],
                    'tag_text':element['tag_text'],
                    'tag_text_russian':element['tag_text_russian'],
                    'parent_id':parent_id,
                    'tag_color':element['tag_color']
                })
        reasons = TblReason.objects.filter(reason_language_id = text_language).values('id_reason','reason_name')
        grades = TblGrade.objects.filter(grade_language_id = text_language).values('id_grade','grade_name')
        annotation_form = get_annotation_form(grades,reasons)

        ann_right = check_permissions_work_with_annotations(request.user.id_user, text_id)

        return render(request, "work_area.html", context= {'founded':True,'ann_right':ann_right,'user_id':request.user.id_user, 'tags_info':tags_info, 'annotation_form':annotation_form, 'text_id':text_id,'lang_name':text_language_name})
    else:
        return render(request, 'work_area.html', context={'founded':False})
