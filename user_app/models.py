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
    
    # TODO: Логин и Пароль blank=False и null=False
    login = models.CharField(max_length=100, unique=True, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, blank=True, null=True)
    
    # For admin
    # is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'login'
    
    objects = CustomUserManager()
    ordering = ["last_name"]

    def __str__(self):
        return self.last_name + ' ' + self.name
    
    def is_teacher(self):
        teacher = TblTeacher.objects.filter(user_id = self.id_user)
        if len(teacher) != 0:
            return True
        else:
            return False
        
    
class TblTeacher(models.Model):
    class Meta:
        db_table = "TblTeacher"
        
    id_teacher = models.AutoField(primary_key=True)
    
    user = models.ForeignKey(TblUser, on_delete=models.CASCADE)
    
    # TODO: исправить
    def __str__(self):
        return self.user.last_name + ' ' + self.user.name
    
class TblStudent(models.Model):
    GENDER = (
        (0, 'Мужчина'),
        (1, 'Женщина'),
    )
    
    class Meta:
        db_table = "TblStudent"
        
    id_student = models.AutoField(primary_key=True)
    
    user = models.ForeignKey(TblUser, on_delete=models.CASCADE)
    
    # ???: поле birthdate пустое?
    birthdate = models.DateField(blank=True, null=True)
    gender = models.BooleanField(blank=True, null=True, choices=GENDER)
    # group_number = models.IntegerField()
    course_number = models.IntegerField()
    deduction = models.DateField(blank=True, null=True)
    
    # TODO: исправить
    def __str__(self):
        return self.user.last_name + ' ' + self.user.name
    
    def save(self, *args, **kwargs):
        super(TblStudent, self).save(*args, **kwargs) 
        return self


class TblGroup(models.Model):
    
    class Meta:
        db_table = 'TblGroup'

    id_group =  models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=256)
    enrollement_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.group_name + ' - ' + str(self.enrollement_date)
    
    


class TblStudentGroup(models.Model):

    class Meta:
        db_table = 'TblStudentGroup'

    id_studentgroup = models.AutoField(primary_key=True)
    student = models.ForeignKey(TblStudent, on_delete=models.CASCADE)
    group = models.ForeignKey(TblGroup, on_delete=models.CASCADE)
    current = models.BooleanField(default=False)
    
    def __str__(self):
        return self.group.group_name + ' ' + self.student.user.last_name + ' ' + self.student.user.name