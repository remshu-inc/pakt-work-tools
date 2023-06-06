'''
File name: pakt-to-csv.py
Author: Safonov G. R.
Description: Migration corpora data from MySQL to CSV
'''
import getpass

import sqlalchemy
import pandas as pd

SQL_QUERY_PATH = 'source/'
SAVE_PATH = '../data/'
#* Connection
login = input('User name: ')
password = getpass.getpass('Password: ')
database_name = input('Database name: ')
engine = sqlalchemy.create_engine(f"mysql+pymysql://{login}:{password}@localhost:3306/{database_name}?charset=utf8mb4", echo = False)

#*Query execute
with engine.connect() as con:
    print('Тексты...')
    #**Get info about each text
    with open(SQL_QUERY_PATH+'get_text_info.sql', 'r') as file:
        text_info_query = file.read() 

    text_info = pd.DataFrame(
        columns = ['text_id', 'header','course_number', 'asessment','raw_text'], 
        data = con.execute(sqlalchemy.text(text_info_query)))
    print('\033[F\033[K', end='')
    print('Токены...')
    #**Get info about each token
    with open(SQL_QUERY_PATH+'get_token_info.sql', 'r') as file:
        token_info_query = file.read() 

    token_info = pd.DataFrame(
        columns = ['text_id','token_id','text', 'sentence_number', 'token_number'], 
        data = con.execute(sqlalchemy.text(text_info_query)))

    print('\033[F\033[K', end='')
    print('Разметка...')
    #**Get info about each markup
    with open(SQL_QUERY_PATH+'get_markup_info.sql', 'r') as file:
        markup_info_query = file.read() 

    markup_info = pd.DataFrame(
        columns = ['markup_id', 'reason','grade','error_tag','correct','token_id'], 
        data = con.execute(sqlalchemy.text(markup_info_query))).iloc[: , :-1]
    
    print('\033[F\033[K', end='')
    print('Связи...')
    #**Get markup and token connection table
    with open(SQL_QUERY_PATH+'token_markup_connection.sql', 'r') as file:
        token_markup_con_query = file.read() 

    token_markup_con = pd.DataFrame(
        columns = ['markup_id', 'token_id'], 
        data = con.execute(sqlalchemy.text(token_markup_con_query)))

print('\033[F\033[K', end='')
print('Сохранение...')
text_info.to_csv(SAVE_PATH+'Text.csv',index=False)
token_info.to_csv(SAVE_PATH+'Token.csv',index=False)
markup_info.to_csv(SAVE_PATH+'Markup.csv',index=False)
token_markup_con.to_csv(SAVE_PATH+'Connection.csv',index=False)
    
    
