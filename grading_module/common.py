# -*- coding: utf-8 -*-

import re
import mysql.connector
import pandas as pd

from grading_module.gross_model import GrossModel


# функция формирования на основе базы данных корпуса массива исходных данных для обучения искусственной нейронной сети для определения грубости ошибки
def GetDataForGrossModel(user, password, host, database):

    def pars_str(s):
        # Обработка строки - удаление лишних пробелов и невидимых символов
        s1 = s.strip()
        s1 = s1.replace(' ,', ',').replace(' .', '.').replace(' :', ':').replace(' )', ')')
        s1 = s1.replace('( ', '(').replace(' ”', '”').replace(' ?', '?').replace('  ', ' ')
        s1 = s1.replace(' ,', ',').replace(' .', '.').replace(' :', ':').replace(' )', ')')
        s1 = s1.replace('( ', '(').replace(' ”', '”').replace(' ?', '?').replace('  ', ' ')
        return s1

    # Запрос к базе данных корпуса
    con = mysql.connector.connect(user=user, password=password, host=host, database=database)
    with con:
        cur = con.cursor()
        cur.execute('''SELECT TblSentence.id_sentence, TblSentence.text, 
                TblToken.text, TblToken.order_number, TblMarkup.id_markup, 
                TblMarkup.correct, TblMarkup.grade_id 
                FROM TblSentence, TblText, TblMarkup, TblToken, TblTokenMarkup 
                where (TblSentence.text_id = TblText.id_text) 
                and (TblSentence.id_sentence = TblMarkup.sentence_id)
                and (TblMarkup.id_markup = TblTokenMarkup.markup_id)
                and (TblToken.id_token = TblTokenMarkup.token_id)
                and (TblText.language_id = 1)
                and (TblMarkup.grade_id in (1,2,3))''')
        rows = cur.fetchall()
        cur.close()
    df = pd.DataFrame(rows, columns=['id_sentence', 'text', 'tbltoken.text', 'order_number', 'id_markup', 'correct',
                                     'grade_id'])
    df.sort_values(['id_sentence', 'id_markup', 'order_number'], inplace=True)
    con.close()

    M = []  # Список предложений для обучения с указанием уровня грубости

    # Список номеров предложений с количеством ошибок в нем
    sent_ids = pd.DataFrame(
        list(df[['id_sentence', 'id_markup']].groupby(['id_sentence', 'id_markup']).count().index)).groupby(0).count()

    n_sent = 0  # обработано предложений

    # Для каждого предложения
    for index, row in sent_ids.iterrows():
        # Список номеров ошибок
        A = list(set(df[df['id_sentence'] == index]['id_markup'].values.tolist()))
        # Список списков номеров токенов для ошибок
        MarkUps = []
        for k in range(len(A)):
            MarkUps.append(df[df['id_markup'] == A[k]]['order_number'].values.tolist())
        # список для подмножеств
        subsets = []
        for k in range(len(MarkUps)):
            for k2 in range(len(MarkUps)):
                if k != k2:
                    if set(MarkUps[k]).issubset(MarkUps[k2]):
                        subsets.append((A[k], MarkUps[k]))
        # удаление подмножеств
        for k in subsets:
            try:
                A.remove(k[0])
                MarkUps.remove(k[1])
            except:
                pass

        flagNotIntercept = True
        for k in range(len(MarkUps) - 1):
            for k2 in range((k + 1), len(MarkUps)):
                if not set(MarkUps[k]).isdisjoint(MarkUps[k2]):
                    flagNotIntercept = False

        if flagNotIntercept:
            flagNotGaps = True
            for k in range(len(MarkUps)):
                A_min = min(MarkUps[k])
                A_max = max(MarkUps[k])
                if A_max - A_min + 1 != len(MarkUps[k]):
                    flagNotGaps = False
            if flagNotGaps:
                # Ошибки включают только последовательные токены
                n_sent += 1
                # Список замен
                Pairs = []
                B = df[df['id_sentence'] == index]['text']
                sentCorrect = B.iloc[0]
                sentCorrect = pars_str(sentCorrect)

                TupleA = []
                for k in range(len(A)):
                    nu = min(df[df['id_markup'] == A[k]]['order_number'])
                    TupleA.append((A[k], nu))
                sorted_tuples = sorted(TupleA, key=lambda item: item[1])
                A = [k for k, v in sorted_tuples]

                for k in range(len(A)):
                    nn = 0
                    AMarkUp = df[df['id_markup'] == A[k]]['tbltoken.text']
                    strold = ''
                    for t in AMarkUp:
                        if not pd.isna(t):
                            strold = strold + t + ' '
                    strold = pars_str(strold)
                    B = df[df['id_markup'] == A[k]][['text', 'correct', 'grade_id']]
                    strnew = B.iloc[0]['correct']
                    if (strnew is None) or (type(strnew) == float):
                        continue
                    if strnew.strip() == '-':
                        strnew = ' '
                    nn = sentCorrect.find(strold)
                    sentCorrect = sentCorrect.replace(strold, strnew, 1)
                    Pairs.append((strold, strnew, B.iloc[0]['grade_id'], nn))

                NotM = []
                for k in range(len(Pairs)):
                    sentCorrect = sentCorrect.replace('\n', ' ')
                    if Pairs[k][1] == ' ':
                        sentError = sentCorrect[:Pairs[k][3]] + ' ' + Pairs[k][0] + sentCorrect[Pairs[k][3]:]
                    else:
                        if str(Pairs[k][0]).strip() == '-EMPTY-':
                            sentError = sentCorrect.replace(Pairs[k][1], ' ', 1)
                        else:
                            if Pairs[k][3] > 1:
                                sentError = sentCorrect[:Pairs[k][3] - 2] + sentCorrect[Pairs[k][3] - 2:].replace(
                                    Pairs[k][1], Pairs[k][0], 1)
                            else:
                                sentError = sentCorrect.replace(Pairs[k][1], Pairs[k][0], 1)

                    sentError = re.sub(r'^\d{1,2}\.|^\d{1,2}\)', '', sentError)
                    sentCorrect = re.sub(r'^\d{1,2}\.|^\d{1,2}\)', '', sentCorrect)
                    sentError = sentError.replace('-EMPTY-', '')
                    sentError = pars_str(sentError)
                    sentCorrect = sentCorrect.replace('-EMPTY-', '')
                    sentCorrect = pars_str(sentCorrect)

                    # Проверка на пунктуацию
                    if (Pairs[k][1].strip() == '') and ((Pairs[k][0].strip() == '.') or (Pairs[k][0].strip() == ',')):
                        NotM.append('Пунктуация: ' + sentError + ' | ' + sentCorrect + ' | ' + str(Pairs[k][2]))
                        continue
                    # Проверка на одинаковость предложений в том числе без учета регистра
                    if (sentError.strip() == sentCorrect.strip()) or (
                            sentError.strip().lower() == sentCorrect.strip().lower()):
                        NotM.append('Одинаковые: ' + sentError + ' | ' + sentCorrect + ' | ' + str(Pairs[k][2]))
                        continue
                    # Проверка на пустое предложение
                    if len(sentError.strip()) == 0 or len(sentCorrect.strip()) == 0:
                        NotM.append('Пустое: ' + sentError + ' | ' + sentCorrect + ' | ' + str(Pairs[k][2]))
                        continue
                    # Проверка на предложение с токеном ???
                    if sentError.strip() == '???' or sentCorrect.strip() == '???':
                        NotM.append('???: ' + sentError + ' | ' + sentCorrect + ' | ' + str(Pairs[k][2]))
                        continue
                    if Pairs[k][1].strip() == '???':
                        NotM.append('????: ' + sentError + ' | ' + sentCorrect + ' | ' + str(Pairs[k][2]))
                        continue
                    if Pairs[k][1].strip()[:9] == 'скопирова':
                        NotM.append('Плагиат: ' + sentError + ' | ' + sentCorrect + ' | ' + str(Pairs[k][2]))
                        continue

                    M.append((sentError, sentCorrect, str(Pairs[k][2])))
            else:
                # Токены в ошибках идут с разрывом
                pass
        else:
            # Есть сложные пересечения ошибок
            pass

    return M


