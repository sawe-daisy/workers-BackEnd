from django.contrib import admin
from .models import User, Jobpost, Reviews, Profile, jobcategory
from django.contrib import admin

# Register your models here.
admin.site.register(User)
admin.site.register(Jobpost)
admin.site.register(jobcategory)
admin.site.register(Profile)
admin.site.register(Reviews)


class Review_Admin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(active=True)