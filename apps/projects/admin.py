from django.contrib import admin

from .models import Project, Requirement, FlexiDetails, OtherProjectDetail, ClientDetail, Pricing, Suspended, Closed, \
    Reopen


admin.site.register(Project)
admin.site.register(Requirement)
admin.site.register(FlexiDetails)
admin.site.register(OtherProjectDetail)
admin.site.register(ClientDetail)
admin.site.register(Pricing)
admin.site.register(Suspended)
admin.site.register(Closed)
admin.site.register(Reopen)
