import re

from text_app.models import TblText, TblSentence, TblToken, TblMarkup, TblTokenMarkup
from user_app.models import TblUser
from .task_controller import get_text_before_and_after
import spacy
from german_nouns.lookup import Nouns
import json
from django.forms.models import model_to_dict
from random import shuffle

# python -m spacy download fr_core_news_sm
# python -m spacy download de_core_news_sm

german_nlp = spacy.load("de_core_news_sm")
# french_nlp = spacy.load("fr_core_news_sm")
german_nouns = Nouns()

conv_german_pos = {
    "NOUN": "N",
    "VERB": "V",
    "ADJ": "ADJ",
    "ADV": "ADV"
}

# skull emoji
orthographical_mistakes_ids = [
    7, 8, 9, 10, 11, 12, 25, 27, 28, 29,
    30, 32, 33, 34, 35, 36, 38, 39, 40, 41,
    42, 43, 44, 46, 47, 49, 50, 51, 54,
    55, 56, 66, 67, 70, 71, 72, 73, 74, 75,
    84, 85, 86, 86, 88, 89, 90, 91, 92
]


# Генерирует упражнения по заданным параметрам. Возвращает список сгенерированных упражнений.
def generate_tasks(parametres):

    sentence_count = parametres["sentence_count"]
    if sentence_count is None:
        sentence_count = 1

    tasks = []

    for text_id in parametres["text_ids"]:
        tasks.extend(prepare_text(get_text(text_id), parametres))

    shuffle(tasks)
    return tasks[:sentence_count]



# Вспомогательная функция, запрашивает из БД тексты пользователя с токенами и разметкой и возвращает их.
def get_user_texts(user_id):
    texts = [
        dict(text, sentences=[])
        for text in TblText.objects.filter(user_id=user_id).all().values()
    ]
    texts_ids = []
    for text in texts:
        texts_ids.append(text["id_text"])

    sentences = [
        dict(sent, tokens=[])
        for sent in TblSentence.objects.filter(text_id__in=texts_ids).all().values()
    ]
    sentences_ids = []
    for sent in sentences:
        sentences_ids.append(sent["id_sentence"])

    markups = (TblMarkup.objects.filter(correct__isnull=False) & TblMarkup.objects.filter(
        sentence_id__in=sentences_ids)).all().values()

    markups_keys_to_inds = dict()
    markup_ids = []

    for ind, markup in enumerate(markups):
        markups_keys_to_inds[markup["id_markup"]] = ind
        markup_ids.append(markup["id_markup"])

    markupstokens = list(TblTokenMarkup.objects.filter(markup_id__in=markup_ids).all().values())

    for mt in markupstokens:
        if markups_keys_to_inds.get(mt["markup_id"]) is not None:
            if markups[markups_keys_to_inds[mt["markup_id"]]].get("mt") is not None:
                markups_keys_to_inds.pop(mt["markup_id"])
            else:
                markups[markups_keys_to_inds[mt["markup_id"]]]["mt"] = True

    markups = [
        markup
        for markup in markups if markups_keys_to_inds.get(markup["id_markup"]) is not None
    ]

    sentences_ids = set()
    for markup in markups:
        sentences_ids.add(markup["sentence_id"])

    tokens = [
        dict(token, markups=[])
        for token in TblToken.objects.filter(sentence_id__in=sentences_ids).all().values()
    ]

    sentences = list(filter(lambda s: s["id_sentence"] in sentences_ids, sentences))

    texts_ids = set()
    for sent in sentences:
        texts_ids.add(sent["text_id_id"])
    texts = list(filter(lambda s: s["id_text"] in texts_ids, texts))

    text_keys_to_inds = dict()
    sent_keys_to_inds = dict()
    token_keys_to_inds = dict()

    for ind, text in enumerate(texts):
        text_keys_to_inds[text["id_text"]] = ind

    for ind, sent in enumerate(sentences):
        sent_keys_to_inds[sent["id_sentence"]] = ind

    for ind, token in enumerate(tokens):
        token_keys_to_inds[token["id_token"]] = ind

    for markup in markups:
        tokens[token_keys_to_inds[markup["token_id"]]]["markups"].append(markup)

    for token in tokens:
        sentences[sent_keys_to_inds[token["sentence_id"]]]["tokens"].append(token)

    for sent in sentences:
        texts[text_keys_to_inds[sent["text_id_id"]]]["sentences"].append(sent)

    texts = list(filter(lambda s: s["language_id"] == 1, texts))

    return texts


