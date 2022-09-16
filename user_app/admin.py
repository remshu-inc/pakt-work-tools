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
        "course_number",
        "user_id",
    )
    list_filter = (
        "id_student",
    )
    list_editable = (
        "birthdate",
        "gender",
        "course_number",
    )
    search_fields = (
        "birthdate",
        "gender",
        "course_number",
    )

    date_hierarchy = "birthdate"
    save_on_top = True


# Register your models here.
