from django.db import models
from apps.admin_app.models import Domain
from apps.common.models import CustomRole, CustomSkill, Users
from core.model_choices import (CUSTUM_ROLES_SKILLS_STATUS,EMPLOYER_COMPANY_SIZE, EMPLOYER_SOURCE,EMPLOYER_STATUS, EMPLOYER_JOB_STATUS, EMPLOYER_TARGET_AUDIENCE, INTERVIEW_STATUS, JOB_DRAFT_STATUS, USER_TYPE_CHOICES, CANDIDATE_JOB_STATUS, FEEDBACK_STATUS)
# Create your models here.
from apps.candidate.models import Candidate

class Company(models.Model):
    name = models.CharField(max_length=150)
    website = models.URLField()
    logo = models.URLField(null=True)
    description = models.TextField()
    industry_type = models.ForeignKey(Domain,  on_delete=models.DO_NOTHING)
    size =  models.CharField(max_length=5, choices=EMPLOYER_COMPANY_SIZE)
    target_audience = models.CharField(max_length=5, choices=EMPLOYER_TARGET_AUDIENCE)
    source = models.CharField(max_length=5, choices=EMPLOYER_SOURCE)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return self.name

    class Meta:
        db_table = 'companies'


class Employer(models.Model):
    user = models.ForeignKey(Users, on_delete=models.DO_NOTHING, null=True)
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, null=True)
    status = models.CharField(max_length=5, choices=EMPLOYER_STATUS, default=EMPLOYER_STATUS[0][0])
    additional_info=models.JSONField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) :
        return str(self.user.email)
    
    class Meta:
        db_table = 'employers'


class Job(models.Model):
    employer=models.ForeignKey(Employer, on_delete=models.DO_NOTHING)
    status=models.CharField(max_length=5, blank=True, choices=EMPLOYER_JOB_STATUS,  default=EMPLOYER_JOB_STATUS[0][0])
    function = models.ForeignKey('admin_app.Function', on_delete=models.CASCADE)
    role = models.ForeignKey('admin_app.Role', on_delete=models.CASCADE, null=True, blank=True)
    skills = models.ManyToManyField('admin_app.Skill', related_name='job_skills')
    description = models.TextField()
    flexi_details = models.JSONField(default={})
    requirement_details = models.JSONField(default={})
    other_details = models.JSONField(default={})
    attachment = models.URLField(blank=True)
    details = models.JSONField(default={})
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'


class JobCustomRoleSkills(models.Model):
    job = models.ForeignKey(Job, on_delete=models.DO_NOTHING)
    role = models.ForeignKey(CustomRole, on_delete=models.DO_NOTHING ,null=True)
    skill = models.ManyToManyField(CustomSkill)
    status = models.CharField(max_length=5, choices=CUSTUM_ROLES_SKILLS_STATUS, default=CUSTUM_ROLES_SKILLS_STATUS[0][0])

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return f"{self.job}"
    
    class Meta:
        db_table = 'job_custom_role_skills'


class DraftJob(models.Model):
    employer=models.ForeignKey(Employer, on_delete=models.DO_NOTHING)
    status = models.CharField(choices=JOB_DRAFT_STATUS, default=JOB_DRAFT_STATUS[0][0], max_length=2)
    details = models.JSONField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'draft_jobs'

    
class RolesMinMaxPricing(models.Model):
    existing_role = models.ForeignKey('admin_app.Role', on_delete=models.CASCADE, null=True, blank=True)
    custom_role = models.ForeignKey(CustomRole, on_delete=models.DO_NOTHING, null=True, blank=True)
    min_salary = models.FloatField()
    max_salary = models.FloatField()
    currency   = models.CharField(max_length=5, blank= True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles_min_max_pricing'


class CandidateJobStatus(models.Model):

    job = models.ForeignKey(Job, on_delete=models.DO_NOTHING)
    candidate = models.ForeignKey(Candidate, on_delete=models.DO_NOTHING)
    status = models.PositiveSmallIntegerField(choices=CANDIDATE_JOB_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidate_job_status'

class CandidateJobNotes(models.Model):
    comments = models.TextField()
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidate_job_status_notes'

class SkippedCandidate(models.Model):
    job = models.ForeignKey(Job, on_delete=models.DO_NOTHING)
    candidate = models.ForeignKey(Candidate, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'job_skipped_candidates'

class InterviewSlot(models.Model):
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interview_slots'

class Interview(models.Model):
    candidate_job_status = models.ForeignKey(CandidateJobStatus, on_delete=models.CASCADE)
    status = models.CharField(choices=INTERVIEW_STATUS, max_length=3)
    slots = models.ManyToManyField(InterviewSlot)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'interviews'