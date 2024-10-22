from django.db import models
from apps.admin_app.models import Role, Skill
from core.model_choices import CUSTUM_ROLES_SKILLS_STATUS, USER_TYPE_CHOICES
from core.extra import make_title, make_lower
from django.contrib.auth.hashers import make_password, check_password
# Create your models here.


# Employer Models
class UserType(models.Model):
    type_name = models.CharField(max_length=50)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type_name
    
    class Meta:
        db_table = 'types'


class Users(models.Model):
    first_name = models.CharField(max_length=50)
    type = models.ForeignKey(UserType, on_delete=models.DO_NOTHING)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    user_type = models.CharField(max_length=2,choices=USER_TYPE_CHOICES, default=USER_TYPE_CHOICES[0][0])
    profile_image = models.URLField(null=True)
    country_code = models.CharField(max_length=5, default="91")
    mobile = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=200, blank=True, null=True)
    password =  models.TextField()
    otp = models.TextField(null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    address = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        make_title(self, ['first_name', 'last_name'])
        make_lower(self, ['email'])
        super(Users, self).save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_otp(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self._otp = None
            self.save(update_fields=["otp", "password"])
        return check_password(raw_password, self.otp, setter)

    class Meta:
        db_table = 'user_infos'

class RoleMapping(models.Model):
    function = models.ForeignKey("admin_app.Function", on_delete=models.DO_NOTHING)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING)
    priority = models.PositiveSmallIntegerField(default= 0 )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return self.role.tag_name
    
    class Meta:
        db_table = 'roles_mappings'


class SkillMapping(models.Model):
    role_mapping = models.ForeignKey(RoleMapping, on_delete=models.DO_NOTHING)
    skill = models.ForeignKey(Skill, on_delete=models.DO_NOTHING)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return self.skill.tag_name
    
    class Meta:
        db_table = 'skills_mappings'

class CustomRole(models.Model):

    function = models.ForeignKey("admin_app.Function", on_delete=models.DO_NOTHING)
    role_name = models.CharField(max_length=50 ,)
    status = models.CharField(max_length=5, choices=CUSTUM_ROLES_SKILLS_STATUS, default=CUSTUM_ROLES_SKILLS_STATUS[0][0])
    action_date=models.DateTimeField(null=True)
    created_by = models.ForeignKey('employer.employer',on_delete=models.DO_NOTHING)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return self.role_name
    
    class Meta:
        indexes = [
            models.Index(fields=['role_name'], name='idx_custom_role_names'),
            ]
        db_table = 'custom_role_mappings'


class CustomSkill(models.Model):
    skill_name = models.CharField(max_length=150)
    status = models.CharField(max_length=5, choices=CUSTUM_ROLES_SKILLS_STATUS, default=CUSTUM_ROLES_SKILLS_STATUS[0][0])
    action_date=models.DateTimeField(null=True)
    created_by = models.ForeignKey('employer.employer', on_delete=models.DO_NOTHING)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self) : 
        return self.skill_name   
    
    class Meta:
        indexes = [
            models.Index(fields=['skill_name'], name='idx_custom_skill_names'),
            ]
        db_table = 'custom_skill_mappings'