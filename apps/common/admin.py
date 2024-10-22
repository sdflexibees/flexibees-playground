from django.contrib import admin
from .models import( UserType, Users, CustomRole, CustomSkill, SkillMapping, RoleMapping)

# Register your models here.
admin.site.register(UserType)
admin.site.register(Users)
admin.site.register(CustomRole)
admin.site.register(CustomSkill)
admin.site.register(SkillMapping)
admin.site.register(RoleMapping)