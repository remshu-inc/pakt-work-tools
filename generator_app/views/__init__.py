from datetime import datetime

from django.forms.models import model_to_dict
from django.shortcuts import render, redirect

import generator_app.views.test_controller as TestController
from generator_app import api
from generator_app.models import TblTest, TblAssignedTest, TblUserAnswer
from generator_app.views.task_controller import check_answer, get_answer
from generator_app.views.test_controller import get_test_status_by_stud, start_test
from user_app.models import TblUser, TblStudent


# prof/stud main menu
def main_menu(request):
    if not request.user.is_authenticated:
        return redirect('login')

    is_teacher = request.user.is_teacher()
    is_student = request.user.is_student()
    context = {'is_teacher': is_teacher, 'is_student': is_student}
    return render(request, 'generator_app/menu.html', context=context)

# prof/stud list of created tests
def test_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_student():
        alltestlist = TestController.get_tests_id_by_stud(request.user.id_user)
        testlist = [t for t in alltestlist if t["creator"] == request.user.id_user]
        for test in testlist:
            answers = get_test_status_by_stud(test["test_id"], request.user.id_user)
            tasks = test["tasks"]
            
            for task in tasks:
                for ans in answers:
                    if ans["task_id_id"] is task["task_id"]:
                        task["ans"] = ans["user_input"]

            total_am = len(tasks)
            right_am = 0
            for task in tasks:
                if check_answer(task["task_id"], task.get("ans", "")):
                    right_am += 1

            test["right_am"] = right_am
            test["total_am"] = total_am

    if request.user.is_teacher():
        testlist = TestController.get_tests_id_by_prof(request.user.id_user)

    context = {
        'is_teacher': request.user.is_teacher(),
        'is_student': request.user.is_student(),
        'testlist': testlist
    }
    return render(request, 'generator_app/my tests.html', context=context)

