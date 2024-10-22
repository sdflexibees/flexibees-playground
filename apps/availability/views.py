import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from weasyprint import HTML
from django.db.models.expressions import RawSQL, Case, When, F

from apps.availability.models import ActivityCard, CandidateAvailability
from apps.availability.serializers import ActivityCardSerializer, CandidateTimelineSerializer, \
    CandidateTimelinePDFSerializer, TimelineSerializer, AddTimelineSerializerSwagger, ActivityCardListSerializer, \
    ActivityCardListingSerializer, EditTimelineSerializerSwagger, TimelineDetailSerializer, SearchActivityCardSerializer
from apps.candidate.all_candidate import check_candidate_profile
from apps.candidate.models import Candidate
from apps.candidate.swagger_serializers import ActivityListSerializer, WakeupTimeSerializer, \
    UpdateTimelineStatusSerializer
from core.api_permissions import AdminAuthentication, AppUserAuthentication, AppVersionPermission
from core.model_choices import LIFESTYLE_QUESTION_CHOICES, LIFESTYLE_RESPONSES_CHOICES
from core.pagination import paginate

from core.response_format import message_response
from core.response_messages import activity_card_exists, updated, object_does_not_exist, no_wakeup_time, \
    timeline_overlap, mandatory_fields_missing, deleted, same_start_end, invalid_input, notification_to_recruiter

# Create your views here.
from core.validations import check_invalid
from flexibees_candidate.settings import CHARACTER_LIMIT_60, CHARACTER_LIMIT_120
from apps.candidate.models import Functional
from apps.notifications.views import notify_admin
from flexibees_candidate.settings import ITEM_TYPE_CANDIDATE, SENT_TO_TYPE_RECRUITER, SUPER_ADMIN_ROLE, SUPER_ADMIN_EMAIL
from apps.admin_app.models import AdminUser
from core.helper_functions import min_hours_filled_in_my_typical_day
from apps.admin_app.views import api_logging


def get_timeline(candidate_id):
    try:
        wakeup_activity = CandidateAvailability.objects.get(candidate=candidate_id, previous_activity=None, active=True)
        timeline = [wakeup_activity]
    except ObjectDoesNotExist:
        return []
    next_activity = wakeup_activity.next_activity
    while next_activity:
        if timeline[-1].activity_card.id == next_activity.activity_card.id:
            timeline[-1].end_time = next_activity.end_time
        else:
            timeline.append(next_activity)
        next_activity = next_activity.next_activity
    return timeline


#Sorting functions for Lifestyle questions
def get_question_key(answer_choice): 
    # return : question_key
    return answer_choice.split('_')[0]

# Get Candidates mylife questions and answer list
def get_question_answer(candidate_obj):
    candidate_answer_choice_list = candidate_obj.lifestyle_responses 
    question_answer_list = []
    
    # remove None values from candidate answer choice list
    if None in candidate_answer_choice_list:
        candidate_answer_choice_list = list(filter(lambda item: item is not None, candidate_answer_choice_list))

    # Sorting candidate answer choice in ascending order(based on questions)
    candidate_answer_choice_list.sort(key=get_question_key)

    # Converting tuple of tuples (models choice) into dictionory 
    response_choice_dict = dict(LIFESTYLE_RESPONSES_CHOICES)
    for value in candidate_answer_choice_list:
        question_key = value.split('_')[0]
        if question_key in LIFESTYLE_QUESTION_CHOICES:
            question_answer_list.append({
                'question': LIFESTYLE_QUESTION_CHOICES[question_key],
                'answer': response_choice_dict[value]
                })
    return question_answer_list


