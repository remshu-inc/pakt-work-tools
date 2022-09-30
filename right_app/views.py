from django.shortcuts import render
from django.db.models import Q
from .models import TblRights, TblUserRights, TblText


def check_permissions_show_text(user_id, text_id = None):
    
    permission = TblUserRights.objects.filter(
        Q(text_id = text_id) | Q(text_id = None),
        right_id = 1, user_id = user_id,
        )
    
    if len(permission) == 0:
        if len(TblText.objects.filter(id_text = text_id, user_id = user_id)) != 0:
            return True
 
        return False
    else:
        return True
 
    
def check_permissions_new_text(user_id, text_id = None):
    
    permission = TblUserRights.objects.filter(
        Q(text_id = text_id) | Q(text_id = None),
        right_id = 2, user_id = user_id,
        )
    
    if len(permission) == 0:
        return False
    else:
        return True
    
def check_permissions_delete_text(user_id, text_id = None):
    
    permission = TblUserRights.objects.filter(
        Q(text_id = text_id) | Q(text_id = None),
        right_id = 3, user_id = user_id,
        )
    
    if len(permission) == 0:
        return False
    else:
        return True
    
def check_permissions_edit_text(user_id, text_id = None):
    
    permission = TblUserRights.objects.filter(
        Q(text_id = text_id) | Q(text_id = None),
        right_id = 4, user_id = user_id,
        )
    
    if len(permission) == 0:
        return False
    else:
        return True
    
def check_permissions_work_with_annotations(user_id, text_id = None):
    
    permission = TblUserRights.objects.filter(
        Q(text_id = text_id) | Q(text_id = None),
        right_id = 5, user_id = user_id,
        )
    
    if len(permission) == 0:
        return False
    else:
        return True
    
    
def check_is_superuser(user_id):
    
    permission = TblUserRights.objects.filter(
        right_id = 6, user_id = user_id,
        )
    
    if len(permission) == 0:
        return False
    else:
        return True