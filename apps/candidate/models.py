from dateutil import relativedelta as rdelta
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields.jsonb import JSONField as JSONBField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

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


class EmploymentDetail(models.Model):
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


@receiver(post_save, sender=EmploymentDetail)
def update_experiences(sender, instance, created, **kwargs):
    user_total_experiences = EmploymentDetail.objects.filter(candidate=instance.candidate, active=True)
    exp_list = []
    total_exp = rdelta.relativedelta(years=0, months=0)
    years_of_break = rdelta.relativedelta(years=0, months=0)
    for each_exp in user_total_experiences:
        start = each_exp.start_date
        end = timezone.now().date() if each_exp.currently_working else each_exp.end_date
        exp_list.append({
            'start': start,
            'end': end,
            'role': 'r' + str(each_exp.role.id),
        })
    newlist = sorted(exp_list, key=lambda k: k['start'])
    final_dict = {'total': []}
    for each_item in newlist:
        if each_item['role'] not in final_dict:
            final_dict[each_item['role']] = [[each_item['start'], each_item['end']]]
        else:
            last_role_range = final_dict[each_item['role']][-1]
            if each_item['start'] > last_role_range[1]:
                final_dict[each_item['role']].append([each_item['start'], each_item['end']])
            else:
                if each_item['start'] <= last_role_range[0]:
                    last_role_range[0] = each_item['start']
                if each_item['end'] >= last_role_range[1]:
                    last_role_range[1] = each_item['end']
                final_dict[each_item['role']][-1] = last_role_range
        if len(final_dict['total']) == 0:
            final_dict['total'].append([each_item['start'], each_item['end']])
        else:
            last_exp_range = final_dict['total'][-1]
            if each_item['start'] > last_exp_range[1]:
                final_dict['total'].append([each_item['start'], each_item['end']])
            else:
                if each_item['start'] <= last_exp_range[0]:
                    last_exp_range[0] = each_item['start']
                if each_item['end'] >= last_exp_range[1]:
                    last_exp_range[1] = each_item['end']
                final_dict['total'][-1] = last_exp_range
    for a in range(len(final_dict['total'])):
        exp = rdelta.relativedelta(final_dict['total'][a][1], final_dict['total'][a][0])
        total_exp += exp
        try:
            years_of_break += rdelta.relativedelta(final_dict['total'][a + 1][0], final_dict['total'][a][1])
        except:
            pass
    final_dict.pop('total')
    for b, value in final_dict.items():
        each_role_exp = rdelta.relativedelta(years=0, months=0)
        for each in value:
            each_role_exp += rdelta.relativedelta(each[1], each[0])
        final_dict[b] = round(float('{0.years}.{0.months}'.format(each_role_exp)), 2)
    instance.candidate.total_year_of_experience = round(float('{0.years}.{0.months}'.format(total_exp)), 2)
    instance.candidate.years_of_break = round(float('{0.years}.{0.months}'.format(years_of_break)), 2)
    instance.candidate.relevantexp = final_dict
    roles = list(EmploymentDetail.objects.filter(active=True, candidate=instance.candidate).
                    values_list('role__id', flat=True).
                    distinct('role__id'))
    instance.candidate.roles.set(roles)
    instance.candidate.profile_last_updated = timezone.now()
    instance.candidate.save()


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


class Certification(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    issued_by = models.CharField(max_length=200)
    issue_date = models.PositiveIntegerField()

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name


class CandidateLanguage(models.Model):
    PROFICIENCY_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    )
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    language = models.ForeignKey('admin_app.Language', on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='Beginner')
    read = models.BooleanField(default=False)
    write = models.BooleanField(default=False)
    speak = models.BooleanField(default=False)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name


class CandidateAttachment(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    attachment = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name


class Shortlist(models.Model):
    STATUS_CHOICES = (
        (1, 'Notification not sent'),
        (2, 'Notification sent/Waiting for response'),
    )
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name + ': ' + self.project.company_name


class InterestCheckAndSelfEvaluation(models.Model):
    STATUS_CHOICES = (
        (1, 'Interested, Self evaluation not done'),
        (2, 'Interested, Self evaluation done'),
        (3, 'Not interested'),
    )
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name + ': ' + self.project.company_name


class Assignment(models.Model):
    STATUS_CHOICES = (
        (1, 'Assignment not submitted'),
        (2, 'Assignment submitted'),
        (3, 'Assignment not cleared'),
        (4, 'Assignment cleared'),
        (5, 'Assignment on hold'),
        (6, 'No assignment'),
    )
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)
    submitted_assignment = models.URLField(null=True)
    submitted_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate.first_name + ': ' + self.project.company_name


class AssignmentFeedback(models.Model):
    STATUS_CHOICES = (
        (3, 'Assignment not cleared'),
        (4, 'Assignment cleared'),
        (5, 'Assignment on hold'),
    )
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    recommendation = models.IntegerField(choices=STATUS_CHOICES, default=3)
    comments = models.TextField(blank=True)
    feedback_by = models.ForeignKey('admin_app.AdminUser', on_delete=models.CASCADE)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.assignment.candidate.first_name + ': ' + self.assignment.project.company_name


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


class FunctionalFeedback(models.Model):
    STATUS_CHOICES = (
        (2, 'Functional interview cleared'),
        (3, 'Functional interview not cleared'),
        (4, 'Functional on hold'),
    )
    functional = models.ForeignKey(Functional, on_delete=models.CASCADE)
    skills_feedback = JSONBField(default=list)
    overall_score = models.IntegerField(default=0)
    recommendation = models.IntegerField(choices=STATUS_CHOICES, default=3)
    comments = models.TextField(blank=True)
    interview_summary = models.URLField(null=True)
    feedback_by = models.ForeignKey('admin_app.AdminUser', on_delete=models.CASCADE)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.functional.candidate.first_name + ': ' + self.functional.project.company_name


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


@receiver(post_save, sender=FinalSelection)
def update_flexibees_count(sender, instance, created, **kwargs):
    if created:
        instance.project.flexibees_selected += 1
    if instance.status == 3:
        instance.project.client_selected += 1
    instance.project.save()


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
    feedback_by = models.ForeignKey('admin_app.AdminUser', on_delete=models.CASCADE, null=True)
    attachment = models.URLField(null=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class SelfAssessment(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    skills = JSONBField(default=list)
    comments = models.TextField(blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class WebUser(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    country_code = models.CharField(max_length=5, default='91')
    phone = models.CharField(max_length=15, validators=[mobile_regex])
    converted = models.BooleanField(default=False)
    converted_date = models.DateTimeField(null=True, blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name

class EmailChange(models.Model):
    email = models.EmailField()
    previous_email = models.EmailField()
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    otp = models.TextField(blank=True)
    verified = models.BooleanField(blank=True, null=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def check_otp(self, raw_password):
        def setter(raw_password):
            self._otp = None
            self.save(update_fields=["otp"])
        return check_password(raw_password, self.otp, setter)