def get_timeline_sequence(candidate_id, edit_activity_id=0):
    try:
        wakeup_activity = CandidateAvailability.objects.get(candidate=candidate_id, previous_activity=None,active=True)
        edit_index = 0
        final_edit_index = 0
        wakeup_data = {'id': wakeup_activity.id, 'activity_card': wakeup_activity.activity_card.id,
                       'start_time': wakeup_activity.start_time, 'end_time': wakeup_activity.end_time,
                       'previous_activity_id': wakeup_activity.previous_activity.id if wakeup_activity.previous_activity else None,
                       'next_activity_id': wakeup_activity.next_activity.id if wakeup_activity.next_activity else None}
        timeline = [wakeup_data]
        next_activity = wakeup_activity.next_activity
        while next_activity:
            edit_index += 1
            timeline.append({'id': next_activity.id, 'activity_card': next_activity.activity_card.id,
                             'start_time': next_activity.start_time, 'end_time': next_activity.end_time,
                             'previous_activity_id': next_activity.previous_activity.id if next_activity.previous_activity else None,
                             'next_activity_id': next_activity.next_activity.id if next_activity.next_activity else None})
            if edit_activity_id == next_activity.id:
                final_edit_index = edit_index
            next_activity = next_activity.next_activity
    except ObjectDoesNotExist:
        timeline = []
        final_edit_index = 0
    return timeline, final_edit_index


def adjust_timeline(timeline, last_end_time=None):
    day_end = datetime.datetime.strptime('23:59:59', '%H:%M:%S').time()
    day_start = datetime.datetime.strptime('00:00:00', '%H:%M:%S').time()
    for each_activity in timeline[:]:
        # if last_end_time != each_activity['start_time']:
        # print(each_activity)
        duration = datetime.timedelta(hours=each_activity['end_time'].hour,
                                      minutes=each_activity['end_time'].minute,
                                      seconds=each_activity['end_time'].second) -\
                   datetime.timedelta(hours=each_activity['start_time'].hour,
                                      minutes=each_activity['start_time'].minute,
                                      seconds=each_activity['start_time'].second)
        each_activity['start_time'] = last_end_time
        duration_adjusted_end = (datetime.datetime.combine(datetime.date(1, 2, 1),
                                                           each_activity['start_time']) + duration).time()
        if duration_adjusted_end.hour != 23 and duration_adjusted_end.minute == 59 and \
                duration_adjusted_end.second == 59:
            duration_adjusted_end = (datetime.datetime.combine(datetime.date(1, 2, 1), duration_adjusted_end) +
                                     datetime.timedelta(seconds=1)).time()
        each_activity['end_time'] = duration_adjusted_end
        if duration_adjusted_end.hour == 23 and duration_adjusted_end.minute == 59 and \
                duration_adjusted_end.second == 59:
            last_end_time = (datetime.datetime.combine(datetime.date(1, 2, 1), duration_adjusted_end) +
                             datetime.timedelta(seconds=1)).time()
        else:
            last_end_time = each_activity['end_time']
        if each_activity['start_time'] > each_activity['end_time']:
            split = check_and_split_activity(each_activity['activity_card'], each_activity['start_time'],
                                             each_activity['end_time'],
                                             each_activity['id'] if 'id' in each_activity else None)
            timeline[timeline.index(each_activity):timeline.index(each_activity)+1] = split
            last_end_time = split[1]['end_time']
    return timeline


def check_overlap(timeline, data):
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    for each_activity in timeline:
        if each_activity['start_time'] < end_time and each_activity['end_time'] > start_time:
            raise exceptions.ValidationError(message_response(timeline_overlap), 400)


def validate_timeline(timeline):
    for each_activity in range(len(timeline)):
        start_time = timeline[each_activity]['start_time']
        end_time = timeline[each_activity]['end_time']
        for check_activity in timeline[each_activity + 1:]:
            if check_activity['start_time'] < end_time and check_activity['end_time'] > start_time:
                raise exceptions.ValidationError(message_response(timeline_overlap), 400)


def check_and_split_activity(activity_id, start_time, end_time, availability_id=None):
    split_activities = []
    # if start_time > end_time:
    split_1 = {'id': availability_id, 'start_time': start_time,
               'end_time': datetime.datetime.strptime('23:59:59', '%H:%M:%S').time(),
               'activity_card': activity_id}
    split_1.pop('id') if availability_id is None else split_1
    split_2 = {'start_time': datetime.datetime.strptime('00:00:00', '%H:%M:%S').time(),
               'end_time': end_time,
               'activity_card': activity_id}
    split_activities.append(split_1)
    split_activities.append(split_2)
    return split_activities


