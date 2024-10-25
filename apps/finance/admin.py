from django.contrib import admin
from apps.finance.models import BankAccount, Consultant, SocialMedia

admin.site.register(SocialMedia)
admin.site.register(BankAccount)
admin.site.register(Consultant)
# admin.site.register(ConsultantContract)