from email.policy import default
from django.db import models

from user_app.models import TblTeacher, TblUser, TblGroup, TblLanguage


class TblTextType(models.Model):
    class Meta:
        db_table = "TblTextType"

    id_text_type = models.AutoField(primary_key=True)

    text_type_name = models.CharField(max_length=100)

    language = models.ForeignKey(TblLanguage, on_delete=models.PROTECT)

    def __str__(self):
        return self.text_type_name


class TblEmotional(models.Model):
    class Meta:
        db_table = "TblEmotional"

    id_emotional = models.AutoField(primary_key=True)

    emotional_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.emotional_name


class TblWriteTool(models.Model):
    class Meta:
        db_table = "TblWriteTool"

    id_write_tool = models.AutoField(primary_key=True)

    write_tool_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.write_tool_name


class TblWritePlace(models.Model):
    class Meta:
        db_table = "TblWritePlace"

    id_write_place = models.AutoField(primary_key=True)

    write_place_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.write_place_name


class TblText(models.Model):
    YEARS = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )

    RATES = (
        (0, '-1'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )

    TASK_RATES = ((1, '1'),
                  (2, '2-'),
                  (3, '2'),
                  (4, '2+'),
                  (5, '3-'),
                  (6, '3'),
                  (7, '3+'),
                  (8, '4-'),
                  (9, '4'),
                  (10, '4+'),
                  (11, '5-'),
                  (12, '5')
                  )

    class Meta:
        db_table = "TblText"

        # делает уникальным направление обмена
        # unique_together = ("pos_check_user", "error_tag_check_user")

    id_text = models.AutoField(primary_key=True)

    user = models.ForeignKey(TblUser, blank=True, null=True, on_delete=models.SET_NULL)

    language = models.ForeignKey(TblLanguage, blank=True, null=True, on_delete=models.SET_NULL)
    text_type = models.ForeignKey(TblTextType, blank=True, null=True, on_delete=models.SET_NULL)
    emotional = models.ForeignKey(TblEmotional, blank=True, null=True, on_delete=models.SET_NULL)
    write_tool = models.ForeignKey(TblWriteTool, blank=True, null=True, on_delete=models.SET_NULL)
    write_place = models.ForeignKey(TblWritePlace, blank=True, null=True, on_delete=models.SET_NULL)

    header = models.CharField(max_length=255)
    text = models.TextField()
    create_date = models.DateField(null=True)
    modified_date = models.DateField(null=True)

    education_level = models.IntegerField(blank=True, null=True)
    self_rating = models.IntegerField(blank=True, null=True, choices=RATES)
    student_assesment = models.IntegerField(blank=True, null=True, choices=RATES)
    creation_course = models.IntegerField(choices=YEARS)

    assessment = models.IntegerField(blank=True, null=True, choices=TASK_RATES)
    completeness = models.IntegerField(blank=True, null=True, choices=TASK_RATES)
    structure = models.IntegerField(blank=True, null=True, choices=TASK_RATES)
    coherence = models.IntegerField(blank=True, null=True, choices=TASK_RATES)
    teacher = models.ForeignKey(TblTeacher, blank=True, null=True, on_delete=models.SET_NULL)

    pos_check = models.BooleanField(blank=True, null=True, default=0)
    pos_check_user = models.ForeignKey(TblUser, blank=True, null=True, on_delete=models.SET_NULL,
                                       related_name="pos_check_user")
    error_tag_check = models.BooleanField(blank=True, null=True, default=0)
    error_tag_check_user = models.ForeignKey(TblUser, blank=True, null=True, on_delete=models.SET_NULL,
                                             related_name="error_tag_check_user")
    pos_check_date = models.DateField(blank=True, null=True)
    error_tag_check_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.header

    def save(self, *args, **kwargs):
        super(TblText, self).save(*args, **kwargs)
        return self


class TblTextGroup(models.Model):
    class Meta:
        db_table = 'TblTextGroup'

    id_textgroup = models.AutoField(primary_key=True)
    text = models.ForeignKey(TblText, on_delete=models.CASCADE, db_column='text_id')
    group = models.ForeignKey(TblGroup, on_delete=models.CASCADE, db_column='group_id')


class TblSentence(models.Model):
    class Meta:
        db_table = "TblSentence"

    id_sentence = models.AutoField(primary_key=True)

    text_id = models.ForeignKey(TblText, on_delete=models.CASCADE, db_column='text_id')

    text = models.TextField()
    order_number = models.IntegerField()

    def __str__(self):
        return self.text


class TblToken(models.Model):
    class Meta:
        db_table = "TblToken"

    id_token = models.AutoField(primary_key=True)

    sentence = models.ForeignKey(TblSentence, on_delete=models.CASCADE, db_column='sentence_id')

    text = models.TextField()
    order_number = models.IntegerField()

    def __str__(self):
        return self.text


class TblMarkupType(models.Model):
    class Meta:
        db_table = "TblMarkupType"

    id_markup_type = models.AutoField(primary_key=True)

    markup_type_name = models.TextField()

    def __str__(self):
        return self.markup_type_name


class TblTag(models.Model):
    class Meta:
        db_table = "TblTag"

    id_tag = models.AutoField(primary_key=True)

    markup_type = models.ForeignKey(TblMarkupType, on_delete=models.CASCADE)
    tag_parent = models.ForeignKey('self', on_delete=models.CASCADE, null = True)
    tag_language = models.ForeignKey(TblLanguage, on_delete=models.CASCADE)

    tag_text = models.TextField()
    tag_text_russian = models.TextField()
    tag_text_abbrev = models.TextField(max_length=56, default='')
    tag_color = models.CharField(max_length=7, default="#cfcfcf")

    def __str__(self):
        return self.tag_text


class TblGrade(models.Model):
    class Meta:
        db_table = "TblGrade"

    id_grade = models.AutoField(primary_key=True)

    grade_name = models.CharField(max_length=255)
    grade_language = models.ForeignKey(TblLanguage, on_delete=models.SET_NULL, blank=True, null=True)
    grade_abbrev = models.CharField(max_length=30, default= '', null = True)

    def __str__(self):
        return self.grade_name


class TblReason(models.Model):
    class Meta:
        db_table = "TblReason"

    id_reason = models.AutoField(primary_key=True)

    reason_name = models.CharField(max_length=255)
    reason_language = models.ForeignKey(TblLanguage, blank=True, null=True, on_delete=models.SET_NULL)
    reason_abbrev = models.CharField(max_length=30, default= '', null = True)

    def __str__(self):
        return self.reason_name


class TblMarkup(models.Model):
    class Meta:
        db_table = "TblMarkup"

        # делает уникальным направление обмена
        # unique_together = ("start_token", "end_token")

    id_markup = models.AutoField(primary_key=True)

    token = models.ForeignKey(TblToken, on_delete=models.CASCADE)
    sentence = models.ForeignKey(TblSentence, on_delete=models.CASCADE)
    tag = models.ForeignKey(TblTag, on_delete=models.CASCADE)

    user = models.ForeignKey(TblUser, blank=True, null=True, on_delete=models.SET_NULL)

    # start_token = models.ForeignKey(TblToken, on_delete=models.CASCADE, related_name="start_token", db_column='start_token')
    # end_token = models.ForeignKey(TblToken, on_delete=models.CASCADE, related_name="end_token", db_column='end_token')

    grade = models.ForeignKey(TblGrade, blank=True, null=True, on_delete=models.SET_NULL)
    reason = models.ForeignKey(TblReason, blank=True, null=True, on_delete=models.SET_NULL)

    correct = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    change_date = models.DateField()

    def __str__(self):
        return self.id_markup


class TblTokenMarkup(models.Model):
    class Meta:
        db_table = "TblTokenMarkup"

    id_token_markup = models.AutoField(primary_key=True)

    token = models.ForeignKey(TblToken, on_delete=models.CASCADE)
    markup = models.ForeignKey(TblMarkup, on_delete=models.CASCADE)

    position = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.id_token_markup


class TblMarkError(models.Model):
    class Meta:
        db_table = 'TblMarkError'

    idrecord = models.AutoField(primary_key=True)

    typeerror = models.CharField(max_length=25, null=True, default=None)
    mark = models.CharField(max_length=2, null=True, default=None)

    grade3 = models.IntegerField(default=None)
    grade2 = models.IntegerField(default=None)
    grade1 = models.IntegerField(default=None)