# Вспомогательная функция, запрашивает из БД все тексты с токенами и разметкой и возвращает их.
def get_all_texts(size=200, offset=0):
    # markups = list(TblMarkup.objects.filter(correct__isnull=False).all().values())
    markups = list(TblMarkup.objects.filter(correct__isnull=False)[offset:offset + size].all().values())
    sentences = set()
    tokens = set()
    texts = set()

    markup_ids = [
        markup["id_markup"]
        for markup in markups
    ]

    markups_keys_to_inds = dict()

    for ind, markup in enumerate(markups):
        markups_keys_to_inds[markup["id_markup"]] = ind

    markupstokens = list(TblTokenMarkup.objects.filter(markup_id__in=markup_ids).all().values())

    for mt in markupstokens:
        if markups_keys_to_inds.get(mt["markup_id"]) is not None:
            if markups[markups_keys_to_inds[mt["markup_id"]]].get("mt") is not None:
                markups_keys_to_inds.pop(mt["markup_id"])
            else:
                markups[markups_keys_to_inds[mt["markup_id"]]]["mt"] = True

    # print("Всего разметок: " + str(len(markups)))
    markups = [
        markup
        for markup in markups if markups_keys_to_inds.get(markup["id_markup"]) is not None
    ]
    # print("Однотокенных разметок: " + str(len(markups)))

    for markup in markups:
        sentences.add(markup["sentence_id"])

    tokens = [
        dict(token, markups=[])
        for token in TblToken.objects.filter(sentence_id__in=sentences).all().values()
    ]
    sentences = [
        dict(sentence, tokens=[])
        for sentence in TblSentence.objects.filter(id_sentence__in=sentences).all().values()
    ]

    for sentence in sentences:
        texts.add(sentence["text_id_id"])

    texts = [
        dict(text, sentences=[])
        for text in TblText.objects.filter(id_text__in=texts).all().values()
    ]

    text_keys_to_inds = dict()
    sent_keys_to_inds = dict()
    token_keys_to_inds = dict()

    for ind, text in enumerate(texts):
        text_keys_to_inds[text["id_text"]] = ind

    for ind, sent in enumerate(sentences):
        sent_keys_to_inds[sent["id_sentence"]] = ind

    for ind, token in enumerate(tokens):
        token_keys_to_inds[token["id_token"]] = ind

    for markup in markups:
        tokens[token_keys_to_inds[markup["token_id"]]]["markups"].append(markup)

    for token in tokens:
        sentences[sent_keys_to_inds[token["sentence_id"]]]["tokens"].append(token)

    for sent in sentences:
        texts[text_keys_to_inds[sent["text_id_id"]]]["sentences"].append(sent)

    return texts


# Вспомогательная функция, запрашивает из БД текст по id.
def get_text(text_id):
    text = model_to_dict(TblText.objects.get(id_text=text_id))
    sentences = [
        dict(sent)
        for sent in TblSentence.objects.filter(text_id=text_id).all().values()
    ]

    sentences_ids = []
    for sent in sentences:
        sentences_ids.append(sent["id_sentence"])

    markups = (TblMarkup.objects.filter(correct__isnull=False) & TblMarkup.objects.filter(
        sentence_id__in=sentences_ids)).all().values()

    markup_ids = [
        markup["id_markup"]
        for markup in markups
    ]

    markups_keys_to_inds = dict()

    for ind, markup in enumerate(markups):
        markups_keys_to_inds[markup["id_markup"]] = ind

    markupstokens = list(TblTokenMarkup.objects.filter(markup_id__in=markup_ids).all().values())

    for mt in markupstokens:
        if markups_keys_to_inds.get(mt["markup_id"]) is not None:
            if markups[markups_keys_to_inds[mt["markup_id"]]].get("mt") is not None:
                markups_keys_to_inds.pop(mt["markup_id"])
            else:
                markups[markups_keys_to_inds[mt["markup_id"]]]["mt"] = True

    # print("Всего разметок: " + str(len(markups)))
    markups = [
        markup
        for markup in markups if markups_keys_to_inds.get(markup["id_markup"]) is not None
    ]
    # print("Однотокенных разметок: " + str(len(markups)))

    sentences = set()
    for markup in markups:
        sentences.add(markup["sentence_id"])

    tokens = [
        dict(token, markups=[])
        for token in TblToken.objects.filter(sentence_id__in=sentences).all().values()
    ]
    sentences = [
        dict(sentence, tokens=[])
        for sentence in TblSentence.objects.filter(id_sentence__in=sentences).all().values()
    ]

    sent_keys_to_inds = dict()
    token_keys_to_inds = dict()

    for ind, sent in enumerate(sentences):
        sent_keys_to_inds[sent["id_sentence"]] = ind

    for ind, token in enumerate(tokens):
        token_keys_to_inds[token["id_token"]] = ind

    for markup in markups:
        tokens[token_keys_to_inds[markup["token_id"]]]["markups"].append(markup)

    for token in tokens:
        sentences[sent_keys_to_inds[token["sentence_id"]]]["tokens"].append(token)

    text["sentences"] = sentences

    return text


