from apps.candidate.models import Functional
from core.fcm import send_candidate_notification
from core.notification_contents import candidate_recruitment_typical_day_notification
from core.helper_functions import min_hours_filled_in_my_typical_day
from datetime import datetime
from flexibees_finance.settings import MAX_NO_OF_MY_TYPICAL_DAY_NOTIFICATIONS, HOURS_A_DAY
from apps.admin_app.views import api_logging
from django.utils import timezone


def notify_functional_candidates():
    """
    check weather the candidate cleared the interview, notifications sent is less then maximum
    notifications, candidate filled min hours of my typical day and the difference between the
    last notification time is grater than equal to present time
    """
    log_data = [f"info|| {datetime.now()}: Exception occured while sending my typical day notification"]
    try:
        functional_objs = Functional.objects.filter(active=True, status=2)
        if list(functional_objs):
            for functional_obj in functional_objs:
                try:
                    candidate_id = functional_obj.candidate.id
                    if functional_obj.no_of_notifications_on_my_typical_day < MAX_NO_OF_MY_TYPICAL_DAY_NOTIFICATIONS and \
                        not min_hours_filled_in_my_typical_day(candidate_id):
                        if functional_obj.last_notified :
                            time_diff_hours = round((timezone.now() - functional_obj.last_notified).total_seconds()/3600)
                        if not functional_obj.last_notified or time_diff_hours >= HOURS_A_DAY:
                            # check candidate is hire and project status are not in suspended or closed 
                            if functional_obj.candidate.hire and functional_obj.project.status not in [9,11]:
                                push_data = candidate_recruitment_typical_day_notification(candidate_id, f"{functional_obj.candidate.first_name} {functional_obj.candidate.last_name}", functional_obj.project.company_name, bool(functional_obj.candidate.lifestyle_responses))
                                send_candidate_notification(users=[candidate_id], push_data=push_data)
                                functional_obj.no_of_notifications_on_my_typical_day += 1
                                functional_obj.last_notified = datetime.now()
                                functional_obj.save()
                except Exception as e:
                    log_data.append(f"info|| {functional_obj}")
                    log_data.append(f"error|| {e}")
                    api_logging(log_data)
        return True
    except Exception as e:
        log_data.append(f"error|| {e}")
        api_logging(log_data)
        return False
