from django.contrib.auth.hashers import make_password, check_password
from django.contrib.postgres.fields import ArrayField
from django.db import models
from core.extra import make_title, make_lower
from core.model_choices import LIFESTYLE_RESPONSES_CHOICES, CANDIDATE_STATES, CANDIDATE_JOINING_STATUS
from core.validations import mobile_regex


class Candidate(models.Model):
    HEAR_ABOUT_FLEXIBEE_CHOICES = (
        ('others', 'Others'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('whatsapp', 'WhatsApp'),
        ('referral_scheme', 'Referral Scheme'),
        ('other_website_or_women_group', 'Other website or Women group'),
        ('google_search', 'Google search'),
        ('news_or_media', 'News or Media'),
        ('word_of_mouth', 'Word of mouth'),
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True)
    country_code = models.CharField(max_length=5, default='91')
    phone = models.CharField(max_length=15, validators=[mobile_regex], blank=True)
    password = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)
    profile_pic = models.URLField(null=True)
    will_to_travel_to_local_office = models.BooleanField(default=False)
    hear_about_flexibees = models.CharField(max_length=50, choices=HEAR_ABOUT_FLEXIBEE_CHOICES)
    hear_about_detailed = models.TextField(blank=True, null=True)
    brief_description = models.TextField(blank=True)
    profile_summary = models.TextField(blank=True)
    skills = models.ManyToManyField('admin_app.Skill', blank=True)
    roles = models.ManyToManyField('admin_app.Role', blank=True)
    total_year_of_experience = models.FloatField(default=0.0)
    relevant_experience = models.IntegerField(blank=True, null=True)
    relevantexp = models.JSONField(blank=True, default=dict)
    years_of_break = models.FloatField(default=0.0)
    hire = models.BooleanField(default=True)
    otp = models.TextField(null=True, blank=True)
    portfolio_link = models.URLField(null=True)
    address = models.TextField(blank=True, null=True)
    legacy_skills = models.TextField(blank=True)
    legacy_last_role = models.TextField(blank=True)
    legacy_prior_roles = models.TextField(blank=True)
    legacy_last_employer = models.TextField(blank=True)
    legacy_prior_employers = models.TextField(blank=True)
    active_projects = models.PositiveIntegerField(default=0)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    read_notifications = ArrayField(models.PositiveIntegerField(blank=True), blank=True, default=list)
    lifestyle_responses = ArrayField(models.CharField(max_length=50, blank=True, choices=LIFESTYLE_RESPONSES_CHOICES), blank=True, default=list)
    wakeup_time = models.TimeField(null=True, blank=True)
    total_available_hours = models.FloatField(default=0.0)
    timeline_completed = models.BooleanField(default=False)
    questionnaire_completed = models.BooleanField(default=False)
    timeline_last_updated = models.DateTimeField(null=True)
    mylife_last_updated = models.DateTimeField(null=True)
    profile_last_updated = models.DateTimeField(null=True)
    last_login = models.DateTimeField(null=True, blank=True)
    flexibees_selected = models.PositiveIntegerField(default=0)
    skills_resume=ArrayField(models.CharField(max_length=1000),blank=True,default=list)
    last_used_andriod_app_version = models.CharField(max_length=10, null=True, blank=True)
    last_used_ios_app_version = models.CharField(max_length=10, null=True, blank=True)
    notification_count = models.PositiveSmallIntegerField(default=0)
    last_notified = models.DateTimeField(null=True)
    previous_email = models.EmailField(blank=True)
    status = models.CharField(max_length=3 , choices=CANDIDATE_STATES , null=True)
    function = models.ForeignKey('admin_app.Function', on_delete=models.DO_NOTHING, null=True)
    joining_status = models.CharField(max_length= 3, choices= CANDIDATE_JOINING_STATUS, null= True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        make_title(self, ['first_name', 'last_name'])
        make_lower(self, ['email'])
        super(Candidate, self).save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    def set_otp(self, raw_password):
        self.otp = make_password(raw_password)
        self._otp = raw_password

    def check_otp(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self._otp = None
            self.save(update_fields=["otp"])
        return check_password(raw_password, self.otp, setter)

    def __str__(self):
        # return str(self.id) + ' - ' + str(self.email)
        return str(self.id)
    
    class Meta:
        app_label='candidate'
        db_table = 'candidate_candidate'


class Employmentdetail(models.Model):
    EMPLOYMENT_TYPE_CHOICES = (
        ('Full Time Employee', 'Full Time Employee'),
        ('Full Time Contractor', 'Full Time Contractor'),
        ('Part Time Employee', 'Part Time Employee'),
        ('Part Time Contractor', 'Part Time Contractor'),
        ('Consultant', 'Consultant'),
        ('Paid Internship', 'Paid Internship'),
        ('Unpaid Internship', 'Unpaid Internship'),
    )
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    role = models.ForeignKey('admin_app.Role', on_delete=models.CASCADE)
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE_CHOICES, default='Full Time Employee')
    company = models.CharField(max_length=200)
    currently_working = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    # industry_type = models.CharField(max_length=100)
    domains = models.ManyToManyField('admin_app.Domain')
    description = models.TextField()

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name
    class Meta:
        app_label='candidate'
        db_table = 'candidate_employmentdetail'


class Education(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    school_college = models.CharField(max_length=200)
    education = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    start_date = models.PositiveIntegerField()
    end_date = models.PositiveIntegerField()
    grade = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name
    
    class Meta:
        app_label='candidate'
        db_table = 'candidate_education'



class Functional(models.Model):
    STATUS_CHOICES = (
        (1, 'Functional interview scheduled'),
        (2, 'Functional interview cleared'),
        (3, 'Functional interview not cleared'),
        (4, 'Functional on hold'),
    )
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    no_of_notifications_on_my_typical_day = models.PositiveSmallIntegerField(default=0)
    last_notified = models.DateTimeField(blank=True, null=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name + ': ' + self.project.company_name
    
    class Meta:
        app_label='candidate'
        db_table = 'candidate_functional'


class FunctionalFeedback(models.Model):
    STATUS_CHOICES = (
        (2, 'Functional interview cleared'),
        (3, 'Functional interview not cleared'),
        (4, 'Functional on hold'),
    )
    functional = models.ForeignKey(Functional, on_delete=models.CASCADE, null=True)
    skills_feedback = models.JSONField()
    overall_score = models.IntegerField(default=0)
    recommendation = models.IntegerField(choices=STATUS_CHOICES, default=3)
    comments = models.TextField(blank=True)
    interview_summary = models.URLField(null=True)
    feedback_by = models.ForeignKey('admin_app.AdminUser', on_delete=models.CASCADE)
    feedback_by = models.ForeignKey('admin_app.AdminUser', on_delete=models.DO_NOTHING, null=True)
    attachment = models.URLField(null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.functional.candidate.first_name + ': ' + self.functional.project.company_name
    
    class Meta:
        app_label='candidate'
        db_table = 'candidate_functionalfeedback'


class Flexifit(models.Model):
    STATUS_CHOICES = (
        (1, 'Flexifit interview scheduled'),
        (2, 'Candidate selected'),
        (3, 'Candidate not selected'),
        (4, 'Flexifit on hold'),
    )
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name + ': ' + self.project.company_name
    
    class Meta:
        app_label='candidate'
        db_table = 'candidate_flexifit'


class FlexifitFeedback(models.Model):
    STATUS_CHOICES = (
        (2, 'Candidate selected'),
        (3, 'Candidate not selected'),
        (4, 'Flexifit on hold'),
    )
    flexifit = models.ForeignKey(Flexifit, on_delete=models.CASCADE)
    recommendation = models.IntegerField(choices=STATUS_CHOICES, default=3)
    comments = models.TextField(blank=True)
    interview_summary = models.URLField(null=True)
    feedback_by = models.ForeignKey('admin_app.AdminUser', on_delete=models.CASCADE)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.flexifit.candidate.first_name + ': ' + self.flexifit.project.company_name
    
    class Meta:
        app_label='candidate'
        db_table = 'candidate_flexifitfeedback'


class FinalSelection(models.Model):
    STATUS_CHOICES = (
        (1, 'Flexibees selected'),
        (2, 'Sent to BD manager'),
        (3, 'Client selected'),
        (4, 'Client rejected'),
        (5, 'Partial selected'),
        (6, 'Selected'),
    )
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    send_to_bdmanager=models.DateTimeField(null=True,blank=True)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)
    flexifit_feedback = models.ForeignKey(FlexifitFeedback, on_delete=models.CASCADE)
    recruiter_comments = models.TextField()
    final_notification_sent = models.PositiveSmallIntegerField(default=0)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name + ': ' + self.project.company_name
    
    class Meta:
        app_label='candidate'
        db_table = 'candidate_finalselection'


class ClientFeedback(models.Model):
    STATUS_CHOICES = (
        (3, 'Client selected'),
        (4, 'Client rejected'),
        (5, 'Partial selected'),
    )
    final_selection = models.ForeignKey(FinalSelection, on_delete=models.CASCADE, null=True)
    job_interview = models.ForeignKey('employer.Interview', on_delete=models.CASCADE, null=True)
    recommendation = models.IntegerField(choices=STATUS_CHOICES, default=4)
    comments = models.TextField(blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True)
    attachment = models.URLField(null=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label='candidate'
        db_table = 'candidate_clientfeedback'