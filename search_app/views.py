from django.shortcuts import render

def index(request):
    # Тестовый показ
    if request.get_full_path() == '/search1/':
        return render(request, "search1.html")
    elif request.get_full_path() == '/search1/Reise/':
        return render(request, "reise.html")
    elif request.get_full_path() == '/search3/':
        return render(request, "search3.html")
    
    
    return render(request, "index.html")
