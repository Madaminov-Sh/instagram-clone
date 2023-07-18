from django.contrib import admin
from .models import User, UserComfirmation


class UserConfirmationAdmin(admin.ModelAdmin):
    list_display = ('user', 'expiration_time', 'is_confirmed')

admin.site.register(UserComfirmation, UserConfirmationAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username','email', 'user_rules', 'phone_number', 'created_time', "auth_status")
    
admin.site.register(User, UserAdmin)



