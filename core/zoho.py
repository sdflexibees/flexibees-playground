import datetime
import json
import http.client

from apps.admin_app.models import ZOHOToken
from apps.admin_app.views import api_logging
from flexibees_finance.settings import ZOHO_REFRESH_TOKEN, ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET


def get_access_token():
    conn = http.client.HTTPSConnection("accounts.zoho.com")
    conn.request("POST", "/oauth/v2/token?refresh_token=" + ZOHO_REFRESH_TOKEN + '&client_id=' + ZOHO_CLIENT_ID +
                 '&client_secret=' + ZOHO_CLIENT_SECRET + '&grant_type=refresh_token')
    res = conn.getresponse()
    data_1 = res.read()
    data_1 = json.loads(data_1.decode("utf-8"))
    ZOHOToken.objects.create(access_token=data_1['access_token'], refresh_token=ZOHO_REFRESH_TOKEN)
    access_token = data_1['access_token']
    return access_token


def get_crm_data(bd_email=None, all=False):
    try:
        conn = http.client.HTTPSConnection("www.zohoapis.com")
        date = (datetime.datetime.now().date() - datetime.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
        criteria = f"((Modified_Time:greater_than:{date}){f'AND(Owner.email:equals:{bd_email})'if bd_email else ''})"
        def get_data_from_crm(result=[], page=1, access_token=None):
            if not access_token:
                try:
                    access_token = ZOHOToken.objects.filter(active=True).first().access_token
                except Exception:
                    return get_data_from_crm(result, page, get_access_token())
            headers = {
                'Authorization': 'Zoho-oauthtoken ' + access_token
            }
            try:
                url = f"/crm/v5/Deals/search?page={str(page)}&criteria={criteria}"
                if all:
                    url = f"/crm/v2/Deals?page={str(page)}"
                conn.request("GET", url, headers=headers)
                res = conn.getresponse()
                data = res.read()
                data = json.loads(data.decode("utf-8"))
                result.extend(data['data'])
            except Exception:
                return get_data_from_crm(result, page, get_access_token())
            return get_data_from_crm(result, page+1, access_token if access_token else None) if data["info"]["more_records"] else result
        return get_data_from_crm()
    except Exception as e:
        log_data = [f"info|| {datetime.datetime.now()}: pull_from_crm"]
        log_data.append(f"error|| {e}")
        api_logging(log_data)
        return []
