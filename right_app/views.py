from django.shortcuts import render
from .models import TblRight, TblUserRights

def check_permissions_text(id_user):
    
    permission = TblUserRights.objects.filter(user_id = id_user)
    
    if len(permission) == 0:
        return False
    else:
        return True