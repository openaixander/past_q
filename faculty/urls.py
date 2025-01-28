from django.urls import path
from . import views


app_name = 'faculty'

urlpatterns = [
    path('', views.index, name='index'),
    path('choice/', views.choice, name='choice'),
    path('about-pastq/', views.about_pastq, name='about_pastq'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('view-or-download-pastq/', views.view_or_download_pastq, name='view_or_download_pastq'),
    path('process-past-question-form/', views.process_past_question_form, name='process_past_question_form'),
    path('view-past-question/<int:pk>/', views.view_past_question, name='view_past_question'),
    path('no-past-question-found/', views.no_past_question_found, name='no_past_question_found'),
    path('download-pastq-images/<int:pk>/', views.download_pastq_images, name='download_pastq_images'),


    path('search-materials/', views.download_materials, name='download_materials'),
    path('process-materials/', views.process_materials, name='process_materials'),
    path('download-study-materials/<int:pk>/', views.download_study_materials, name='download_study_materials'),
    path('download-file/<int:pk>/', views.download_file, name='download_file'),
    path('download-multiple-files/<int:pk>/', views.download_multiple_files, name='download_multiple_files'),
    path('no-material-found/', views.no_download_materials_found, name='no_download_materials_found'),

    path('lecturer-dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('upload-pastq/', views.upload_pastq, name='upload_pastq'),
    path('load-courses/', views.load_courses, name='load_courses'),
    path('upload-study-material/', views.upload_study_material, name='upload_study_material'),
    path('load-courses-for-material/', views.load_courses_for_material, name='load_courses_for_material'),
    

]

