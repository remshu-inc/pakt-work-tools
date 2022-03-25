from django.shortcuts import render
from .models import TblRights, TblUserRights

def check_permissions_show_text(user_id, text_id = None):
    
    if text_id == None:
        permission = TblUserRights.objects.filter(right_id = 1, user_id = user_id)
    else:
        permission = TblUserRights.objects.filter(right_id = 1, id_text = text_id, user_id = user_id)
    
    if len(permission) == 0:
        return False
    else:
        return True
    
def check_permissions_new_text(user_id, text_id = None):
    
    permission = TblUserRights.objects.filter(right_id = 2, user_id = user_id)
    
    if len(permission) == 0:
        return False
    else:
        return True
    
def check_permissions_delete_text(user_id, text_id = None):
    
    if text_id == None:
        permission = TblUserRights.objects.filter(right_id = 3, user_id = user_id)
    else:
        permission = TblUserRights.objects.filter(right_id = 3, id_text = text_id, user_id = user_id)
    
    if len(permission) == 0:
        return False
    else:
        return True
    
def check_permissions_edit_text(user_id, text_id = None):
    
    if text_id == None:
        permission = TblUserRights.objects.filter(right_id = 4, user_id = user_id)
    else:
        permission = TblUserRights.objects.filter(right_id = 4, id_text = text_id, user_id = user_id)
    
    if len(permission) == 0:
        return False
    else:
        return True
    
def check_permissions_work_with_annotations(user_id, text_id = None):
    
    if text_id == None:
        permission = TblUserRights.objects.filter(right_id = 5, user_id = user_id)
    else:
        permission = TblUserRights.objects.filter(right_id = 5, id_text = text_id, user_id = user_id)
    
    if len(permission) == 0:
        return False
    else:
        return True
    