# stud list of assigned tests
def assigned_tests(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_teacher():
        return redirect('generator_app:main_menu')
    # where assigned test getter
    testlist = TestController.get_tests_id_by_stud(request.user.id_user)
    assigned = [t for t in testlist if t["creator"] != request.user.id_user]
    for t in assigned:
        t["status"] = model_to_dict(TblAssignedTest.objects.get(test_id=t["test_id"], user_id=request.user.id_user))
    context = {'testlist': assigned}
    return render(request, 'generator_app/tests from tutor.html', context=context)

# prof list of all tests
def all_tests(request):
    if not (request.user.is_authenticated and request.user.is_teacher()):
        return render(request, 'access_denied.html', status=403)
    tests = [
        api.get_test(test["test_id"])
        for test in TblTest.objects.all().values()
    ]
    for test in tests:
        test["author_name"] = str(TblUser.objects.get(id_user=test["creator"]))
    context = {'testlist': tests}
    return render(request, 'generator_app/all tests ALL OF THEM.html', context=context)

# prof list of students assigned to a test
def assigned_students(request, test_id):
    if not (request.user.is_authenticated and request.user.is_teacher()):
        return render(request, 'access_denied.html', status=403)
    test = api.get_test(test_id)
    studentInfo = TestController.get_studs_by_test(test_id)
    all_count = len(test["tasks"])
    for stud in studentInfo:
        stud["solving_status"] = model_to_dict(TblAssignedTest.objects.get(user_id=stud["user"], test_id=test_id))
        qans = TblUserAnswer.objects.filter(test_id=test_id, user_id=stud["user"]).all().values()
        solved_count = 0
        for t in qans:
            if check_answer(t["task_id_id"], t["user_input"]):
                solved_count += 1

        stud["solved_count"] = solved_count
        if stud["solving_status"]["finish_date"]:
            # stud["solving_status"]["finish_date"] = 
            stud["solve_time"] = stud["solving_status"]["finish_date"] - stud["solving_status"]["start_date"]
            stud["average_time"] = datetime.utcfromtimestamp((stud["solve_time"] / all_count).total_seconds()).strftime("%H:%M:%S")
            stud["solve_time"] = datetime.utcfromtimestamp(stud["solve_time"].total_seconds()).strftime("%H:%M:%S")

    context = {
        'students': studentInfo,
        'test': test,
        'all_count': all_count,
    }
    return render(request, 'generator_app/test result all students.html', context=context)

# prof view student's answers
def view_answers(request, test_id, stud_id):
    if not (request.user.is_authenticated and request.user.is_teacher()):
        return render(request, 'access_denied.html', status=403)
    test = api.get_test(test_id)
    qans = TblUserAnswer.objects.filter(test_id=test_id, user_id=stud_id).all().values()
    qtasks = test["tasks"]
    ans = [t for t in qans]
    tasks = []
    for t in qtasks:
        answer = list(filter(lambda task: task["task_id_id"] == t["task_id"], ans))
        if answer:
            status = check_answer(t["task_id"], answer[0]["user_input"])
            t["answer"] = answer[0]
            t["answer"]["status"] = status
        else:
            t["answer"] = {}
        tasks.append(t)
    studentInfo = TestController.get_studs_by_test(test_id)
    stud = list(filter(lambda s: s['user'] == stud_id, studentInfo))
    context = {
        "test": test,
        "stud": stud[0]
    }
    l = len(test["tasks"])
    context["length"] = l
    exercises = []
    if l >= 1:
        for i in range(l):
            exercises.append(tasks[i])
        # context["first"] = tasks[0]
        context["exercises_mid"] = exercises
        # context["last"] = tasks[l-1]
    context["solving_status"] = model_to_dict(TblAssignedTest.objects.get(user_id=stud_id, test_id=test_id))
    return render(request, 'generator_app/test result.html', context=context)

# prof/stud generator settings menu
def generator_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')

    language_id=request.user.language_id
    is_teacher = request.user.is_teacher()
    is_student = request.user.is_student()
    context = {}

    if is_teacher:
        '''
        stud_id = -1
        if is_student:
            stud_id = request.user.id_user
            context['student'] = request.user.id_user
        else:
            try:
                stud_id = request.GET['stud-id']
            except:
                stud_id = -1
                context['student'] = None
            else:
                context['student'] = TblUser.objects.get(pk=stud_id)
        '''
        # Text choice
        # texts = TblText.objects.filter(language_id=language_id)
        '''
        if stud_id != -1:
            texts = [
                dict(text, sentences=[])
                for text in TblText.objects.filter(user_id=stud_id).all().values()
            ]
            context['texts'] = texts
        else:
            context['texts'] = []
        '''
        students_ids = [s.user_id for s in TblStudent.objects.all()]
        students = TblUser.objects.filter(id_user__in=students_ids).all().values()
        context['students'] = sorted([s for s in students], key=lambda s: s['last_name'])
        # print(sorted(students, key=lambda s: s['last_name']))
        # context['students'] = [s for s in students]
        return render(request, 'generator_app/assemble.html', context=context)
    elif is_student:
        context['stud_id'] = request.user.id_user
        return render(
            request,
            "generator_app/assemble student.html",
            context
        )

# prof preview test
def preview(request, test_id):
    if not (request.user.is_authenticated and request.user.is_teacher()):
        return render(request, 'access_denied.html', status=403)
    test = TestController.get_test(test_id)
    context = {'test': test}
    l = len(test["tasks"])
    context["length"] = l
    exercises_mid = []
    if l >= 1:
        for i in range(l):
            exercises_mid.append(test["tasks"][i])
            exercises_mid[i]["answer"] = get_answer(test['tasks'][i]['task_id'])
        context["exercises"] = exercises_mid
        # print(exercises_mid)
    return render(request, 'generator_app/test preview.html', context=context)

# prof assign menu
def send_test(request, test_id):
    if not (request.user.is_authenticated and request.user.is_teacher()):
        return render(request, 'access_denied.html', status=403)
    context = {
        'test_id': test_id
    }
    students_ids = [s.user_id for s in TblStudent.objects.all()]
    students = TblUser.objects.filter(id_user__in=students_ids).all().values()
    context['students'] = [s for s in students]
    return render(request, 'generator_app/send test.html', context=context)

# stud test solver menu
def test_solver(request, test_id):
    if not request.user.is_authenticated and request.user.is_student:
        return redirect('main_menu')

    stud_id = request.user.id_user
    test = api.get_test(test_id)
    context = {"test": test}
    l = len(test["tasks"])
    context["length"] = l
    qans = TblUserAnswer.objects.filter(test_id=test_id, user_id=stud_id).all().values()
    qtasks = test["tasks"]
    ans = [t for t in qans]
    for t in qtasks:
        answer = list(filter(lambda task: task["task_id_id"] == t["task_id"], ans))
        if answer:
            status = check_answer(t["task_id"], answer[0]["user_input"])
            t["answer"] = answer[0]
            t["answer"]["status"] = status
        else:
            t["answer"] = {}
    test["tasks"] = qtasks

    context["exercises"] = test["tasks"]
    context["my_test"] = (test["creator"] == stud_id)
    
    start_test(test_id, stud_id)
    return render(request, 'generator_app/pass test.html', context=context)


def make_report(request):
    if not (request.user.is_authenticated and request.user.is_teacher()):
        return render(request, 'access_denied.html', status=403)

    context = {}

    students = TblUser.objects.all().values()
    context['students'] = [s for s in students]
    context['tests'] = [
        api.get_test(test["test_id"])
        for test in TblTest.objects.all().values()
    ]

    return render(
        request,
        "generator_app/make_report.html",
        context
    )
