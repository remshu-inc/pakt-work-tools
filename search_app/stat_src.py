import pandas as pd
from text_app.models import TblText, TblSentence, TblMarkup, TblMarkupType
from user_app.models import TblUser, TblStudent
from django.db.models import Q
from datetime import datetime
import numpy as np
import os
import shutil
import xlsxwriter
# def _group_stat_get_data(group_number:int, detalization:int, search_by:int):


TMP_FOLDER = 'search_app/tmp/stat_requests/{}'

def _queryset_to_list(query_set):

    results = {key:[] for key in query_set[0].keys()}
    
    for element in query_set:
        for key in element.keys():
            results[key].append(element[key])
    
    return(results)

def _fill_nonstr(list_):
    result = []
    for element in list_:
        if type(element) != str:
            result.append('')
        else:
            result.append(element)

    return(result)

def _get_errors(main_frame:pd.DataFrame, frame_name:str):
    error_frame = main_frame.groupby('tag_text').agg('count').iloc[:,[0]]
    error_frame.columns = ['Частота']

    return({frame_name:error_frame})

def _get_meta(main_frame:pd.DataFrame, frame_name:str):
    meta_dict = []
    for column in main_frame.columns[1:]:
        
        new_column = main_frame.groupby(column).count().iloc[:,[0]].reset_index()
        new_column.columns = ['Название','Частота']
        meta_dict += [{'Название':column,'Частота':''}]+new_column.to_dict('records')+[{'Название':'','Частота':''}]

    return({frame_name: pd.DataFrame(data = meta_dict)})

def _check_frames(dict_of_frames:dict):
    for key in dict_of_frames.keys():
        if type(dict_of_frames[key]) == pd.DataFrame and dict_of_frames[key].shape[0] > 0:
            return(True)
    return(False)

def built_group_stat(group_numbers:int, course_number:int,detalization:int, search_by:int,
        requester_id:int, start_date, end_date):

    #*Create query for dates
    markup_dates_limits = Q(token_id__sentence_id__text_id__create_date__gte = start_date)\
     & Q(token_id__sentence_id__text_id__create_date__lte = end_date)
    dates_limits = Q(create_date__gte = start_date) & Q(create_date__lte = end_date)

    #* Transform course number
    if course_number != -2:
        course_number = [course_number]
    else:
        course_number = [i for i in range(-1,6)]

    #* Get all users id from current group
    students_info =  _queryset_to_list(TblStudent.objects.order_by('group_number').filter(Q(group_number__in = group_numbers)).values('user_id', 'group_number').all())

    group_users = students_info['user_id']
    group_numbers = students_info['group_number']

    del students_info
    #* Get users names 
    users_info = _queryset_to_list(TblUser.objects.filter(id_user__in = group_users).values(
        'id_user',
        'name',
        'last_name',
        'patronymic',
        ).all())


    del group_users

    #* Fix names (if None and etc.)
    users_info['name'] = _fill_nonstr(users_info['name'])
    users_info['last_name'] = _fill_nonstr(users_info['last_name'])
    users_info['patronymic'] = _fill_nonstr(users_info['patronymic'])

    #* Resort users id from new query
    users_id = users_info['id_user']

    #* Concate parts of names
    users_names = [(' '.join(element)) for element in zip(
        users_info['last_name'], 
        users_info['name'], 
        users_info['patronymic'])]

    #* DataFrame for user's info
    users_frame = pd.DataFrame(data = {'user_id':users_id,'user_name':users_names, 'group': group_numbers})
    
    del users_names, users_info
    #* List for QuerySets
    queries = [None, None]

    #* Queries for errors and meta
    if search_by == 1 or search_by == 3:
        queries[0] = list(TblMarkup.objects.filter(
            Q(token_id__sentence_id__text_id__user_id__in = users_id) &
            Q(tag_id__markup_type_id__markup_type_name ='error') & 
            Q(token_id__sentence_id__text_id__creation_course__in = course_number) & markup_dates_limits
            ).values('token_id__sentence_id__text_id__user_id','tag_id__tag_text'))
    
    if search_by == 2 or search_by == 3:
        queries[1] = list(TblText.objects.filter(
            Q(user_id__in = users_id) &
            Q(creation_course__in = course_number) & dates_limits
            ).values(
                'user_id',
                'emotional__emotional_name',
                'write_tool__write_tool_name',
                'write_place__write_place_name', 
                'self_rating',
                'student_assesment',
                'assessment'))
    
    #* Disct of DataFrames for errors and meta queries result
    frames = {}
    frames_names = ['error', 'meta']

    for index, query in enumerate(queries):
        if query:

            frames[frames_names[index]] = pd.DataFrame(query)  
            #* Rename 'ugly' names of columns
            if index == 0:
                frames[frames_names[index]].columns = ['user_id', 'tag_text']

            elif index == 1:
                frames[frames_names[index]].columns = [
                    'user_id',
                    'Эмоциональное состояние',
                    'Средство написания',
                    'Место написания',
                    'Самооценка',
                    'Оценка задания студентом',
                    'Оценка работы преподавателем']

    if not _check_frames(frames):
        return({'state':False, 'folder_link':''})

    results = {'error':[], 'meta':[]}

    if detalization == 1:

        for frame_name in frames.keys():
            if frame_name == 'error':
                results[frame_name].append(_get_errors(frames[frame_name], 'Ошибки общие показатели'))

            elif frame_name == 'meta':
                results[frame_name].append(_get_meta(frames[frame_name], 'Метаданные общие показатели'))
    
    else:
        for frame_name in frames.keys():
            
            if frame_name == 'error':
                df = frames[frame_name].merge(users_frame, left_on = 'user_id', right_on = 'user_id', suffixes = ('',''))
                users = df['user_id'].unique()
                for user in users:
                    query_frame = df.query('user_id == @user')
                    user_name = query_frame['user_name'].unique()[0]
                    user_group = query_frame['group'].unique()[0]
                    results[frame_name].append(_get_errors(query_frame, f'Ошибки, гр.{user_group}, {user_name}'[:31]))
            
            elif frame_name == 'meta':
                df = frames[frame_name].merge(users_frame, left_on = 'user_id', right_on = 'user_id', suffixes = ('',''))
                users = df['user_id'].unique()
                for user in users:
                    query_frame = df.query('user_id == @user')
                    user_name = query_frame['user_name'].unique()[0]
                    user_group = query_frame['group'].unique()[0]
                    results[frame_name].append(_get_meta(query_frame, f'Метаданные, гр.{user_group}, {user_name}'[:31]))

    query_type = 'Summary_' if detalization == 1 else 'By_Students_'
    user_dir_name = query_type + str(requester_id) +'_'+ datetime.now().strftime("%m_%d_%H_%M")
    
    total_folder = TMP_FOLDER.format(user_dir_name)
    os.mkdir(total_folder)

    for key in results.keys():
        if results[key]:
            if key == 'meta':
                include_index = False
            else:
                include_index = True

            file_path = total_folder+f'/{key}.xlsx'
            writer = pd.ExcelWriter(file_path, engine = 'xlsxwriter')
            for frame_dict in results[key]:
                sheet_name = list(frame_dict.keys())[0]
                frame = frame_dict[sheet_name]

                frame.to_excel(writer, sheet_name = sheet_name, index = include_index)
            writer.save()
            writer.close()
    
    archive_link = total_folder
    shutil.make_archive(archive_link, 'zip', total_folder)
    shutil.rmtree(path = total_folder+'/')
    return({'state':True,'folder_link':archive_link+'.zip', 'file_name':user_dir_name+'.zip'})