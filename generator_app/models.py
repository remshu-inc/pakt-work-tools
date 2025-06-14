from django.db import models 

from user_app.models import TblTeacher, TblUser
from text_app.models import TblMarkup, TblText

class TblTest(models.Model):
    class Meta:
        db_table = "TblTest"

    test_id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(TblUser, on_delete=models.PROTECT)
    create_date = models.DateTimeField(null=True)
    name = models.CharField(max_length=100)
    score_for_3 = models.FloatField()
    score_for_4 = models.FloatField()
    score_for_5 = models.FloatField()


class TblTask(models.Model):
    class Meta:
        db_table = "TblTask"

    task_id = models.AutoField(primary_key=True)
    markup_id = models.ForeignKey(TblMarkup, on_delete=models.PROTECT)
    inf = models.CharField(max_length=100)
    input_type = models.SmallIntegerField(blank=False, null=False, default = 0)
    test_id = models.ForeignKey(TblTest, on_delete=models.PROTECT)
    altered_text_before = models.CharField(max_length=500, blank=True, null=True)
    altered_text_after = models.CharField(max_length=500, blank=True, null=True)


class TblAdditionalVariant(models.Model):
    class Meta:
        db_table = "TblAdditionalVariant"
    
    variant_id = models.AutoField(primary_key=True)
    task_id = models.ForeignKey(TblTask, on_delete=models.PROTECT)
    variant_text = models.CharField(max_length=100)

    def __str__(self):
        return self.variant_text


class TblAssignedTest(models.Model):
    class Meta:
        db_table = "TblAssignedTest"

    assigned_test_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(TblUser, on_delete=models.PROTECT)
    test_id = models.ForeignKey(TblTest, on_delete=models.PROTECT)
    start_date = models.DateTimeField(null=True)
    finish_date = models.DateTimeField(null=True)
    score = models.SmallIntegerField(null=True)


class TblUserAnswer(models.Model):
    class Meta:
        db_table = "TblUserAnswer"
    user_answer_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(TblUser, on_delete=models.PROTECT)
    test_id = models.ForeignKey(TblTest, on_delete=models.PROTECT)
    task_id = models.ForeignKey(TblTask, on_delete=models.PROTECT)
    user_input = models.CharField(max_length=100)

    def __str__(self):
        return self.user_input