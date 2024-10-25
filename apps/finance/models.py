from datetime import date
from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.common.models import Users




CONTRACT_STATUS = (
    ('1',"Draft"),
    ('2',"Shared"),
    ('3',"Signed"),
    ('4',"In Progress")    
)

CONTRACT_TYPES = (
    ('1',"Internal Consultant"),
    ('2',"External Consultant"),
    ('3',"Placement")
)


class SocialMedia(models.Model):
    user = models.ForeignKey(Users, on_delete=models.DO_NOTHING, null=True)
    facebook_profile = models.URLField(_("Facebook Profile URL"), blank=True, null=True)
    instagram_profile = models.URLField(_("Instagram Profile URL"), blank=True, null=True)
    linkedin_profile = models.URLField(_("LinkedIn Profile URL"), blank=True, null=True)
    twitter_profile = models.URLField(_("Twitter Profile URL"), blank=True, null=True)
    permit_social_media_tagging = models.BooleanField(_("Permit Social Media Tagging"), default=False)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'social media'
        verbose_name = _('social media')
        verbose_name_plural = _('social medias')
        
        
    def __str__(self):
        return f"Social Media Profiles for ID {self.user.first_name}"        


class BankAccount(models.Model):
    user = models.ForeignKey(Users, on_delete=models.DO_NOTHING, null=True)
    pan_card = models.FileField(upload_to='bank_documents/', blank=True, null=True)
    aadhar_card = models.FileField(upload_to='bank_documents/', blank=True, null=True)
    account_holder_name = models.CharField(_("Account Holder's Name"), max_length=255)
    bank_name = models.CharField(_("Bank Name"), max_length=255)
    account_number = models.CharField(_("Account Number"), max_length=125)
    ifsc_code = models.CharField(_("IFSC Code"), max_length=125)
    branch = models.CharField(_("Branch"), max_length=255)
    city = models.CharField(_("City"), max_length=255)
    bank_statement_or_cheque = models.FileField(upload_to='bank_documents/', blank=True, null=True)
    account_type = models.CharField(_("Account Type"), max_length=125)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bank detail'
        verbose_name = _('bank detail')
        verbose_name_plural = _('bank details')
        
    def __str__(self):
        return f"Bank Details for {self.account_holder_name}"


class Consultant(models.Model):
    candidate = models.ForeignKey("candidate.Candidate", on_delete=models.CASCADE, limit_choices_to={'status': '17'}, related_name='consultant')    
    social_media = models.ForeignKey(SocialMedia, on_delete=models.CASCADE)
    bank_details = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    alt_contact_person_name = models.CharField(_("Alternative Contact Person's Name"), max_length=255, blank=True, null=True)
    alt_contact_person_number = models.CharField(_("Alternative Contact Person's Phone"), max_length=125, blank=True, null=True)
    alt_contact_person_relation = models.CharField(_("Relation with Alternative Contact Person"), max_length=255, blank=True, null=True)    
    number_of_projects = models.IntegerField()
    number_of_current_projects = models.IntegerField(validators=[MaxValueValidator(3)]) # maximum current project should not be greater than 3
    
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultant'
        verbose_name = _('consultant')
        verbose_name_plural = _('consultants')
        
    def __str__(self):
        return f"Consultant {self.candidate.first_name}"


class ConsultantContract(models.Model):
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    job = models.ForeignKey("employer.Job", on_delete=models.CASCADE)
    contract_type = models.CharField(_('Domain'),choices=CONTRACT_TYPES,max_length=255)
    notice_period = models.IntegerField(_("Notice Period (in days)"))
    created_date = models.DateField(_("Contract Date"), default=date.today)
    signed_date = models.DateField()
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    food_allowance = models.IntegerField(_("Food Allowance"), default=0)
    travel_allowance = models.IntegerField(_("Travel Allowance"), default=0)
    phone_allowance = models.IntegerField(_("Phone Allowance"), default=0)
    other_allowance = models.IntegerField(_("Other Allowance"), default=0)
    status = models.CharField(_('Status'),choices=CONTRACT_STATUS,max_length=125)
    pdf_link = models.URLField(_("Link to Signed PDF"), blank=True, null=True)
    digi_sign_link = models.URLField(_("Digital Signature Link"), blank=True, null=True)    

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contracts'
        verbose_name = _('contract')
        verbose_name_plural = _('contracts')

    def __str__(self):
        return f'Contract for {self.consultant} on project {self.project}'
    
# ProjectRenewal
# renewal_count = models.IntegerField(_("Number of times renewed")) # ask aboli - where should we keep the renewal count