from django.db import models
from user_app.models import TblLanguage


from datetime import datetime

# Create your models here.
class TblSystemMetric(models.Model):
    class Meta:
        db_table = 'TblSystemMetric'

    id_metric = models.AutoField(primary_key=True)
    language = models.ForeignKey(TblLanguage, null = True, on_delete=models.PROTECT)
    metric_name = models.CharField(max_length=255)
    metric_value = models.FloatField(default=0)
    metric_update_time = models.DateTimeField(default=datetime(1970,1,1), null=False)