# (
#         markup_id   = TblMarkup.objects.get(id_markup=data["markup_id"]),
#         inf         = data["inf"],
#         input_type  = data["input_type"],
#         test_id     = data["test_id"],
#     )

BestimmterArtikel = [
    "der",
    "des",
    "dem",
    "den",
    "die",
    "das"
]

unbestimmterArtikel = [
    "ein",
    "eines",
    "einem",
    "einen",
    "eine",
    "einer"
]
Negationsartikel = [
    "kein",
    "keine",
    "keinen",
    "keinem",
    "keines",
    "keiner"
]


def execute_order_43(artikel):
    if artikel in ['ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr',
                   'Sie', 'sie', 'mich', 'dich', 'ihn', 'uns',
                   'euch', 'mir', 'dir', 'ihm', 'Ihnen', 'ihnen']:
        return "Впишите личное местоимение в правильной форме"
    elif artikel in ['mein', 'meine', 'meines', 'meiner', 'meinem',
                     'meinen', 'dein', 'deine', 'deines', 'deiner',
                     'deinem', 'deinen', 'sein', 'seine', 'seines',
                     'seiner', 'seinem', 'seinen', 'ihr', 'ihre', 'ihres',
                     'ihrer', 'ihrem', 'ihren', 'unser', 'unsere', 'unseres',
                     'unserer', 'unserem', 'unseren', 'euer', 'eure', 'eures',
                     'eurer', 'eurem', 'euren', 'Ihr', 'Ihre', 'Ihres',
                     'Ihrer', 'Ihrem', 'Ihren']:
        return "Впишите притяжательное местоимение в правильной форме"
    elif artikel in ['der', 'die', 'das', 'dessen', 'deren', 'derer',
                     'dem', 'denen', 'den', 'derjenige', 'dasjenige',
                     'diejenige', 'diejenigen', 'desjenigen', 'derjenigen',
                     'demjenigen', 'denjenigen', 'derselbe', 'dasselbe', 'dieselbe',
                     'dieselben', 'desselben', 'derselben', 'denselben', 'dieser',
                     'dieses', 'diese', 'diesem', 'diesen', 'ein solcher', 'ein solches',
                     'eine solche', 'solche', 'eines solchen', 'einer solchen',
                     'solcher', 'einem solchen', 'solchen', 'einen solchen',
                     'selbst', 'selber']:
        return "Впишите указательное местоимение в правильной форме"
    elif artikel in ['wer', 'was', 'wessen', 'wem', 'wen', 'was für eine',
                     'was für welche', 'was für eines', 'was für einer',
                     'was für welcher', 'was für einem', 'was für einer',
                     'was für welchen', 'was für einen', 'was für eines',
                     'was für eins', 'was für eine', 'was für welche',
                     'welchem', 'welcher', 'welchen', 'welches', 'welche']:
        return "Впишите вопросительное местоимение в правильной форме"
    elif artikel in ['mich', 'dich', 'sich', 'uns', 'euch']:
        return "Впишите возвратное местоимение в правильной форме"
    else:
        return "Вставьте неопределенное местоимение в нужной форме"


