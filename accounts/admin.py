from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user','full_name','phone','created_at')
    search_fields = ('user__username','full_name','phone')
    list_per_page = 25
from django.contrib import admin

# Register your models here.
