from django.db.models import F

def get_profile_values():
    """
    get employer fields
    """
    employer_fields = ['id']
    other_values = {
        'company_name' : F('company__name'),
        'company_logo' : F('company__logo'),
        'website' : F('company__website'),
        'description' : F('company__description'),
        'size' : F('company__size'),
        'industry_type' : F('company__industry_type__tag_name'),
        'industry_id' : F('company__industry_type__id'),
        'target_audience' : F('company__target_audience'),
        'source' : F('company__source'),
        'mobile' : F('user__mobile'),
        'email' : F('user__email'),
        'address' : F('user__address'),
        'country_code' : F('user__country_code'),
        'first_name' : F('user__first_name'),
        'last_name' : F('user__last_name'),
        'profile_image' : F('user__profile_image'),
        'mobile_verified' : F('user__phone_verified'),
        'email_verified' : F('user__email_verified'),
    }
    return employer_fields, other_values