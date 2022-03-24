from django.shortcuts import render
from .models import TblRights, TblUserRights

def check_permissions_show_text(request, text_id = None):
    
    if text_id == None:
        permission = TblUserRights.objects.filter(right_id = 2, user_id = request.user.id_user)
    else:
        permission = TblUserRights.objects.filter(right_id = 2, id_text = text_id, user_id = request.user.id_user)
    
    if len(permission) == 0:
        return False
    else:
        return True