from django.contrib import admin
from .models import(CandidateJobNotes, CandidateJobStatus, Company, Employer, InterviewSlot, JobCustomRoleSkills, Job, Interview,
                    DraftJob, RolesMinMaxPricing, SkippedCandidate)

# Register your models here.
admin.site.register(Employer)
admin.site.register(Company)
admin.site.register(JobCustomRoleSkills)
admin.site.register(DraftJob)
admin.site.register(Job)
admin.site.register(RolesMinMaxPricing)
admin.site.register(CandidateJobNotes)
admin.site.register(CandidateJobStatus)
admin.site.register(Interview)
admin.site.register(SkippedCandidate)
admin.site.register(InterviewSlot)
