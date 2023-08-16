from django.db.models import Q
from .models import TblUserRights, TblText, TblUser


def check_permissions_show_text(user_id, text_id=None):
    
    permission = TblUserRights.objects.filter(
        Q(text_id=text_id) | Q(text_id=None),
        right_id=1, user_id=user_id,
    )

    ownText = TblText.objects.filter(id_text=text_id, user_id=user_id)
    return ownText.exists() or permission.exists()


def check_permissions_new_text(user_id, text_id=None):
    permission = TblUserRights.objects.filter(
        Q(text_id=text_id) | Q(text_id=None),
        right_id=2, user_id=user_id,
    )

    return permission.exists()


def check_permissions_delete_text(user_id, text_id=None):
    permission = TblUserRights.objects.filter(
        Q(text_id=text_id) | Q(text_id=None),
        right_id=3, user_id=user_id,
    )

    return permission.exists()


def check_permissions_edit_text(user_id, text_id=None):
    permission = TblUserRights.objects.filter(
        Q(text_id=text_id) | Q(text_id=None),
        right_id=4, user_id=user_id,
    )

    return permission.exists()


def check_permissions_work_with_annotations(user_id, text_id):
    user_language = TblUser.objects.filter(id_user=user_id).first().language_id
    text_language = TblText.objects.filter(id_text=text_id).first().language_id
    if (text_language != user_language):
        return False
    
    permission = TblUserRights.objects.filter(
        Q(text_id=text_id) | Q(text_id=None),
        right_id=5, user_id=user_id,
    )

    return permission.exists()


def check_is_superuser(user_id):
    permission = TblUserRights.objects.filter(
        right_id=6, user_id=user_id,
    )

    return permission.exists()