# Вспомогательная функция, преобразует текст в набор пре-упражнений и отфильтровывает согласно параметрам.
def prepare_text(text, parametres="", lang_german=True):
    """Возвращает такую штуку:
            "text_before" - текст до ошибки
            "text_after" - текст после ошибки
            "input_type" - 0 = Dropdown, 1 = Text
            "inf" - подсказка, должна быть написано в конце упражнения (только для input_type=1!!!)
            "variants" - варианты ответа (только для input_type=0!!!)
        parametres и lang_german пока не используются - все равно все упражнения на орфографию и для немецкого
    """
    tasks = []
    # Цикл по каждому предложению в тексте
    for sentence in text["sentences"]:
        current_text = sentence["text"]
        # Цикл по каждому токену в предложении
        flag_one_task = True
        for i in range(0, len(sentence["tokens"])):
            token = sentence["tokens"][i]
            # Получение размеки токена, и если она не пустая(len!=1), то токен содержит ошибку,
            # если len > 1 - более одной ошибки на токен
            markups = token["markups"]
            if len(markups) == 1 and flag_one_task:
                flag_one_task = False
                # Структура new_pretask соответствует записи бд tblTask
                new_pretask = dict()

                markup = markups[0]
                new_pretask["text_before"], new_pretask["text_after"] = get_text_before_and_after(markup["id_markup"])
                if markup["correct"] == "":
                    continue

                if markup["correct"] == "-EMPTY-":
                    correct = "-"
                else:
                    correct = markup["correct"]

                if token["text"] == "-EMPTY-":
                    was = "-"
                else:
                    was = token["text"]
                bad = [35, 36, 57, 27]
                # 27 - ошибка на несколько токенов
                # 36 - правильно: 4. , 21. - что такое?
                # 57 - не соответствует описанию алгоритма

                if markup["tag_id"] == 28:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Поставьте существительное ({get_word_form(correct, True)}) в нужную форму"

                elif markup["tag_id"] == 29:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Впишите правильную форму слова ({get_word_form(correct, True)})"

                elif markup["tag_id"] == 30:
                    new_pretask["input_type"] = 0
                    new_pretask[
                        "inf"] = f"Вспомните управление существительного и впишите правильный ответ ({get_word_form(correct, True)})"

                elif markup["tag_id"] == 31:
                    variants = set(BestimmterArtikel)
                    variants.add(correct)
                    d = list()
                    for var in list(variants):
                        d.append({"variant_text": var})
                    new_pretask["variants"] = d
                    new_pretask["input_type"] = 1

                elif markup["tag_id"] == 32:
                    variants = set(unbestimmterArtikel)
                    variants.add(correct)
                    d = list()
                    for var in variants:
                        d.append({"variant_text": var})
                    new_pretask["variants"] = d
                    new_pretask["input_type"] = 1

                elif markup["tag_id"] == 33:
                    variants = set(Negationsartikel)
                    variants.add(correct)
                    d = list()
                    for var in variants:
                        d.append({"variant_text": var})

                    new_pretask["variants"] = d
                    new_pretask["input_type"] = 1

                elif markup["tag_id"] == 34:
                    new_pretask["input_type"] = 0
                    new_pretask[
                        "inf"] = "Впишите артикль, если это необходимо; впишите предлог, если это необходимо."

                elif markup["tag_id"] == 37:
                    new_pretask["input_type"] = 1
                    new_pretask["variants"] = list({get_word_form(correct, True), correct, was})

                elif markup["tag_id"] == 38:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = "Впишите личное местоимение"

                elif markup["tag_id"] == 39:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = "Впишите притяжательное местоимение"

                elif markup["tag_id"] == 40:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = "Впишите указательное местоимение"

                elif markup["tag_id"] == 41:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = "Впишите вопросительное местоимение"

                elif markup["tag_id"] == 42:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = "Впишите возвратное местоимение"

                elif markup["tag_id"] == 43:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = execute_order_43(correct)

                elif markup["tag_id"] == 44:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Поставьте глагол ({get_word_form(correct, True)}) в нужную форму"

                elif markup["tag_id"] == 66:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Поставьте модальный глагол ({get_word_form(correct, True)}) в нужную форму"

                elif markup["tag_id"] == 67:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Поставьте сильный глагол ({get_word_form(correct, True)}) в нужную форму"

                elif markup["tag_id"] in [68, 69]:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Поставьте глагол ({get_word_form(correct, True)}) в правильной форме. "


                elif markup["tag_id"] in [83, 88]:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Präsens"

                elif markup["tag_id"] in [84, 89]:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Präteritum"

                elif markup["tag_id"] in [85, 90]:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Perfekt"

                elif markup["tag_id"] in [86, 91]:
                    new_pretask["input_type"] = 0
                    new_pretask[
                        "inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Plusquamperfekt"

                elif markup["tag_id"] in [87, 92]:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Futurum I"

                elif markup["tag_id"] == 72:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Imperativ"

                elif markup["tag_id"] == 73:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Konjunktiv"

                elif markup["tag_id"] == 74:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Aktiv"

                elif markup["tag_id"] == 75:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Passiv"

                elif markup["tag_id"] == 76:
                    new_pretask["input_type"] = 0
                    new_pretask[
                        "inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Zustandspassiv"
                # ??
                elif markup["tag_id"] == 48:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Вспомните управление глагола и впишите правильный ответ"

                elif markup["tag_id"] == 49:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Partizip I"

                elif markup["tag_id"] == 50:

                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Измените форму глагола ({get_word_form(correct, True)}) на форму Partizip II"

                elif markup["tag_id"] in [51, 52, 53]:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Впишите нужный предлог"

                elif markup["tag_id"] == 9:

                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Впишите нужный союз"

                elif markup["tag_id"] == 54:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Поставьте прилагательное ({get_word_form(correct, True)}) в правильную форму"

                elif markup["tag_id"] == 55:
                    if correct == "weniger":
                        a = "wenig"
                    elif correct in ["mehr", "größer"]:
                        a = "viel"
                    else:
                        a = get_word_form(correct, True)

                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Поставьте прилагательное ({a}) в сравнительную степень"

                elif markup["tag_id"] == 56:
                    new_pretask["input_type"] = 0
                    new_pretask[
                        "inf"] = f"Поставьте прилагательное ({get_word_form(correct, True)}) в превосходную степень"

                elif markup["tag_id"] == 11:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Впишите нужное наречие"

                elif markup["tag_id"] == 13:
                    new_pretask["input_type"] = 0
                    new_pretask["inf"] = f"Впишите подходящий союз в данном сравнительном обороте"

                # if int(markup["tag_id"]) not in orthographical_mistakes_ids:
                #     continue
                else:
                    continue
                    # variants = {markup["correct"]}
                    # new_pretask["markup_id"] = markup["id_markup"]
                    # # По умолчанию вид ввода упражнения будет Text, если понадобиться, то будет изменен на Dropdown
                    # new_pretask["input_type"] = 0
                    # # Случай, если ошибка - пропущенный токен(слово, знак пунктуации)
                    # if token["text"] == "-EMPTY-":
                    #     if not re.findall("[a-zA-z]", markup["correct"]):
                    #         new_pretask["inf"] = ""
                    #     else:
                    #         new_pretask["inf"] = get_word_form(markup["correct"], True)
                    # else:
                    #     new_pretask["inf"] = get_word_form(markup["correct"], True)
                    #     variants = {markup["correct"], token["text"], new_pretask["inf"]}
                    #     if new_pretask["inf"] is None or new_pretask["inf"] == "":
                    #         new_pretask["inf"] = markup["correct"]
                    #     # print(f'inf: {new_pretask["inf"]}')
                    #     # if lang_german:
                    #     #     nlpied = german_nlp(new_pretask["inf"])
                    #     # else:
                    #     #     nlpied = french_nlp(new_pretask["inf"])
                    #     nlpied = german_nlp(new_pretask["inf"])
                    #     tokenized = nlpied[0]
                    #
                    #     if tokenized.pos_ == "NOUN":
                    #         variants = variants.union(set(get_noun_forms(new_pretask["inf"])))
                    #         new_pretask["input_type"] = 1
                    # new_pretask["variants"] = list(variants)

                # if len(new_pretask) > 2:
                #     new_pretask["input_type"] = 1

                new_pretask["markup_id"] = markup["id_markup"]
                tasks.append(new_pretask)
    return tasks


def search(asked_id):
    for text in get_all_texts(size=100000):
        for sentence in text["sentences"]:
            # Цикл по каждому токену в предложении
            for token in sentence["tokens"]:
                # Получение размеки токена, и если она не пустая(len!=1), то токен содержит ошибку,
                # если len > 1 - более одной ошибки на токен
                markups = token["markups"]

                if len(markups) == 1:
                    markup = markups[0]
                    if markup["tag_id"] == asked_id:
                        print("BEGIN\n")
                        prepare_text(text, "", True)
                        print(markup)
                        print(sentence["text"])
                        print("END\n")


# Вспомогательная функция, возвращает различные формы слова, в том числе начальную.
def get_word_forms(word):
    pass


def get_noun_forms(word):
    forms = german_nouns[word]
    if not forms:
        return []
    return forms[0]["flexion"].values()


def get_word_form(word, is_language_german=True):
    """Возвращает начальную форму слова указанного языка
    :param str word: слово, которому ищется начальная форма
    :param pos[NOUN, VERB, ADJ, ADV] - Часть речи
    :param bool is_language_german: True - word есть слово немецкое, False - французское.
    """

    # if is_language_german:
    nlpied = german_nlp(word)
    for token in nlpied:
        return token.lemma_
    # else:
    #     nlpied = french_nlp(word)
    #     for token in nlpied:
    #         return token.lemma_
