from django.contrib.auth.hashers import make_password, check_password
from django.contrib.postgres.fields import ArrayField
from django.db import models

from core.extra import make_title, make_lower, upload_image
from core.model_choices import ADMIN_LEVEL_CHOICES
from core.validations import mobile_regex


class Function(models.Model):
    tag_name = models.CharField(max_length=50, unique=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag_name


class Skill(models.Model):
    function = models.ForeignKey(Function, on_delete=models.CASCADE)
    tag_name = models.CharField(max_length=150, unique=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag_name

    class Meta:
        ordering = ('tag_name',)


class Domain(models.Model):
    tag_name = models.CharField(max_length=50, unique=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag_name

    class Meta:
        ordering = ('tag_name',)


class Role(models.Model):
    tag_name = models.CharField(max_length=50, unique=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag_name

    class Meta:
        ordering = ('tag_name',)


class AdminUser(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.TextField()
    country_code = models.CharField(max_length=5, default='91')
    profile_pic = models.URLField(null=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=15, validators=[mobile_regex])
    level = models.PositiveIntegerField(choices=ADMIN_LEVEL_CHOICES)
    skills = models.ManyToManyField(Skill, blank=True)
    functions = models.ManyToManyField(Function, blank=True)
    roles = ArrayField(models.CharField(max_length=11))
    last_login = models.DateTimeField(null=True, blank=True)
    published = models.BooleanField(default=True)
    read_notifications = ArrayField(models.PositiveIntegerField(blank=True), blank=True, default=list)
    active_projects = models.PositiveIntegerField(default=0)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def save(self, *args, **kwargs):
        make_title(self, ['first_name', 'last_name'])
        make_lower(self, ['email'])
        super(AdminUser, self).save(*args, **kwargs)


class Tags(models.Model):
    name = models.CharField(max_length=50, unique=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        super(Tags, self).save(*args, **kwargs)

    class Meta:
        ordering = ('name',)


class Dropdown(models.Model):
    key_name = models.CharField(max_length=100)
    title = models.TextField(blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key_name

    class Meta:
        ordering = ('title',)


class Configuration(models.Model):
    title = models.CharField(max_length=50, unique=True)
    tags = models.ManyToManyField(Tags)
    dropdown = models.ForeignKey(Dropdown, null=True, blank=True, on_delete=models.CASCADE)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Token(models.Model):
    uid = models.CharField(unique=True, max_length=10)
    token = models.CharField(max_length=32)
    status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified = models.DateTimeField(auto_now_add=False, auto_now=True)


class ZOHOToken(models.Model):
    access_token = models.TextField()
    refresh_token = models.TextField()

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-id',)


class Language(models.Model):
    name = models.CharField(max_length=100)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)


class AppVersion(models.Model):
    android = models.CharField(max_length=10)
    ios = models.CharField(max_length=10)
    force_update = models.BooleanField(default=False)
    recommended_update = models.BooleanField(default=False)
    under_maintenance = models.BooleanField(default=False)
    android_release_note = models.CharField(max_length=250, null=True, blank=True)
    ios_release_note = models.CharField(max_length=250, null=True, blank=True)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.android + ' - ' + self.ios

class Country(models.Model):
    name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='index_country_name'),
        ]

    def __str__(self):
        return self.name 


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='index_city_name'),
        ]

    def __str__(self):
        return self.name 