from django.contrib import admin
from apps.finance.models import BankAccount, Client, ClientInvoice, Consultant, ConsultantInvoice, Contract, SocialMedia

admin.site.register(SocialMedia)
admin.site.register(BankAccount)
admin.site.register(Client)
admin.site.register(Consultant)
admin.site.register(Contract)
admin.site.register(ConsultantInvoice)
admin.site.register(ClientInvoice)