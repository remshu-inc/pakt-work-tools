import re

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

from generator_app.models import TblTask, TblAdditionalVariant
from text_app.models import TblToken, TblMarkup


# Возвращает упражнение по его ID.
def get_task(task_id):
    try:
        task = model_to_dict(TblTask.objects.get(task_id=task_id))
        task["variants"] = [
            dict(var)
            for var in TblAdditionalVariant.objects.filter(task_id=task_id).all().values()
        ]
        task["text_before"], task["text_after"] = get_text_before_and_after(task["markup_id"])
        if task['altered_text_before']:
            task['text_before'] = task["altered_text_before"]
        if task['altered_text_after']:
            task["text_after"] = task["altered_text_after"]
    except ObjectDoesNotExist:
        return None

    return task


# Проверяет правильность ответа на данное по ID упражнение.
def check_answer(task_id, answer):
    pattern = re.compile("\\s*" + get_answer(task_id).replace(" ", "\\s+") + "\\s*")
    return pattern.fullmatch(answer) is not None


# Возвращает правильный ответ на данное по ID упражнение.
def get_answer(task_id):
    task = model_to_dict(TblTask.objects.get(task_id=task_id))
    markup = model_to_dict(TblMarkup.objects.get(id_markup=task["markup_id"]))

    return markup["correct"]


# Возвращает упражнения по ID теста.
def get_tasks_by_test(test_id):
    return [
        get_task(task["task_id"])
        for task in list(TblTask.objects.filter(test_id=test_id).all().values())
    ]


# Принимает на вход объект упражнения, сохраняет упражнение в базе данных. Возвращает упражнение с присвоенным ID.
def save_task(data):
    task = TblTask.objects.create(
        markup_id   = TblMarkup.objects.get(id_markup=data["markup_id"]),
        inf         = data["inf"],
        input_type  = data["input_type"],
        test_id     = data["test_id"],
    )

    variants = []
    if "variants" in data:
        for var in data["variants"]:
            variants.append(model_to_dict(TblAdditionalVariant.objects.create(
                task_id = task,
                variant_text = var["variant_text"]
            )))
    
    task = model_to_dict(task)
    task["variants"] = variants

    return task


# Удаляет упражнение по его ID.
def delete_task(task_id):
    TblAdditionalVariant.objects.filter(task_id=task_id).delete()
    TblTask.objects.filter(task_id=task_id).delete()


# Возвращает кусок текста до и после поля ввода
def get_text_before_and_after(markup_id):
    markup = model_to_dict(TblMarkup.objects.get(id_markup=markup_id))

    tokens = [
        dict(token)
        for token in TblToken.objects.filter(sentence_id=markup["sentence"]).all().values()
    ]

    i = -1
    for j in range(0, len(tokens)):
        if tokens[j]["id_token"] == markup["token"]:
            i = j
            break

    text_before = ""
    for j in range(0, i):
        if (text_before != "" and not re.match("[-.?!)(,:]", tokens[j]["text"])):
            text_before += " "
        text_before += tokens[j]["text"]

    text_after = ""
    for j in range(i + 1, len(tokens)):
        if (text_after != "" and not re.match("[-.?!)(,:]", tokens[j]["text"])):
            text_after += " "
        text_after += tokens[j]["text"]

    return (text_before, text_after)