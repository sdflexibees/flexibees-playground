from django.contrib.postgres.fields.jsonb import JSONField as JSONBField
from django.db import models


PAYOUT_CHOICES = (
        ('hourly', 'hourly'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
        ('yearly', 'yearly'),
    )


class Project(models.Model):
    STATUS_CHOICES = (
        (1, 'Project Proposal'),
        (2, 'Project Details Updated'),
        (3, 'Candidate Salary Requested'),
        (4, 'Candidate Salary Proposed'),
        (5, 'Project Pricing to Client Updated'),
        (6, 'Project Details Updated'),
        (7, 'New'),
        (8, 'In Progress'),
        (9, 'Closed'),
        (10, 'Re-opened'),
        (11, 'Suspended'),
        (12, 'Final client pricing sent/received'),
    )
    FORM_TYPE_CHOICES = (
        ('general', 'general'),
        ('sales', 'sales'),
        ('content', 'content'),
    )
    NOTIFY_STATUS_CHOICES = (
        (1, 'Notification pending'),
        (2, 'Notified'),
    )
    deal_name = models.CharField(max_length=200)
    zoho_id = models.CharField(max_length=100)
    bd_email = models.EmailField()
    bd = models.ForeignKey('admin_app.AdminUser', null=True, blank=True, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    function = models.ForeignKey('admin_app.Function', on_delete=models.CASCADE)
    role = models.ForeignKey('admin_app.Role', on_delete=models.CASCADE, null=True, blank=True)
    role_type = models.CharField(max_length=120, blank=True)
    model_type = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    flex_details = models.CharField(max_length=60)
    stage = models.CharField(max_length=30)
    status_description = models.TextField(blank=True)
    next_step = models.TextField(blank=True)
    post_status = models.CharField(max_length=60, blank=True)
    project_created = models.BooleanField(default=False)
    form_type = models.CharField(max_length=10, choices=FORM_TYPE_CHOICES, default='general')
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)
    recruiter = models.ForeignKey('admin_app.AdminUser', null=True, blank=True, on_delete=models.CASCADE,
                                    related_name='recruiter')
    flexibees_selected = models.PositiveIntegerField(default=0)
    client_selected = models.PositiveIntegerField(default=0)
    request_date = models.DateTimeField(null=True, blank=True)
    launch_date = models.DateField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    suspended_on = models.DateTimeField(null=True, blank=True)
    send_to_bdmanager=models.DateTimeField(null=True,blank=True)
    date_sent_to_recruitment = models.DateTimeField(null=True,blank=True)
    previous_recruiter = models.ForeignKey('admin_app.AdminUser', null=True, blank=True, on_delete=models.CASCADE,
                                            related_name='previous_recruiter')
    notify_status = models.IntegerField(default=1, choices=NOTIFY_STATUS_CHOICES)
    recruitment_days = models.PositiveIntegerField(default=0)
    date_assigned_to_recruiter = models.DateTimeField(null=True,blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        ordering = ('-modified', '-id',)


class Requirement(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    no_of_positions = models.PositiveIntegerField(default=1)
    detailed_job_description = models.TextField(blank=True)
    min_total_experience_needed = models.IntegerField(null=True, default=0)
    max_total_experience_needed = models.IntegerField(null=True, default=0)
    min_relevant_experience = models.IntegerField(null=True, default=0)
    max_relevant_experience = models.IntegerField(null=True, default=0)
    educational_constraints = models.BooleanField(default=False)
    education = models.CharField(max_length=100, blank=True)
    must_have_skills = models.ManyToManyField('admin_app.Skill', related_name='must_have_skills')
    nice_to_have_skills = models.ManyToManyField('admin_app.Skill', blank=True)
    must_have_domains = models.ManyToManyField('admin_app.Domain', related_name='must_have_domains', blank=True)
    nice_to_have_domain = models.ManyToManyField('admin_app.Domain', blank=True)

    # Sales
    sale_type = models.CharField(max_length=100, blank=True)
    describe_more = models.TextField(blank=True)
    lead_generation_requirement = models.CharField(max_length=100, blank=True)
    own_contact_required = models.CharField(max_length=50, blank=True, default='No')
    if_yes = models.CharField(max_length=100, blank=True)
    lead_expresses_interest = models.TextField(blank=True)
    language = JSONBField(default=list, null=True,blank=True)
    communication_skill_level = models.CharField(max_length=50, blank=True)

    # Content writer
    goals = models.TextField(blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    quantum_min = models.PositiveIntegerField(blank=True, null=True)
    quantum_max = models.PositiveIntegerField(blank=True, null=True)
    quantum_unit = models.CharField(max_length=20, blank=True)
    word_min = models.PositiveIntegerField(blank=True, null=True)
    word_max = models.PositiveIntegerField(blank=True, null=True)
    word_unit = models.CharField(max_length=20, blank=True)
    sample_work = models.CharField(max_length=20, blank=True)
    sample_work_detail = models.CharField(max_length=200, blank=True)
    budget = models.PositiveIntegerField(blank=True, null=True)
    content_duration_min = models.PositiveIntegerField(blank=True, null=True)
    content_duration_max = models.PositiveIntegerField(blank=True, null=True)
    content_duration_unit = models.CharField(max_length=100, blank=True, null=True)

    target_audience = models.CharField(max_length=20, blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project.company_name


class FlexiDetails(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    location_constraints = models.BooleanField(default=False)
    selected_city = models.CharField(max_length=100, blank=True)
    selected_country = models.CharField(max_length=100, blank=True)
    is_travel_required = models.BooleanField(default=False)
    how_often_travelling = models.CharField(max_length=100, blank=True)
    company_address = models.TextField(blank=True)
    min_no_of_working_hours = models.IntegerField(null=True, default=4)
    max_no_of_working_hours = models.IntegerField(null=True, default=5)
    working_hours_duration_unit = models.CharField(max_length=10, default='days', blank=True)
    type_of_payout = models.CharField(max_length=100)
    project_duration = models.IntegerField(null=True)
    project_duration_unit = models.CharField(max_length=10, blank=True)
    turn_around_time = models.IntegerField(null=True, default=2)
    turn_around_duration_unit = models.CharField(max_length=10, blank=True, default='weeks')
    client_assignment = models.BooleanField(default=False)
    assignment_file = models.URLField(null=True)
    assignment_duration = models.FloatField(null=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class OtherProjectDetail(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    compensation_from_client = models.CharField(max_length=100, blank=True)
    travel_expense_reimbursement = models.CharField(max_length=100, blank=True)
    phone_reimbursement = models.CharField(max_length=100, blank=True)
    other_comments = models.TextField(blank=True)
    client_variable = models.CharField(max_length=100, blank=True)
    compensation_structure = models.CharField(max_length=100, blank=True)
    when_make_it_known = models.CharField(max_length=100, blank=True)
    existing_team = models.CharField(max_length=100, blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class ClientDetail(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    company_website = models.URLField(blank=True, null=True)
    company_brief = models.TextField()
    currency = models.CharField(max_length=10, default='INR')
    is_interview_required =models.BooleanField(blank=True, null=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Pricing(models.Model):
    STAGE_CHOICES = (
        (1, 'Proposed candidate salary'),
        (2, 'Propose project pricing to Client'),
        (3, 'Final client pricing'),
        (4, 'Final candidate salary'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    stage = models.IntegerField(default=1, choices=STAGE_CHOICES)
    type_of_payout = models.CharField(max_length=100)
    min_salary = models.PositiveIntegerField(null=True)
    max_salary = models.PositiveIntegerField(null=True)
    project_duration_unit = models.CharField(max_length=10)
    comments = models.TextField(blank=True)
    added_by = models.ForeignKey('admin_app.AdminUser', on_delete=models.CASCADE)
    project_duration = models.IntegerField(null=True)
    currency = models.CharField(max_length=10, default='INR')

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Suspended(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reason = models.TextField()
    description = models.TextField(blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Closed(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reason = models.TextField(blank=True)
    comments = models.TextField(blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Reopen(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reason = models.TextField()
    comments = models.TextField(blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
