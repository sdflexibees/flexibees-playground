from django.contrib import admin
from .models import ActivityCard, CandidateAvailability
# Register your models here.


class TimelineAdmin(admin.ModelAdmin):
    list_display = ['id', 'candidate', 'activity_card', 'previous_activity', 'next_activity', 'active']


admin.site.register(ActivityCard)
admin.site.register(CandidateAvailability, TimelineAdmin)
