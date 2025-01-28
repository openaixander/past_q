from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, LecturerProfile
# Register your models here.


@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = (
        'full_name',
        'email',
        'username',
        'phone_number',
        'last_login',
        'is_active',
        'is_approved',
    )


    readonly_fields = (
        'last_login',
        'is_active',
        'is_lecturer',
    )


    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

@admin.register(LecturerProfile)
class LecturerProfileAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id',
        'department',
        'office_number',
        'faculty_position',
        'id_card',
    ]

    readonly_fields = [
        'user'
    ]