def delete_extra_activities(deleted_ids):
    for deleted_item in deleted_ids:
        a = get_object_or_404(CandidateAvailability, id=deleted_item, active=True)
        deleted_previous = a.previous_activity
        deleted_next = a.next_activity
        if deleted_previous:
            deleted_previous.next_activity = None
            deleted_previous.save()
        if deleted_next:
            deleted_next.previous_activity = None
            deleted_next.save()
        a.previous_activity = None
        a.next_activity = None
        a.active = False
        a.save()


def save_activities(previous_activity, edited_timeline, new_activities=[], user=None, availability_id=0):
    first_after_new = True
    for each_activity in edited_timeline:
        if 'id' in each_activity:
            activity_query = get_object_or_404(CandidateAvailability, id=each_activity['id'], active=True)
            activity_query.activity_card_id = each_activity['activity_card']
            activity_query.start_time = each_activity['start_time']
            activity_query.end_time = each_activity['end_time']
            if each_activity['id'] == availability_id:
                if activity_query.next_activity:
                    activity_query.next_activity.previous_activity = None if len(
                        new_activities) != 0 else activity_query.next_activity.previous_activity
                    activity_query.next_activity.save()
                activity_query.next_activity = None if len(new_activities) != 0 else activity_query.next_activity
            else:
                # activity_query.previous_activity = previous_activity if first_after_new else activity_query.previous_activity
                activity_query.previous_activity = previous_activity
                if previous_activity:
                    previous_activity.next_activity = activity_query
                    previous_activity.save()
                # first_after_new = False
            activity_query.save()
        else:
            if previous_activity and previous_activity.next_activity:
                previous_activity.next_activity.previous_activity = None
                previous_activity.next_activity.save()
            activity_query = CandidateAvailability.objects.create(candidate=user,
                                                                  activity_card_id=each_activity['activity_card'],
                                                                  start_time=each_activity['start_time'],
                                                                  end_time=each_activity['end_time'],
                                                                  previous_activity=previous_activity)
            if previous_activity:
                previous_activity.next_activity = activity_query
                previous_activity.save()
        previous_activity = activity_query
    return True


def get_total_duration(wakeup_time, end_time):
    wakeup_time = datetime.timedelta(hours=wakeup_time.hour, minutes=wakeup_time.minute)
    end_time = datetime.timedelta(hours=end_time.hour, minutes=end_time.minute)
    return round((end_time - wakeup_time).seconds / 60, 2)


def reset_typical_day_detail(candidate_obj):
    """
        Reset The Typical Day Section.
    """
    try:
        candidate_obj.wakeup_time = None
        candidate_obj.timeline_last_updated = None
        candidate_obj.timeline_completed = False
        candidate_obj.total_available_hours = 0
        candidate_availability_objs = CandidateAvailability.objects.filter(active=True, candidate=candidate_obj.id)
        candidate_availability_objs.update(active=False)
        candidate_obj.save()
    except Exception:
        return False
    return True


