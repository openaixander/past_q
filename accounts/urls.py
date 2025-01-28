from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('registration/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/', views.reset_password, name='reset_password'),

    path('lecturer_info/', views.lecturer_info, name='lecturer_info'),
    path('lecturer_waiting/', views.lecturer_waiting, name='lecturer_waiting'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),
]