# функция формирования на основе базы данных корпуса массива исходных данных для обучения искусственной нейронной сети для определения грубости ошибки
def GrossModelDataTo_scv(file, user, password, host, database):
    M = GetDataForGrossModel(user, password, host, database)
    pd.DataFrame(M, columns=['sent', 'sentcorrect', 'level']).to_csv(file, sep=';')


# функция формирования на основе базы данных корпуса массива исходных данных для обучения искусственной нейронной сети для формирования оценки текста
def GetDataForMarkModel(user, password, host, database):
    con = mysql.connector.connect(user=user, password=password, host=host, database=database)
    with con:
        cur = con.cursor()
        cur.callproc('make_dataset', [])
        for result in cur.stored_results():
            rows = result.fetchall()
        cur.close()
    con.close()

    df = pd.DataFrame(rows, columns=['idT', 'text_mark', 'gram', 'leks', 'punkt', 'orpho', 'diskurs', 'skips', 'extra',
                                     'gram1', 'gram2', 'gram3', 'gram4', 'gram5', 'gram6', 'gram7', 'gram8', 'gram9',
                                     'gram10', 'gram11',
                                     'gram12', 'gram13', 'gram14', 'leks15', 'leks16', 'leks17', 'leks18', 'diskurs19',
                                     'diskurs20',
                                     'diskurs21', 'diskurs22', 'g1', 'g2', 'g3', 'numsent', 'numtoken', 'numchar'])
    return df


# функция формирования массива исходных данных на основе базы данных корпуса для обучения искусственной нейронной сети для формирования оценки текста
def MarkModelDataTo_scv(file, user, password, host, database):
    df = GetDataForMarkModel(user, password, host, database)
    df.to_csv(file, index=False)


# функция для определения грубости ошибки
def GetGrossError(textError, textCorrect):
    # Входные данные - два предложения
    model = GrossModel(modeltype='CrossEncoder', score=[0.98, 0.93, 0.87])
    model.load_model(pathname='model_gross')
    res = model.predict([[textError], [textCorrect]])
    del model
    return res[0][2:]


# функция для формирования оценки текста
###@tf.function
def GetTextMark(Val, model=None):
    # Val - список списков
    from grading_module.mark_model import MarkModel
    model = MarkModel(modelpath = 'model_mark')
    res = model.predict(Val)
    del model
    return res
