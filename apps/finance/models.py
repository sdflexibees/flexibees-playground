from datetime import date
import os
from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.common.models import Users
from django.core.exceptions import ValidationError




COMPANY_SECTORS = (
    ('1',"Agriculture"),
    ('2',"Advertising & Marketing"),    
    ('3',"Analytics"),
    ('4',"Apparel & Fashion"),
    ('5',"Architecture & Planning"),
    ('6',"Automobile Industry"),
    ('7',"BPO / KPO / LPO"),
    ("8","Computer and Electronics Manufacturing"),
    ("9","Construction"),
    ("10","Consumer Discretionary /Luxury / Jewellery / Arts"),
    ('11',"E-commerce"),
    ('12',"EdTech / E-Learning"),    
    ('13',"Education"),
    ('14',"Environmental Services /Sustainability / Renewable energy"),
    ('15',"Event Management / Entertainment"),
    ('16',"Financial Services"),
    ('17',"FinTech"),
    ("18","FMCG / Food & Beverage"),
    ("19","Healthcare / Hospital management"),
    ("20","HealthTech"),
    ('1',"HR / Recruitments"),
    ('2',"Industrial Engineering / Automation"),    
    ('3',"Information Technology & Services"),
    ('4',"Logistics & Supply Chain"),
    ('5',"Management Consulting / Legal Services"),
    ('6',"Manufacturing / Materials"),
    ('7',"Non-profit"),
    ("8","Pharmaceuticals / Medical Related"),
    ("9","Property Management / Facility Service"),
    ("10","Publishing / Library / Book Shopss"),
    ('11',"Real Estate"),
    ('12',"Retail"),    
    ('13',"SAAS / PAAS"),
    ('14',"Security"),
    ('15',"Sports"),
    ('16',"Tech / IT Consulting"),
    ('17',"Telecommunication"),
    ("18","Travel / Tourism /Transport"),
    ("19","Utilities"),
    ("20","Venture Capital & Private Equity"),
    ("19","Wellness & Fitness"),
    ("20","Other")
)

COMPANY_SETUPS = (
    ('1',"Start - up"),
    ('2',"Small/Medium Enterprise"),    
    ('3',"Large Corporates"),
    ('4',"Others")
)

REGISTRATION_TYPES = (
    ('1',"Registered Business - Regular"),
    ('2',"Consumer"),    
    ('3',"Overseas"),
    ('4',"Registered Business - Composition"),
    ('5',"Special Economic Zone"),
    ('6',"SEZ Developer"),
    ('7',"Tax Deductor"),
    ("8","Other")
)

CONTRACT_STATUS = (
    ('1',"Draft"),
    ('2',"Published"),    
    ('3',"Pending Consultant Signature"),
    ('4',"Pending Client Signature"),
    ('5',"Signed"),
    ('6',"In Progress"),
    ('7',"Suspended"),
    ("8","Completed"),
    ("9","Pending Renewal"),
    ("10","Withdrawn")
)

CONSULTANT_CONTRACT_TYPES = (
    ('1',"External Consultant"),
    ('2',"Internal Consultant - BDM"),
    ('3',"Internal Consultant - Non BDM")
)
# @TODO - in future , this has to be fetched from job model as a foreign key
CLIENT_CONTRACT_TYPES = (
    ('1',"International"),
    ('2',"Domestic - Proprietorship"),
    ('3',"Domestic - Non Proprietorship"),
    ('4',"Placement - Full Time"),
    ('5',"Placement - Part Time"),
)
DIRECTOR_NAME_CHOICES = (
    ('1',"Shreya Prakash"),
    ('2',"Rashmi Rammohan"),
    ('3',"Deepa Narayanaswamy")
)


def validate_file_or_image(file):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Unsupported file extension. Allowed extensions are: .jpg, .jpeg, .png, .pdf")


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
        db_table = 'finance_social_media'
        verbose_name = _('social media')
        verbose_name_plural = _('social medias')
        
        
    def __str__(self):
        return f"Social Media Profiles for ID {self.user.first_name}"        


class BankAccount(models.Model):
    user = models.ForeignKey(Users, on_delete=models.DO_NOTHING, null=True)
    pan_card = models.FileField(upload_to='bank_documents/', blank=True, null=True, validators=[validate_file_or_image])
    aadhar_card = models.FileField(upload_to='bank_documents/', blank=True, null=True, validators=[validate_file_or_image])
    account_holder_name = models.CharField(_("Account Holder's Name"), max_length=255)
    pan_card_number = models.CharField(_("PAN Card Number"), max_length=125)
    bank_name = models.CharField(_("Bank Name"), max_length=255)
    account_number = models.CharField(_("Account Number"), max_length=125)
    ifsc_code = models.CharField(_("IFSC Code"), max_length=125)
    branch = models.CharField(_("Branch"), max_length=255)
    city = models.CharField(_("City"), max_length=255)
    bank_statement_or_cheque = models.FileField(upload_to='bank_documents/', blank=True, null=True, validators=[validate_file_or_image])
    account_type = models.CharField(_("Account Type"), max_length=125)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'finance_bank_account'
        verbose_name = _('bank account')
        verbose_name_plural = _('bank accounts')
        
    def __str__(self):
        return f"Bank Details of {self.user.first_name} {self.user.last_name}"
    
    
