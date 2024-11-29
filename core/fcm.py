import requests
from datetime import datetime
from core.string_constants import LINE_BREAK
from apps.notifications.models import UserDevice, CandidateNotification
from flexibees_finance.settings import FCM_PROJECT_ID
from flexibees_finance.settings.base import FCM_CREDENTIALS_PATH, FCM_NOTIFICATION_URL, FCM_SCOPES
from google.oauth2.service_account import Credentials
import google.auth.transport.requests


def _get_access_token():
    """
    Generates an OAuth 2.0 access token for authenticating with the FCM API.
    
    This function uses a service account JSON file to generate credentials,
    which are then used to request a fresh access token. This token is
    required for making authenticated API calls to Firebase Cloud Messaging.
    
    Returns:
        str: A valid OAuth 2.0 access token.
    """
    
    # Load the service account credentials from the provided JSON file.
    # The 'scopes' parameter specifies the required API scopes (permissions).
    credentials = Credentials.from_service_account_file(
      FCM_CREDENTIALS_PATH, scopes=FCM_SCOPES)

    # Create a new HTTP request object needed to refresh the credentials.
    request = google.auth.transport.requests.Request()

    # Refresh the credentials to ensure the access token is up-to-date.
    credentials.refresh(request)

    # Return the freshly generated access token to be used in API requests.
    return credentials.token

def get_user_devices_and_notifications(users, devices, app_notify, data_message):
    """
    Determine the devices to send notifications to and prepare notifications to be recorded.
    
    :param users: List of users to send notifications to.
    :param devices: List of devices to send notifications to.
    :param app_notify: Boolean to indicate if app notifications should be recorded.
    :param data_message: Dictionary containing data about the notification.
    :return: Tuple containing the list of user devices and a list of bulk notifications.
    """
    # Initialize bulk notification list
    bulk_notification = []
    user_devices = []
    # Determine the devices to send notifications to
    if devices:
        user_devices = devices  # Use provided devices list if available
    else:
        # Get active devices based on provided users or all active devices if no users are provided
        user_devices = list(UserDevice.objects.filter(user__in=users, active=True)) if users else list(UserDevice.objects.filter(active=True))
        
        if app_notify:
            # Record notifications for the appropriate users
            bulk_notification = [
                CandidateNotification(
                    item_type=data_message['item_type'],
                    item_id=data_message['item_id'],
                    sent_to_id=user if users else None,
                    all=not users,
                    message=data_message['message']
                )
                for user in (users if users else [None])
            ]
            # Save all notifications in bulk
            CandidateNotification.objects.bulk_create(bulk_notification)
    
    return user_devices

def send_fcm_notification(tokens, data_message):
    """
    Sends FCM (Firebase Cloud Messaging) notifications to multiple device tokens.
    
    Args:
        tokens (list): A list of device tokens to which the notifications should be sent.
        data_message (dict): A dictionary containing the notification title, body, and additional data.

    Returns:
        response: The HTTP response from the FCM API.
    """
    
    # Importing the api_logging function for logging purposes.
    from apps.admin_app.views import api_logging
    
    # Define the headers needed for the HTTP request, including the access token for authorization.
    headers = {
        'Authorization': f'Bearer {_get_access_token()}',  # Fetch the access token
        'Content-Type': 'application/json; UTF-8',  # Set the content type for JSON data
    }

    # Create the message payload structure for FCM
    message = {
        "message": {
            "notification": {
                'title': data_message['title'],  # Title of the notification
                'body': data_message['message'],  # Body of the notification
            },
            "data": data_message,  # Additional data to send with the notification
        }
    }

    # Loop through each token to send notifications to individual devices
    for token in tokens:
        try:
            # Add the current token to the message payload
            message['message']['token'] = token
            
            # Set the FCM server URL with the project ID (FCM_PROJECT_ID)
            url = FCM_NOTIFICATION_URL.format(project_id=FCM_PROJECT_ID)
            
            # Send the notification using a POST request with the specified URL, headers, and message payload
            response = requests.post(url, headers=headers, json=message)
            
            # Check if the response contains a non-2xx status code, raise an exception if so
            response.raise_for_status()
        
        except Exception as e:
            # Log the error and response in case of an exception
            log_data = [f"info || {datetime.now()}: send_fcm_notification function"]
            log_data.append(f"info || exception : {e}")  # Log the exception
            log_data.append(response.json())  # Log the response details
            log_data.append(LINE_BREAK)
            api_logging(log_data)  # Call the api_logging function to store logs

    # Return the last response received (could be from the last token in the loop)
    return True

def send_candidate_notification(users=[], app_notify=True, devices=[], **kwargs):
    """
    Send notification using Firebase Cloud Messaging (FCM).
    Requires 'Firebase Admin SDK' which is configured in the settings.
    
    :param users: List of users to send notifications to. Defaults to an empty list.
    :param app_notify: Boolean to indicate if app notifications should be recorded. Defaults to True.
    :param devices: List of devices to send notifications to. Defaults to an empty list.
    :param kwargs: Additional data for the notification, including 'title', 'body', and 'push_data'.
    :return: Result from Firebase or False if an exception occurs.
    """
    from apps.admin_app.views import api_logging

    try:
        # Get the push data (additional data) for the notification from kwargs
        data = kwargs.get('push_data', {})
        
        # Ensure all values in data_message are strings (Firebase requires this)
        data_message = {key: str(value) for key, value in data.items()}
        
        if not isinstance(users, list):
            users = [users]  # Ensure users is a list, even if a single user is passed
        
        # Determine the devices to send notifications to
        # Get user devices and bulk notifications
        user_devices = get_user_devices_and_notifications(users, devices, app_notify, data_message)
        # Categorize devices by type (iOS, Android, Web)
        tokens = [x.registration_id for x in user_devices]
        # Send the message using Firebase
        send_fcm_notification(tokens, data_message)
        return True
    except Exception as e:
        # Log any exceptions that occur during the notification process
        log_data = [f"info || {datetime.now()}: send_candidate_notification function"]
        log_data.append(f"info || exception : {e}")
        log_data.append(LINE_BREAK)
        api_logging(log_data)
        return False
