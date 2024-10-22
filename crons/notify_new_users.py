from datetime import datetime, timedelta

from apps.admin_app.views import api_logging
from apps.notifications.models import UserDevice
from core.constants import MAX_DAYS_FOR_TOKEN, NOTIFY_INTERVAL
from core.fcm import send_candidate_notification
from core.notification_contents import candidate_signup_notification_one, candidate_signup_notification_two


def notify():
    """
    Notify the users who has installed the app regarding the signup
    """
    log_data = [f"info|| {datetime.now()}: Exception occured while sending newly app installed candidates"]
    try:
        message1_devices = []
        message2_devices = []
        current_date = datetime.now()
        max_notify_date = current_date - timedelta(days=MAX_DAYS_FOR_TOKEN)
        # get all the tokens which are created in previous 8 days range 
        device_tokens = UserDevice.objects.filter(user__isnull=True, created__date__gte=max_notify_date, active=True)
        for device_token in device_tokens:
            days = (current_date.date() - device_token.created.date()).days
            if days == NOTIFY_INTERVAL[0] or days == NOTIFY_INTERVAL[2]:
                message1_devices.append(device_token)
            elif days == NOTIFY_INTERVAL[1] or days == NOTIFY_INTERVAL[3]:
                message2_devices.append(device_token)
        # notify the users 
        if message1_devices:
            push_data = candidate_signup_notification_one()
            send_candidate_notification(devices=message1_devices, push_data=push_data, app_notify=False)           
        if message2_devices:
            push_data = candidate_signup_notification_two()
            send_candidate_notification(devices=message2_devices, push_data=push_data, app_notify=False)           
        return True
    except Exception as e:
        log_data.append(f"error|| {e}")
        api_logging(log_data)
        return False