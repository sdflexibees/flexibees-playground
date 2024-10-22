from asgiref.sync import async_to_sync
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.admin_app.models import AdminUser
from apps.candidate.models import Candidate
from apps.notifications.consumers import update_admin, get_notification_count, update_candidate, \
    get_candidate_notification_count
from core.model_choices import DEVICE_TYPES


class AdminNotification(models.Model):
    ITEM_TYPE_CHOICES = (
        ('project', 'project'),
        ('candidate', 'candidate'),
    )
    USER_TYPE_CHOICES = (
        ('bd', 'BD'),
        ('admin', 'Recruiter Admin'),
        ('recruiter', 'Recruiter'),
        ('sme', 'SME'),
        ('super_admin', 'Super Admin'),
        ('candidate', 'Candidate'),
    )
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, default='project')
    item_id = models.PositiveIntegerField()
    sent_by_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    sent_to_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    sent_by = models.ForeignKey('admin_app.AdminUser', on_delete=models.CASCADE, related_name='sent_by')
    sent_to = models.ForeignKey('admin_app.AdminUser', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('-id',)


@receiver(post_save, sender=AdminNotification)
def send_count(sender, instance, created, **kwargs):
    if created:
        filter = dict()
        if instance.sent_to:
            filter.update({'id': instance.sent_to.id})
        all_receivers = AdminUser.objects.filter(active=True, published=True, roles__contains=[instance.sent_to_type],
                                                 **filter)
        for each_receiver in all_receivers:
            data = get_notification_count(each_receiver, instance.sent_to_type)
            async_to_sync(update_admin)(data, instance.sent_to_type + str(each_receiver.id), 'new_count')


class CandidateNotification(models.Model):
    ITEM_TYPE_CHOICES = (
        ('project', 'project'),
        ('candidate', 'candidate'),
    )
    USER_TYPE_CHOICES = (
        ('bd', 'BD'),
        ('admin', 'Recruiter Admin'),
        ('recruiter', 'Recruiter'),
        ('sme', 'SME'),
        ('super_admin', 'Super Admin'),
        ('candidate', 'Candidate'),
    )
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, default='project')
    item_id = models.PositiveIntegerField()
    sent_to = models.ForeignKey('candidate.Candidate', on_delete=models.CASCADE, null=True, blank=True)
    all = models.BooleanField(default=False)
    message = models.TextField()

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('-id',)


@receiver(post_save, sender=CandidateNotification)
def send_count_to_app(sender, instance, created, **kwargs):
    if created:
        candidate_obj = Candidate.objects.filter(active=True, id=instance.sent_to.id)
        data = get_candidate_notification_count(candidate_obj[0])
        async_to_sync(update_candidate)(data, (str(candidate_obj[0].id)), "new_count")


class UserDevice(models.Model):
    """
    This model stores registration id or device id of users and
    also store type of device
    """
    user = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True)
    registration_id = models.CharField(max_length=200, blank=True)
    type = models.CharField(choices=DEVICE_TYPES, max_length=10)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name + ' - ' if self.user else ''}{self.type}"