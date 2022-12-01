import pandas as pd
from text_app.models import TblText, TblSentence, TblMarkup, TblMarkupType
from user_app.models import TblUser, TblStudent, TblGroup, TblStudentGroup
from text_app.models import TblTextGroup
from django.db.models import Q
from datetime import datetime
import numpy as np
import os
import shutil
import xlsxwriter

from pakt_work_tools.settings import SEARCH_TMP_FOLDER
# def _group_stat_get_data(group_number:int, detalization:int, search_by:int):


TMP_FOLDER = SEARCH_TMP_FOLDER+'stat_requests/{}'

def _queryset_to_list(query_set):
    if query_set.exists():
        query_set = query_set.all()
        results = {key:[] for key in query_set[0].keys()}
        
        for element in query_set:
            for key in element.keys():
                results[key].append(element[key])
    
        return(results)
    else:
        return({})

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
    error_frame['Тег Ошибки'] = error_frame.index
    error_frame = error_frame.reset_index(drop=True)
    error_frame.columns = ['Частота','Тег Ошибки']
    
    error_frame = error_frame.loc[:,['Тег Ошибки','Частота']]

    return({frame_name:error_frame})

def _get_meta(main_frame:pd.DataFrame, frame_name:str):
    meta_dict = []
    for column in main_frame.columns[1:]:
        
        new_column = main_frame.groupby(column).count().iloc[:,[0]].reset_index(drop=True)
        new_column.columns = ['Название','Частота']
        meta_dict += [{'Название':column,'Частота':''}]+new_column.to_dict('records')+[{'Название':'','Частота':''}]

    return({frame_name: pd.DataFrame(data = meta_dict)})

def _check_frames(dict_of_frames:dict):
    for key in dict_of_frames.keys():
        if type(dict_of_frames[key]) == pd.DataFrame and dict_of_frames[key].shape[0] > 0:
            return(True)
    return(False)

def built_group_stat(group_id:int,requester_id:int):

    #* Get all users id from current group
    students_info =  _queryset_to_list(TblStudentGroup.objects.order_by('group_id')\
        .filter(Q(group_id = group_id)).values(
            'group_id',
            'student_id__user_id',
            'group_id__group_name',
            'group_id__enrollement_date'))
    if not students_info:
        return({'state':False,'folder_link':''})
        # TblStudent.objects.order_by('group_number').filter(Q(group_number__in = group_numbers)).values('user_id', 'group_number').all())

    group_users = students_info['student_id__user_id']
    
    group_name =\
        students_info['group_id__group_name'][0]+' ('\
        +str(students_info['group_id__enrollement_date'][0].year)+') '

    group_id = students_info['group_id'][0]
    works = TblTextGroup.objects.filter(group_id = group_id).values('text_id')

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
    users_frame = pd.DataFrame(data = {'user_id':users_id,'user_name':users_names, 'group': group_name})
    
    del users_names, users_info
    #* List for QuerySets
    queries = [None]

    #* Queries for errors and meta
    queries[0] = list(TblMarkup.objects.filter(
            Q(token_id__sentence_id__text_id__user_id__in = users_id) &
            Q(tag_id__markup_type_id__markup_type_name ='error') & 
            Q(token_id__sentence_id__text_id__in = works)
            ).values('token_id__sentence_id__text_id__user_id','tag_id__tag_text'))
    
    #* Disct of DataFrames for errors and meta queries result
    frames = {}
    frames_names = ['error', 'meta']

    for index, query in enumerate(queries):
        if query:
            frames[frames_names[index]] = pd.DataFrame(query)  
            #* Rename 'ugly' names of columns
            frames[frames_names[index]].columns = ['user_id', 'tag_text']

    if not _check_frames(frames):
        return({'state':False, 'folder_link':''})

    results = {'error':[]}
    
    for frame_name in frames.keys():
        
        if frame_name == 'error':
            df = frames[frame_name].merge(users_frame, left_on = 'user_id', right_on = 'user_id', suffixes = ('',''))
            users = df['user_id'].unique()
            for user in users:
                query_frame = df.query('user_id == @user')
                user_name = query_frame['user_name'].unique()[0]
                user_group = query_frame['group'].unique()[0]
                results[frame_name].append(_get_errors(query_frame, f'{user_name}'[:31]))
        

    query_type =  'By_Students_'
    user_dir_name = query_type + str(requester_id) +'_'+ datetime.now().strftime("%m_%d_%H_%M")
    
    total_folder = TMP_FOLDER.format(user_dir_name)
    os.mkdir(total_folder)

    for key in results.keys():
        if results[key]:
            file_path = total_folder+f'/{group_name+key}.xlsx'
            writer = pd.ExcelWriter(file_path, engine = 'xlsxwriter')
            for frame_dict in results[key]:
                sheet_name = list(frame_dict.keys())[0]
                frame = frame_dict[sheet_name]

                frame.to_excel(writer, sheet_name = sheet_name, index=False)
                for column in frame:
                    column_width = max(frame[column].astype(str).map(len).max(), len(column))
                    col_idx = frame.columns.get_loc(column)
                    writer.sheets[sheet_name].set_column(col_idx, col_idx, column_width)

            writer.save()
            writer.close()
    
    archive_link = total_folder
    shutil.make_archive(archive_link, 'zip', total_folder)
    shutil.rmtree(path = total_folder+'/')
    return({'state':True,'folder_link':archive_link+'.zip', 'file_name':user_dir_name+'.zip'})