class Client(models.Model):
    employer = models.ForeignKey("employer.Employer", on_delete=models.CASCADE)
    social_media = models.ForeignKey("finance.SocialMedia", on_delete=models.CASCADE)
    legal_entity_name = models.CharField(_("Legal Entity Name"),max_length=255)
    brand_name = models.CharField(_("Brand Name (If any)"),max_length=255, blank=True, null=True)
    date_of_incorporation = models.DateField(_("Date of Incorporation"),blank=True, null=True)
    # address = models.TextField(_("Address"))
    city = models.CharField(_("City"),max_length=255)
    state = models.CharField(_("State"),max_length=255)
    zip_code = models.CharField(_("Zip Code"),max_length=10)
    # country = models.CharField(_("h. Country"),max_length=100)
    registered_under_gst_act = models.BooleanField(_("Whether Registered under GST Act 2017?"),default=False)
    type_of_registration = models.CharField(_("Type of Registration"),choices=REGISTRATION_TYPES,max_length=255,default='1')
    gstin = models.CharField(_("GSTIN"),max_length=50, blank=True, null=True)
    gst_certificate = models.FileField(upload_to='gst_certificates/', blank=True, null=True, validators=[validate_file_or_image])
    registered_under_msmed = models.BooleanField(_("Whether Registered under MSMED?"),default=False)
    msme_registration_number = models.CharField(_("MSME Registration Number"),max_length=50, blank=True, null=True)
    company_sector = models.CharField(_("Company Sector"),choices=COMPANY_SECTORS,max_length=255,default='1')
    company_setup = models.CharField(_("Company Setup"),choices=COMPANY_SETUPS,max_length=255,default='1')
    company_head_count = models.PositiveIntegerField(_("Company Head Count"))
    # website = models.URLField(_("Website/other source"),blank=True, null=True)
    # billing_currency = models.CharField(_("Billing Currency"),max_length=10)
    authorized_person_name = models.CharField(_("Name of authorized person for signing the contract"),max_length=255)
    authorized_person_designation = models.CharField(_("Designation of the authorized person"),max_length=255)
    authorized_person_email = models.EmailField(_("Mail id of the authorized person"))
    accounts_contact_person_name = models.CharField(_("Contact Person in Accounts/Finance Department"),max_length=255)
    accounts_contact_person_email = models.EmailField(_("Email Id of Accounts/Finance Person"))
    accounts_contact_person_phone = models.CharField(_("Phone no of Accounts/Finance Person"),max_length=20)
    send_hard_copy_invoice = models.BooleanField(_("Whether hard copy invoice to be sent for billing (by default we send soft copy only, but hard copy can be sent on request)"),default=False)
    # email = models.EmailField(_("Email"))
    pan_card = models.FileField(upload_to='bank_documents/', blank=True, null=True, validators=[validate_file_or_image])
    pan_card_number = models.CharField(_("PAN Card Number"), max_length=125)
    
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clients'
        verbose_name = 'client'
        verbose_name_plural = 'clients'

    def __str__(self):
        return f"{self.legal_entity_name} ({self.brand_name if self.brand_name else 'No Brand'})"
    
    

class Consultant(models.Model):
    user = models.ForeignKey(Users, on_delete=models.DO_NOTHING, null=True)  # @TODO fix later - candidate model refactoring
    candidate = models.ForeignKey("candidate.Candidate", on_delete=models.CASCADE, limit_choices_to={'status__in': ['17', '18', '19', '20', '21', '22', '23', '24', '25']}, related_name='consultant')  
    alt_contact_person_name = models.CharField(_("Alternative Contact Person's Name"), max_length=255, blank=True, null=True)
    alt_contact_person_number = models.CharField(_("Alternative Contact Person's Phone"), max_length=125, blank=True, null=True)
    alt_contact_person_relation = models.CharField(_("Relation with Alternative Contact Person"), max_length=255, blank=True, null=True) 
    number_of_current_projects = models.IntegerField(default=0,validators=[MaxValueValidator(3)]) # maximum current project should not be greater than 3
    
    created = models.DateTimeField(auto_now_add=True)  
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'finance_consultant'
        verbose_name = _('consultant')
        verbose_name_plural = _('consultants')
        
    def __str__(self):
        return f"Consultant {self.id} {self.candidate.first_name} {self.candidate.last_name}"


