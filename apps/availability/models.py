from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import F, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from core.model_choices import LIFESTYLE_RESPONSES_CHOICES


class ActivityCard(models.Model):
    PRIORITY_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    SESSION_CHOICES = (
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    )
    title = models.CharField(max_length=250)
    image = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True)
    admin_priority = models.JSONField(blank=True, default={'morning': 'low',
                                                           'afternoon': 'low',
                                                           'evening': 'low',
                                                           'night': 'low'})
    sessions = ArrayField(models.CharField(max_length=50, choices=SESSION_CHOICES))
    popularity_score = models.JSONField(blank=True, default={'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0})
    free_time = models.BooleanField(default=False)
    lifestyle_responses = ArrayField(models.CharField(max_length=50, blank=True, choices=LIFESTYLE_RESPONSES_CHOICES),
                                     blank=True, default=list)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id) + ' - ' + str(self.title)


class CandidateAvailability(models.Model):
    candidate = models.ForeignKey('candidate.Candidate', on_delete=models.CASCADE)
    activity_card = models.ForeignKey(ActivityCard, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    previous_activity = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True, related_name='prev')
    next_activity = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True, related_name='next')

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        # prev_activity = str(self.previous_activity.activity_card.title) if self.previous_activity else 'Wakeup'
        # next_activity = str(self.next_activity.activity_card.title) if self.next_activity else 'Last'
        return str(self.pk) + '-' + str(self.candidate.first_name) + '-' + self.activity_card.title


@receiver(post_save, sender=CandidateAvailability)
def update_free_time_and_popularity(sender, instance, created, **kwargs):
    duration = CandidateAvailability.objects.filter(candidate=instance.candidate, activity_card__free_time=True,
                                                    active=True).\
        annotate(duration=F('end_time')-F('start_time')).aggregate(total_free=Sum('duration'))['total_free']
    if duration:
        instance.candidate.total_available_hours = round(duration.seconds / 3600, 2)
    else:
        instance.candidate.total_available_hours = 0
    instance.candidate.timeline_last_updated = timezone.now()
    instance.last_notified = None
    instance.notification_count = 0
    instance.candidate.save()

#     if instance.previous_activity:
#         previous = CandidateAvailability.objects.get(id=instance.previous_activity.id, active=True)
#     else:
#         previous = CandidateAvailability.objects.get(candidate=instance.candidate.id, active=True, next_activity=None)
#     previous.next_activity_id = instance.pk
#     print(instance.pk, previous.next_activity_id)
#     previous.save()
#     instance.start_time = previous.end_time