class CandidateAvailabilityAPI(ModelViewSet):
    permission_classes = (AppUserAuthentication, AppVersionPermission,)

    @staticmethod
    @swagger_auto_schema(request_body=WakeupTimeSerializer)
    def update_wakeup_time(request):
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        reset_typical_day = request.data.get('reset_typical_day', 0)
        # Reseting the Typical Day of candidate based on Flag
        if reset_typical_day == 1:
            reset_status = reset_typical_day_detail(candidate_query)
            if not reset_status:
                return Response(message_response(invalid_input), 400)
        wakeup_time = datetime.datetime.strptime(request.data.get('wakeup_time'), '%H:%M').time()
        new_activities = request.data.get('new_activities', [])
        edited_last_end = wakeup_time
        for each_new in new_activities:
            each_new['start_time'] = edited_last_end
            each_new['end_time'] = datetime.datetime.strptime(each_new['end_time'], '%H:%M').time()
            edited_last_end = each_new['end_time']
        timeline, edit_index = get_timeline_sequence(request.user.id)
        timeline[edit_index:edit_index] = new_activities
        candidate_query.wakeup_time = wakeup_time
        if len(timeline) != 0:
            adjusted_timeline = adjust_timeline(timeline, last_end_time=wakeup_time)
            validate_timeline(adjusted_timeline)
            save_activities(None, adjusted_timeline, user=request.user)
        candidate_query.save()
        return Response(message_response(updated), 200)

    @staticmethod
    def get_wakeup_time(request):
        context = {
            'wakeup_time': request.user.wakeup_time
        }
        return Response(context)

    @staticmethod
    @swagger_auto_schema(request_body=ActivityListSerializer)
    def candidate_availability_list(request):
        session = request.data.get('session')
        candidate_query = get_object_or_404(Candidate, id=request.user.id, active=True)
        preserved = Case(*[When(**{'admin_priority__'+session: val}, then=pos) for pos, val in enumerate(
            ['high', 'medium', 'low'])])
        activity_card_objs = ActivityCard.objects.filter(
            sessions__contains=[session], active=True).\
            order_by(preserved, '-modified', RawSQL("popularity_score->>%s", (session,)))
        activity_card_ids = [
            activity_card.id
            for activity_card in activity_card_objs
            if any(
                item in candidate_query.lifestyle_responses
                for item in activity_card.lifestyle_responses
            )
        ]
        activity_card_objs1 = activity_card_objs.order_by(preserved, '-modified',
                                                            RawSQL("popularity_score->>%s", (session,))).\
            exclude(id__in=activity_card_ids)
        serializers = ActivityCardListingSerializer(activity_card_objs1, many=True)
        return Response(serializers.data)

    @staticmethod
    # @swagger_auto_schema(request_body=CandidateTimelineSerializer)
    def candidate_typical_day(request):
        timeline = get_timeline(request.user.id)
        serializers = CandidateTimelineSerializer(timeline, many=True)
        return Response(serializers.data)

    @staticmethod
    @swagger_auto_schema(request_body=AddTimelineSerializerSwagger)
    def add_to_timeline(request):
        data = request.data
        data['candidate'] = request.user.id
        last_activity = None
        try:
            last_activity = CandidateAvailability.objects.get(candidate=request.user, next_activity=None, active=True)
            data['start_time'] = last_activity.end_time
            data['previous_activity'] = last_activity.id
        except ObjectDoesNotExist:
            if request.user.wakeup_time is None:
                return Response(message_response(no_wakeup_time), status=400)
            data['start_time'] = request.user.wakeup_time
        if data['start_time'] == datetime.datetime.strptime(data['end_time'], '%H:%M').time():
            return Response(message_response(same_start_end), status=400)
        full_timeline = CandidateAvailability.objects.filter(active=True, candidate=request.user.id).\
            values('start_time', 'end_time')
        if data['start_time'] > datetime.datetime.strptime(data['end_time'], '%H:%M').time():
            split_1 = {**data, 'start_time': data['start_time'],
                       'end_time': datetime.datetime.strptime('23:59:59', '%H:%M:%S').time()}
            split_2 = {**data, 'start_time': datetime.datetime.strptime('00:00:00', '%H:%M:%S').time(),
                       'end_time': datetime.datetime.strptime(data['end_time'], '%H:%M').time(),
                       'previous_activity': None}
            check_overlap(full_timeline, split_1)
            check_overlap(full_timeline, split_2)
            serializer_1 = TimelineSerializer(data=split_1)
            serializer_2 = TimelineSerializer(data=split_2)
            serializer_1_validation = serializer_1.is_valid()
            serializer_2_validation = serializer_2.is_valid()
            if serializer_1_validation and serializer_2_validation:
                serializer_1.save()
                serializer_2.save(previous_activity_id=serializer_1.data['id'])
                if last_activity:
                    last_activity.next_activity_id = serializer_1.data['id']
                    last_activity.save()
                serializer_2.next_activity_id = serializer_2.data['id']
                first = CandidateAvailability.objects.get(id=serializer_1.data['id'])
                first.next_activity_id = serializer_2.data['id']
                first.save()
                response = TimelineDetailSerializer(first).data
                response.update({'total_duration': get_total_duration(request.user.wakeup_time,
                                                                      datetime.datetime.strptime(data['end_time'],
                                                                                                 '%H:%M').time()),
                                 'end_time': serializer_2.data['end_time']})
                return Response(response)
            return Response(message_response(mandatory_fields_missing), status=400)
        else:
            check_overlap(full_timeline, {'start_time': data['start_time'],
                                          'end_time': datetime.datetime.strptime(data['end_time'], '%H:%M').time()})
            serializer = TimelineSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                if last_activity:
                    last_activity.next_activity_id = serializer.data['id']
                    last_activity.save()
                response = serializer.data
                response.update({'total_duration': get_total_duration(request.user.wakeup_time,
                                                                      datetime.datetime.strptime(data['end_time'],
                                                                                                 '%H:%M').time())})
                is_filled_min_hours = min_hours_filled_in_my_typical_day(request.user.id)
                # send notification to the recruiter if the candidate filled minimum hours of my typical day 
                try:
                    functional_query = Functional.objects.filter(active=True, candidate=request.user.id, status=2)
                    if list(functional_query) and is_filled_min_hours:
                        sent_by_super_admin = get_object_or_404(AdminUser, roles=SUPER_ADMIN_ROLE, email=SUPER_ADMIN_EMAIL, active=True)
                        candidate_name = f"{functional_query[0].candidate.first_name} {functional_query[0].candidate.last_name}"
                        for functional_obj in functional_query:
                            notify_admin(item_type=ITEM_TYPE_CANDIDATE, item_id=functional_obj.candidate.id, sent_by=sent_by_super_admin,
                                    sent_by_type=request.role, sent_to_type=SENT_TO_TYPE_RECRUITER, message=notification_to_recruiter.format(candidate_name=candidate_name, project_name=functional_obj.project.company_name),
                                    sent_to=functional_obj.project.recruiter)
                except Exception as e:
                    log_data = [f"info|| {datetime.datetime.now()}: Exception occured in add to time line api"]
                    log_data.append(f"error|| {e}")
                    api_logging(log_data)
                if is_filled_min_hours:
                    Candidate.objects.filter(active=True, id=request.user.id).update(
                    timeline_completed=True, timeline_last_updated=datetime.datetime.now(), notification_count=0, last_notified=None)

                candidate_availability = CandidateAvailability.objects.get(id=serializer.data['id'])
                response = TimelineDetailSerializer(candidate_availability).data
                response.update({'total_duration': get_total_duration(request.user.wakeup_time,
                                                                      datetime.datetime.strptime(data['end_time'],
                                                                                                 '%H:%M').time())})
                return Response(response)
            return Response(serializer.errors, status=400)

    @staticmethod
    @swagger_auto_schema(request_body=EditTimelineSerializerSwagger,
                         operation_description="new_activities is a list of objects with keys 'end_time' and 'activity_card'")
    def edit_timeline(request, availability_id):
        activity = request.data.get('activity_card')
        new_activities = request.data.get('new_activities', [])
        check_invalid([request.data.get('end_time'), activity])
        candidate_activity = get_object_or_404(CandidateAvailability, id=availability_id,
                                               candidate=request.user.id, active=True)
        start_time = candidate_activity.start_time
        end_time_after_update = datetime.datetime.strptime(request.data.get('end_time'), '%H:%M').time()
        timeline, edit_index = get_timeline_sequence(request.user.id, availability_id)
        if start_time == end_time_after_update:
            return Response(message_response(same_start_end), status=400)
        edited_portion = [{'id': availability_id, 'start_time': start_time, 'end_time': end_time_after_update,
                          'activity_card': activity}]
        edited_last_end = end_time_after_update
        for each_new in new_activities:
            each_new['start_time'] = edited_last_end
            each_new['end_time'] = datetime.datetime.strptime(each_new['end_time'], '%H:%M').time()
            edited_last_end = each_new['end_time']
        deleted_ids = []
        for i in timeline[edit_index+1:]:
            if candidate_activity.activity_card.id != i['activity_card']:
                break
            deleted_ids.append(i['id'])
            timeline.remove(i)
        timeline[edit_index:edit_index+1] = edited_portion + new_activities
        # Adjust timeline with latest changes
        adjusted_timeline = adjust_timeline(timeline, last_end_time=request.user.wakeup_time)
        # Validate new timeline
        validate_timeline(adjusted_timeline)
        delete_extra_activities(deleted_ids)
        # Save changes
        save_activities(candidate_activity.previous_activity, adjusted_timeline[edit_index:], new_activities,
                        request.user, availability_id)
        # send notification to the recruiter if the candidate filled minimum hours of my typical day 
        is_filled_min_hours = min_hours_filled_in_my_typical_day(request.user.id)
        try:
            functional_query = Functional.objects.filter(active=True, candidate=request.user.id, status=2)
            if list(functional_query) and is_filled_min_hours:
                sent_by_super_admin = get_object_or_404(AdminUser, roles=SUPER_ADMIN_ROLE, email=SUPER_ADMIN_EMAIL, active=True)
                candidate_name = f"{functional_query[0].candidate.first_name} {functional_query[0].candidate.last_name}"
                for functional_obj in functional_query:
                    notify_admin(item_type=ITEM_TYPE_CANDIDATE, item_id=functional_obj.candidate.id, sent_by=sent_by_super_admin,
                            sent_by_type=request.role, sent_to_type=SENT_TO_TYPE_RECRUITER, message=notification_to_recruiter.format(candidate_name=candidate_name, project_name=functional_obj.project.company_name),
                            sent_to=functional_obj.project.recruiter)
        except Exception as e:
            log_data = [f"info|| {datetime.datetime.now()}: Exception occured in add to time line api"]
            log_data.append(f"error|| {e}")
            api_logging(log_data)
        if is_filled_min_hours:
            Candidate.objects.filter(active=True, id=request.user.id).update(
            timeline_completed=True, timeline_last_updated=datetime.datetime.now(), notification_count=0, last_notified=None)
        return Response(message_response(updated))

    @staticmethod
    @swagger_auto_schema(request_body=AddTimelineSerializerSwagger)
    def delete_activity(request, availability_id):
        new_activities = request.data.get('new_activities', [])
        timeline, edit_index = get_timeline_sequence(request.user.id, availability_id)
        candidate_activity = get_object_or_404(CandidateAvailability, id=availability_id,
                                               candidate=request.user.id, active=True)
        edited_last_end = candidate_activity.previous_activity.end_time if candidate_activity.previous_activity else \
            request.user.wakeup_time
        for each_new in new_activities:
            each_new['start_time'] = edited_last_end
            each_new['end_time'] = datetime.datetime.strptime(each_new['end_time'], '%H:%M').time()
            edited_last_end = each_new['end_time']
        timeline[edit_index:edit_index + 1] = new_activities
        deleted_ids = []
        for i in timeline[edit_index:]:
            if candidate_activity.activity_card.id != i['activity_card']:
                break
            deleted_ids.append(i['id'])
            timeline.remove(i)
        # Adjust timeline with latest changes
        adjusted_timeline = adjust_timeline(timeline, last_end_time=request.user.wakeup_time)
        # Validate new timeline
        validate_timeline(adjusted_timeline)
        delete_extra_activities(deleted_ids)
        # Save changes
        previous_activity = candidate_activity.previous_activity
        next_activity = candidate_activity.next_activity
        candidate_activity.previous_activity = None
        candidate_activity.next_activity = None
        candidate_activity.active = False
        candidate_activity.save()
        if previous_activity:
            previous_activity.next_activity = None
            previous_activity.save()
        if next_activity:
            next_activity.previous_activity = None
            next_activity.save()
        save_activities(previous_activity, adjusted_timeline[edit_index:], new_activities, request.user)
        if not min_hours_filled_in_my_typical_day(request.user.id):
            Candidate.objects.filter(active=True, id=request.user.id).update(
            timeline_completed=False, timeline_last_updated=datetime.datetime.now())
        return Response(message_response(deleted))

    @staticmethod
    @swagger_auto_schema(request_body=UpdateTimelineStatusSerializer)
    def update_timeline_status(request):
        timeline_completed = request.data.get('timeline_completed')
        Candidate.objects.filter(active=True, id=request.user.id).update(
            timeline_completed=timeline_completed, timeline_last_updated=datetime.datetime.now(), notification_count=0, last_notified=None)
        return Response(message_response(updated))
