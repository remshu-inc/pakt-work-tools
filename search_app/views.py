from django.shortcuts import redirect, render
from text_app.models import TblTag, TblMarkup, TblToken, TblSentence
from django.db.models import Q
import re

def index(request):
    
    return render(request, "index.html")

def search(request):
    if request.POST:
        corpus_search = request.POST['corpus_search']
        corpus_search = re.findall(r'\[[^\[\]]+\]', corpus_search)
        
        # Для неточного поиска
        # MyClass.objects.filter(name__iexact=my_parameter)
        
        # TODO: написать фор для обработки всех запросов
        # Поиск только по первому запросу
        if 'word=' in corpus_search[0] or 'word =' in corpus_search[0]:
            word = re.search(r'[\'\"].*[\'\"]', corpus_search[0]).group(0)[1:-1]
            
            sentence_objects = TblToken.objects.filter(
                text__iexact = word
            ).values(
                'id_token', 'sentence_id', 'sentence_id__text_id__header', 'sentence_id__text_id__create_date'
            )

            # TODO: пропписать исключение
            if len(sentence_objects) == 0:
                pass
            
            list_search = []
            for sentence in sentence_objects:
                tokens = TblToken.objects.filter(
                    sentence_id = sentence['sentence_id']
                ).order_by('order_number')
                
                list_token = []
                for token in tokens:
                    if token.text == '-EMPTY-':
                        continue
                    if token.id_token == sentence['id_token']:
                        list_token.append({'text': token.text, 'primary': True})
                    else:
                        list_token.append({'text': token.text})
                
                list_search.append({
                    'header': sentence['sentence_id__text_id__header'],
                    'tokens': list_token,
                    'create_date': sentence['sentence_id__text_id__create_date']
                })
        
        elif 'pos=' in corpus_search[0] or 'pos =' in corpus_search[0]:
            pass
        
        elif 'error=' in corpus_search[0] or 'error =' in corpus_search[0]:
            error = re.search(r'[\'\"].*[\'\"]', corpus_search[0]).group(0)[1:-1]
            
            sentence_objects = TblMarkup.objects.filter(
                Q(tag_id__tag_text = error) | Q(tag_id__tag_text_russian = error)
            ).values(
                'token_id', 'token_id__sentence_id', 'token_id__sentence_id__text_id__header', 'token_id__sentence_id__text_id__create_date'
            )
            
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
                    if token.id_token == sentence['token_id']:
                        list_token.append({'text': token.text, 'primary': True})
                    else:
                        list_token.append({'text': token.text})
                
                list_search.append({
                    'header': sentence['token_id__sentence_id__text_id__header'],
                    'tokens': list_token,
                    'create_date': sentence['token_id__sentence_id__text_id__create_date']
                })

        return render(request, "search.html", context={'search_value': request.POST['corpus_search'],'list_search': list_search})

    else:
        return redirect(request, 'home')