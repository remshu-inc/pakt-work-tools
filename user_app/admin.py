from django.contrib import admin

from user_app.models import TblUser, TblTeacher, TblStudent

# Отображение таблицы TblUser
@admin.register(TblUser)
class TblUserAdmin(admin.ModelAdmin):
    model = TblUser
    
# Отображение таблицы TblUser
@admin.register(TblTeacher)
class TblTeacherAdmin(admin.ModelAdmin):
    model = TblTeacher
    
# Отображение таблицы TblUser
# @admin.register(TblStudent)
# class TblStudentAdmin(admin.ModelAdmin):
#     model = TblStudent

# @admin.register(TblStudent)
# class TblStudentAdmin(admin.ModelAdmin):
#     model = TblStudent

# @admin.register(TblTeacher)
# class TblTeacherAdmin(admin.ModelAdmin):
#     model = TblTeacher
    
@admin.register(TblStudent)
class TblStudentAdmin(admin.ModelAdmin):
    model = TblStudent

    list_display = (
        "id_student",
        "birthdate",
        "gender",
        "group_number",
        "course_number",
        "user_id",
    )
    list_filter = (
        "id_student",
        "group_number",
    )
    list_editable = (
        "birthdate",
        "gender",
        "group_number",
        "course_number",
    )
    search_fields = (
        "birthdate",
        "gender",
        "group_number",
        "course_number",
    )

    date_hierarchy = "birthdate"
    save_on_top = True


# Register your models here.
