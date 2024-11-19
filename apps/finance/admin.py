from django.contrib import admin
from apps.finance.models import BankAccount, Client, Consultant, Contract, SocialMedia

admin.site.register(SocialMedia)
admin.site.register(BankAccount)
admin.site.register(Client)
admin.site.register(Consultant)
admin.site.register(Contract)