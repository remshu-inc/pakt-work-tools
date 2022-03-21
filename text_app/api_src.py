def past_in_template(markups, sent_length:int):
    templates = [] 
    count_list = [0 for i in range(sent_length)]
    for markup in markups:
        count_list[markup['token_id__order_number']] += 1
    lines_num = max(count_list)
    del count_list
    used_markups = []
    for line in range(lines_num):
        template = [{'isann':False} for i in range(sent_length)]
        blocked_position = []
        for markup in markups:
            if markup['token_id__order_number'] not in blocked_position and markup['id_token_markup'] not in used_markups:
                blocked_position.append(markup['token_id__order_number'])
                used_markups.append(markup['id_token_markup'])

                if markup['token_id'] == markup['markup_id__start_token'] == markup['markup_id__end_token']:
                    display = True
                    position = 'single'
                elif markup['token_id'] == markup['markup_id__start_token']:
                    display = True
                    position = 'start'
                elif markup['token_id'] == markup['markup_id__end_token']:
                    display = False
                    position = 'end'
                else:
                    display = False
                    position = 'middle'

                #Добавление записи в шаблон
                template[markup['token_id__order_number']] = {
                        'isann': True,
                        'display':display, # отвечает за отображения текста
                        'ann_position': position,# отвечает за тип позиции
                        'token_id': markup['token_id'],
                        'ann_id': markup['markup_id'],
                        'ann_color': markup['markup_id__tag_id__tag_color'],
                        'tag_text': markup['markup_id__tag_id__tag_text'],
                        'tag_text_rus': markup['markup_id__tag_id__tag_text_russian'],
                        'tag_type': markup['markup_id__tag_id__markup_type_id__markup_type_name'],
                        'token_markup_id': markup['id_token_markup']
                    }

        templates.append(template)
    
    return(templates)