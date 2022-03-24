from django.db import models

from user_app.models import TblUser
from text_app.models import TblText

class TblRights(models.Model):
    class Meta:
        db_table = "TblRights"
    
    id_right = models.AutoField(primary_key=True)
    
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.right_name
    
class TblUserRights(models.Model):
    class Meta:
        db_table = "TblUserRights"
    
    id_user_right = models.AutoField(primary_key=True)
        
    right = models.ForeignKey(TblRights, on_delete=models.PROTECT)
    user = models.ForeignKey(TblUser, on_delete=models.PROTECT)
    text = models.ForeignKey(TblText, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.id_user_right