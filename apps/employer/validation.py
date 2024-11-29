from apps.employer.validators import BaseValidator, CharField, URLField, IntegerField, ListField
from core.model_choices import CANDIDATE_JOB_STATUS, EMPLOYER_COMPANY_SIZE, EMPLOYER_SOURCE, EMPLOYER_TARGET_AUDIENCE


class JobListFilterValidator(BaseValidator):
    def __init__(self):
        super().__init__()
        self.add_field('status', CharField(required=False))
        self.add_field('statusus', ListField(required=False, allow_empty=False))
        self.add_field('search', CharField(required=False, allow_blank=True))