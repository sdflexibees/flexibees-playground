from django.contrib import admin

from apps.admin_app.models import AdminUser, Configuration, Function, Skill, Domain, Role, Tags, Token, ZOHOToken, \
    Dropdown, Language, AppVersion

admin.site.register(AdminUser)
admin.site.register(Configuration)
admin.site.register(Function)
admin.site.register(Skill)
admin.site.register(Domain)
admin.site.register(Role)
admin.site.register(Tags)
admin.site.register(Token)
admin.site.register(ZOHOToken)
admin.site.register(Dropdown)
admin.site.register(Language)
admin.site.register(AppVersion)
