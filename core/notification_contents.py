from apps.candidate.models import ClientFeedback
from core.response_messages import selected_referral, not_selected_referral



def suspend_self_evaluation(project_id, role):
    return {
        'title': 'Project Suspended',
        'message': "Our apologies. Due to some factors not in our control, this {role} role has been suspended at the client's end. We will reach out to you soon when we have another role which matches your skills.".format(
            role=role),
        'item_id': project_id,
        'item_type': 'project'
    }



def send_assignment_notif(project_id, role):
    return {
        'title': 'New Assignment',
        'message': "Assignment given for {role} role. Kindly submit before the due date.".format(
            role=role),
        'item_id': project_id,
        'item_type': 'project'
    }


def interest_check_reminder_1(project_id, role):
    return {
        'title': 'Reminder',
        'message': "You have been shortlisted for a {role} role on FlexiBees! To participate in the process for this role, visit the 'Active Projects' section of your FlexiBees App, and click on \"Yes, I am Interested\"!".format(
            role=role),
        'item_id': project_id,
        'item_type': 'project'
    }


def interest_check_reminder_2(project_id, role):
    return {
        'title': 'Reminder',
        'message': "You could be a great fit! You have been shortlisted for a {role} role on FlexiBees but we haven't heard if you are interested. You can still participate in the process by visiting the 'Active Projects' section of your FlexiBees App and clicking \"Yes, I am Interested\". Hurry, time is running out!".format(
            role=role),
        'item_id': project_id,
        'item_type': 'project'
    }


def candidate_welcome(candidate_id):
    return {
        'title': 'Welcome to FlexiBees!',
        'message': "Welcome to FlexiBees! Kindly complete your profile to get noticed by our recruiters.",
        'item_id': candidate_id,
        'item_type': 'candidate'
    }


def closed_assignment(project_id, role, client_name):
    return {
        'title': 'Project Closed',
        'message': "We regret to inform you that you have not been selected for the {role} role at {client}. However, we will come back to you with another role that matches your skills better. We are thankful for the effort you have put into the process so far and want to assure you that it will be re-used if a similar role comes up in the future.".format(role=role, client=client_name),
        'item_id': project_id,
        'item_type': 'project'
    }


def closed_functional(project_id, role, client_name):
    return {
        'title': 'Project Closed',
        'message': "We regret to inform you that you have not been selected for the {role} role at {client}. However, we will come back to you with another role that matches your skills better. We are thankful for the effort you have put into the process so far and want to assure you that it will be re-used if a similar role comes up in the future.".format(
            role=role, client=client_name),
        'item_id': project_id,
        'item_type': 'project'
    }


def closed_flexifit(project_id, role, client_name):
    return {
        'title': 'Project Closed',
        'message': "We regret to inform you that you have not been selected for the {role} role at {client}. However, we will come back to you with another role that matches your skills better. We are thankful for the effort you have put into the process so far and want to assure you that it will be re-used if a similar role comes up in the future.".format(
            role=role, client=client_name),
        'item_id': project_id,
        'item_type': 'project'
    }


def reopen_notification(project_id, role):
    return {
        'title': 'Project Reopened',
        'message': "We are glad to inform you that the {role} role for which you were being considered by FlexiBees that got Suspended has been reopened from the client's end! To know more about your current stage in the process, visit the 'Active Projects' section of your FlexiBees App !".format(
            role=role),
        'item_id': project_id,
        'item_type': 'project'
    }


def candidate_typical_day_notification_after_signup():
    return {
        'title': 'Update Your Typical Day',
        'message': "Letting us know about your typical day will help us match you with roles that fit with your flexibility needs and constraints. Please complete this section at the earliest."
    }


def candidate_reappear_notification(candidate_id):
    return {
        'title': 'Update Your Typical Day',
        'message': "Its been quite some time since you updated the 'My Typical Day' section of your profile. Outdated information in this section may lead to us not matching you with the roles that fit with your current flexibility needs and constraints. Please view this section and update it if needed.",
        'item_id': candidate_id,
        'item_type': 'candidate'
    }


def candidate_typical_day_notification(candidate_id):
    return {
        'title': 'Update Your Typical Day',
        'message': "We noticed that you have not yet completed the 'My Typical Day' section of your profile. Letting us know about your typical day will help us match you with roles that fit with your flexibility needs and constraints. Please complete this section at the earliest.",
        'item_id': candidate_id,
        'item_type': 'candidate'
    }


def referral_text(candidate):
    user = ClientFeedback.objects.filter(active=True, recommendation=3, final_selection__candidate=candidate)
    if user.exists():
        return selected_referral
    else:
        return not_selected_referral


def candidate_recruitment_typical_day_notification(candidate_id, candidate_name, project_name, is_my_life_updated):
    return {
        'title': 'Update Your Typical Day',
        'message': f"Hi {candidate_name}, as you are in the recruitment process of {project_name} we request you to fill My Typical Day section (minimum 15 hours) to proceed further." if is_my_life_updated else f"Hi {candidate_name}, as you are in the recruitment process of {project_name} we request you to fill the My Life as well as My Typical Day (minimum 15 hours) section to proceed further.",
        'item_id': candidate_id,
        'item_type': 'candidate'
    }

def candidate_signup_notification_one():
    return {
        'title': "Sign up NOW for flexible opportunities!",
        'message': "Hello, Greetings from FlexiBees! You are almost there, please sign up on FlexiBees & update your profile to start getting flexible job opportunities",
    }

def candidate_signup_notification_two():
    return {
        'title': "You are missing out, Sign up NOW!",
        'message': "Hello, Greetings from FlexiBees! You are almost there, please sign up on FlexiBees & update your profile to start getting flexible job opportunities",
    }