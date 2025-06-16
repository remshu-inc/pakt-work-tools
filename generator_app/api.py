import json

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

from generator_app.models import TblAssignedTest, TblTask
from generator_app.views.task_controller import check_answer
from generator_app.views.test_controller import create_test, delete_test, get_test, save_task_status_by_test_and_stud, \
    is_test_assigned, send_test_to_stud, unsend_test_to_stud, complete_test, get_studs_by_test, generate_docx, \
    generate_report
from generator_app.views.test_generator import get_user_texts, generate_tasks, get_text
from user_app.models import TblUser
from .models import TblTest


def api_get_student_texts_names(request, student_id):
    if request.method == 'POST':
        return (HttpResponseBadRequest('Request should be GET'))

    texts = get_user_texts(student_id)
    texts = [
        dict(id_text=text["id_text"], header=text["header"])
        for text in texts
    ]

    return (JsonResponse(texts, safe=False))

def api_change_task_texts(request):
    if request.method == 'POST':
        params = json.loads(request.body.decode('utf-8'))
    else:
        return (HttpResponseBadRequest('Request should be POST'))
    
    # print(params)
    rspns = {
        "success": [],
        "error": {}
    }
    for entry in params:
        task_id = int(entry["task_id"])
        half_id = entry['half']
        try:
            task = TblTask.objects.get(task_id=task_id)
            # print(model_to_dict(task))
            if half_id == 'before':
                task.altered_text_before = entry['new_text']
            elif half_id == 'after':
                task.altered_text_after = entry['new_text']
            else:
                rspns['error'][f"task_id_{half_id}": "broken half"]
                continue
            task.save()
            rspns['success'].append(task_id)
        except ObjectDoesNotExist:
            rspns['error']['task_id': "doesn't exist"]
    return JsonResponse(rspns, safe=False)

def api_generate_tasks(request):
    if request.method == 'POST':
        parametres = json.loads(request.body.decode('utf-8'))
    else:
        return (HttpResponseBadRequest('Request should be POST'))

    tasks = generate_tasks(parametres)

    return (JsonResponse(tasks, safe=False))

def api_create_test(request):
    if request.method == 'POST':
        test = json.loads(request.body.decode('utf-8'))
    else:
        return (HttpResponseBadRequest('Request should be POST'))

    if not request.user.is_authenticated:
        return (HttpResponseBadRequest('Аццесс денаед'))

    test["creator"] = request.user.id_user
    saved_test = create_test(test)

    if (request.user.is_student()):
        send_test_to_stud(saved_test["test_id"], request.user.id_user)

    return (JsonResponse(saved_test, safe=False))


def api_delete_test(request):
    if request.method == 'DELETE':
        test_id = json.loads(request.body.decode('utf-8'))["test_id"]
    else:
        return (HttpResponseBadRequest('Request should be DELETE'))

    if not request.user.is_authenticated:
        return (HttpResponseBadRequest('Аццесс денаед'))

    test = get_test(test_id)
    if (test == None):
        return (HttpResponseBadRequest('А где.'))
        
    if (test["creator"] != request.user.id_user):
        return (HttpResponseBadRequest('Аццесс вери денаед (ю каннот делит не ваш тест)'))

    delete_test(test_id)

    return HttpResponse("okay")

def api_save_student_answer(request):
    if request.method == 'POST':
        test_id = json.loads(request.body.decode('utf-8'))["test_id"]
        task_id = json.loads(request.body.decode('utf-8'))["task_id"]
        stud_answer = json.loads(request.body.decode('utf-8'))["stud_answer"]
    else:
        return (HttpResponseBadRequest('Request should be POST'))

    if not request.user.is_authenticated:
        return (HttpResponseBadRequest('Аццесс денаед'))

    stud_id = request.user.id_user

    if not is_test_assigned(test_id, stud_id):
        return (HttpResponseBadRequest('А тест то не назначен!'))

    save_task_status_by_test_and_stud(task_id, test_id, stud_id, stud_answer)
    status = check_answer(task_id, stud_answer)
    
    return (JsonResponse({"status": status}, safe=False))

def api_save_test_results(request):
    if request.method == 'POST':
        test_id = json.loads(request.body.decode('utf-8'))["test_id"]
    else:
        return (HttpResponseBadRequest('Request should be POST'))

    if not request.user.is_authenticated:
        return (HttpResponseBadRequest('Аццесс денаед'))

    stud_id = request.user.id_user

    if not is_test_assigned(test_id, stud_id):
        return (HttpResponseBadRequest('А тест то не назначен!'))

    assign = complete_test(test_id, stud_id)
    
    return (JsonResponse(assign, safe=False))

def api_send_student_test(request):
    if request.method == 'POST':
        test_id = json.loads(request.body.decode('utf-8'))["test_id"]
        stud_id = json.loads(request.body.decode('utf-8'))["stud_id"]
    else:
        return (HttpResponseBadRequest('Request should be POST'))

    if not request.user.is_authenticated or not request.user.is_teacher():
        return (HttpResponseBadRequest('Аццесс денаед'))

    test = get_test(test_id)
    if (test == None):
        return (HttpResponseBadRequest('А где.'))
        
    if (test["creator"] != request.user.id_user):
        return (HttpResponseBadRequest('Аццесс вери денаед (ю каннот сенд не ваш тест)'))

    send_test_to_stud(test_id, stud_id)
    
    return HttpResponse("okay")

def api_unsend_student_test(request):
    if request.method == 'POST':
        test_id = json.loads(request.body.decode('utf-8'))["test_id"]
        stud_id = json.loads(request.body.decode('utf-8'))["stud_id"]
    else:
        return (HttpResponseBadRequest('Request should be POST'))

    if not request.user.is_authenticated or not request.user.is_teacher():
        return (HttpResponseBadRequest('Аццесс денаед'))

    test = get_test(test_id)
    if (test == None):
        return (HttpResponseBadRequest('А где.'))
        
    if (test["creator"] != request.user.id_user):
        return (HttpResponseBadRequest('Аццесс вери денаед (ю каннот сенд не ваш тест)'))

    unsend_test_to_stud(test_id, stud_id)
    
    return HttpResponse("okay")

def api_downlad_docx(request):
    if request.method == 'POST':
        test_id = json.loads(request.body.decode('utf-8'))["test_id"]
    else:
        return (HttpResponseBadRequest('Request should be POST'))
    document = generate_docx(test_id)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=download.docx'

    document.save(response)

    return response

def api_make_report(request):
    if request.method == 'POST':
        test_ids = json.loads(request.body.decode('utf-8'))["test_ids"]
        stud_ids = json.loads(request.body.decode('utf-8'))["stud_ids"]
    else:
        return (HttpResponseBadRequest('Request should be POST'))
    document = generate_report(stud_ids, test_ids)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=download.docx'

    document.save(response)

    return response

















def api_get_all_tests_very_secret(request):
    tests = [
        get_test(test["test_id"])
        for test in TblTest.objects.all().values()
    ]

    for test in tests:
        test["author_name"] = str(TblUser.objects.get(id_user=test["creator"]))

    

    return (JsonResponse(tests, safe=False))

def api_get_text_very_secret(request, text_id):
    text = get_text(text_id)

    return (JsonResponse(text, safe=False))

def api_get_studs_by_test_very_secret(request, test_id):
    studs = get_studs_by_test(test_id)
    for stud in studs:
        stud["solving_status"] = model_to_dict(TblAssignedTest.objects.get(user_id=stud["id_student"], test_id=test_id))

    return (JsonResponse(studs, safe=False))
