from django.contrib import admin


from .models import StudentDashboardCard, Department, Level, Semester, Course, Session, PastQuestion, Image, LecturerDashboardCard, StudyMaterial
# Register your models here.

@admin.register(LecturerDashboardCard)
class DashboardCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'action_text', 'order')
    list_editable = ('order',)

@admin.register(StudentDashboardCard)
class DashboardCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'action_text', 'order')
    list_editable = ('order',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = [
        'name'
    ]

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['value']

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = [
        'name'
    ]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
    ]

@admin.register(Session)
class YearAdmin(admin.ModelAdmin):
    list_display =[
        'value'
    ]

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

@admin.register(PastQuestion)
class PastQuestionAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = ['course', 'year']   
  

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['past_question', 'page_number', 'image']
    list_filter = ['past_question__course']

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    pass