class Contract(models.Model):
    consultant = models.ForeignKey("finance.Consultant", on_delete=models.CASCADE)
    client = models.ForeignKey("finance.Client", on_delete=models.CASCADE)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, blank=True, null=True)
    pricing = models.ForeignKey("projects.Pricing", on_delete=models.CASCADE, blank=True, null=True)
    project_detail = models.ForeignKey("projects.OtherProjectDetail", on_delete=models.CASCADE, blank=True, null=True)
    job = models.ForeignKey("employer.Job", on_delete=models.CASCADE)
    consultant_contract_type = models.CharField(_('Consultant Contract Type'),choices=CONSULTANT_CONTRACT_TYPES,max_length=255,default='1')
    client_contract_type = models.CharField(_('Client Contract Type'),choices=CLIENT_CONTRACT_TYPES,max_length=255,default='1')
    notice_period = models.IntegerField(_("Notice Period (in days)"))
    signed_date = models.DateField(null=True, blank=True)
    # start_date = models.DateField(_("Start Date"))
    # end_date = models.DateField(_("End Date"))
    consultant_amount = models.IntegerField(_("Consultant Amount"))
    consultant_aggregate_amount = models.IntegerField(_("Consultant Aggregate Amount"))
    client_amount = models.IntegerField(_("Client Amount"))
    # food_allowance = models.IntegerField(_("Food Allowance"), default=0)
    # travel_allowance = models.IntegerField(_("Travel Allowance"), default=0)
    # phone_allowance = models.IntegerField(_("Phone Allowance"), default=0)
    # other_allowance = models.IntegerField(_("Other Allowance"), default=0)
    status = models.CharField(_('Status'),choices=CONTRACT_STATUS,max_length=125, default=1)
    pdf_link = models.URLField(_("Link to Signed PDF"), blank=True, null=True)
    digi_sign_link = models.URLField(_("Digital Signature Link"), blank=True, null=True) 
    signatory_image = models.ImageField(_("Signature"),upload_to='signatures/images/', null=True, blank=True)
    bdm_gross_margin_commission_percentage = models.IntegerField("BDM Gross Margin Percentage", null=True, blank=True)
    bdm_lifetime_commission_percentage = models.IntegerField("BDM Life Time Percentage", null=True, blank=True)
    director_name = models.CharField(_('Director'),choices=DIRECTOR_NAME_CHOICES,max_length=255,default='1')
    director_email = models.EmailField(_('Director email'))
    working_hours_per_day = models.IntegerField(_("Working hours per day"), default=8)
    working_days_in_a_week = models.IntegerField(_("Working days in a week"), default=5)
    paid_leaves = models.IntegerField(_("Number of paid leaves"), default=3)
    initial_fee_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Percentage of the consideration for the first installment (e.g., 70.00)",
        null=True, blank=True
    )
    second_fee_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Percentage of the consideration for the second installment (e.g., 30.00)",
        null=True, blank=True
    )
    initial_invoice_date = models.DateField(_("Date of the first installment invoice"), auto_now_add=True)
    second_invoice_date = models.DateField(_("Date of the first installment invoice"), auto_now_add=True)
    
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contracts'
        verbose_name = _('finance contract')
        verbose_name_plural = _('finance contracts')

    def __str__(self):
        return f'Contract {self.id} for {self.consultant} by {self.client} '
    
    # @property
    # def contract_duration(self):
    #     """
    #     Calculate the duration of the contract in days.
    #     """
    #     if self.end_date and self.start_date:
    #         duration_in_days = (self.end_date - self.start_date).days
    #         duration_in_months = round(duration_in_days / 30)  # Approximate to months
    #         return duration_in_months
    #     return None
    
    @property
    def total_working_hours(self):
        """
        Calculate the total working hours for the consultant in a month.
        
        If working_days_in_a_week is 5:
            total_hours = 4 * 22 days to 5 * 22 days (88 - 110 hours)
        If working_days_in_a_week is 6:
            total_hours = 4 * 26 days to 5 * 26 days (104 - 130 hours)
        
        Returns a string formatted as 'min_hours-max_hours'.
        """
        # Determine the number of working days in a month based on working days per week
        if self.working_days_in_a_week == 5:
            working_days_in_month = 22
        elif self.working_days_in_a_week == 6:
            working_days_in_month = 26
        else:
            # Handle unexpected cases
            return "Invalid working days in a week"

        # Calculate min and max hours based on 4 and 5 hours per day
        min_hours = 4 * working_days_in_month
        max_hours = 5 * working_days_in_month

        # Return as a formatted string
        return f"{min_hours}-{max_hours}"
    
    @property
    def initial_installment_amount(self):
        if self.initial_fee_percentage is not None and self.client_amount is not None:
            return (self.initial_fee_percentage / 100) * self.client_amount
        return 0  # or None, based on your requirements

    @property
    def second_installment_amount(self):
        if self.second_fee_percentage is not None and self.client_amount is not None:
            return (self.second_fee_percentage / 100) * self.client_amount
        return 0  # or None, based on your requirements

    

# ProjectRenewal
# renewal_count = models.IntegerField(_("Number of times renewed")) # ask aboli - where should we keep the renewal count

