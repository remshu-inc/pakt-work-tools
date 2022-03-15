from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .managers import CustomUserManager

class TblUser(AbstractBaseUser, PermissionsMixin):
    class Meta:
        db_table = "TblUser"
        
    id_user = models.AutoField(primary_key=True)
    
    user_permissions = None
    last_login = None
    is_superuser = None
    groups = None
    
    login = models.CharField(max_length=100, unique=True, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100)
    
    # For admin
    # is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'login'
    
    objects = CustomUserManager()

    def __str__(self):
        return self.last_name + ' ' + self.name
    
class TblTeacher(models.Model):
    class Meta:
        db_table = "TblTeacher"
        
    id_teacher = models.AutoField(primary_key=True)
    
    user_id = models.OneToOneField(TblUser, on_delete=models.CASCADE)
    
    # TODO: исправить
    def __str__(self):
        return 'self.id_teacher'
    
class TblStudent(models.Model):
    GENDER = (
        (0, 'Мужчина'),
        (1, 'Женщина'),
    )
    
    class Meta:
        db_table = "TblStudent"
        
    id_student = models.AutoField(primary_key=True)
    
    birthdate = models.DateField(blank=True, null=True)
    gender = models.BooleanField(blank=True, null=True, choices=GENDER)
    group_number = models.IntegerField()
    course_number = models.IntegerField()
    deduction = models.DateField(blank=True, null=True)
    
    user_id = models.OneToOneField(TblUser, on_delete=models.CASCADE)
    
    # TODO: исправить
    def __str__(self):
        return 'self.id_student'
    
# @receiver(post_save, sender=User)
# def update_profile_signal(sender, instance, created, **kwargs):
#     if created:
#         TblUser.objects.create(user=instance)
#     instance.profile.save()