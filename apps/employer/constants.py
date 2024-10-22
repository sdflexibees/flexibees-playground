EMPLOYER = 'employer'
DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "aol.com", "hotmail.co.uk", "hotmail.fr", 
    "msn.com", "yahoo.fr", "wanadoo.fr", "orange.fr", "comcast.net", "yahoo.co.uk", 
    "yahoo.com.br", "yahoo.co.in", "live.com", "rediffmail.com", "free.fr", "gmx.de", 
    "web.de", "yandex.ru", "ymail.com", "libero.it", "outlook.com", "uol.com.br", 
    "bol.com.br", "mail.ru", "cox.net", "hotmail.it", "sbcglobal.net", "sfr.fr", 
    "live.fr", "verizon.net", "live.co.uk", "googlemail.com", "yahoo.es", "ig.com.br", 
    "live.nl", "bigpond.com", "terra.com.br", "yahoo.it", "neuf.fr", "yahoo.de", 
    "alice.it", "rocketmail.com", "att.net", "laposte.net", "facebook.com", 
    "bellsouth.net", "yahoo.in", "hotmail.es", "charter.net", "yahoo.ca", 
    "yahoo.com.au", "rambler.ru", "hotmail.de", "tiscali.it", "shaw.ca", "yahoo.co.jp", 
    "sky.com", "earthlink.net", "optonline.net", "freenet.de", "t-online.de", 
    "aliceadsl.fr", "virgilio.it", "home.nl", "qq.com", "telenet.be", "me.com", 
    "yahoo.com.ar", "tiscali.co.uk", "yahoo.com.mx", "voila.fr", "gmx.net", 
    "mail.com", "planet.nl", "tin.it", "live.it", "ntlworld.com", "arcor.de", 
    "yahoo.co.id", "frontiernet.net", "hetnet.nl", "live.com.au", "yahoo.com.sg", 
    "zonnet.nl", "club-internet.fr", "juno.com", "optusnet.com.au", "blueyonder.co.uk", 
    "bluewin.ch", "skynet.be", "sympatico.ca", "windstream.net", "mac.com", 
    "centurytel.net", "chello.nl", "live.ca", "aim.com", "bigpond.net.au"
]
LOGIN = 1
MOBILE_CHANGE = 2
MOBILE_OTP_MESSAGE = '{} is the OTP for verification at FlexiBees. Please use this to verify your phone number for FlexiBees. Do not share your OTP with anyone.'
DRAFT_JOB_PENDING = '1'
DRAFT_JOB_PUBLISHED = '2'
DEV='DEV'
STAGE='STAGE'
PROD = 'PROD'
CONVERSION_VALUES_USD = {
     "INR" : "0.012", 
     "SGD" : "0.016", 
     "USD" : "1.000",
     "SDG" : "7.200"
}
YEARS = "years"
MONTHLY = "months"
WEEKS = "weeks"
DAYS = "days"
DEFAULT_ADDITIONAL_AMOUNT = 10
DEFAULT_CURRENCY = 'USD'
DEFAULT_CURRENCY_SYMBOL = '$'
MINIMUM_DEFAULT_RATIO_PRICING = 10
DURATION = 1
CURRENCY_FORMAT = "INR"
JOB_CREATED = '1'
JOB_COMPLETED = '6'
PRICING_CONSTANT = 2
DEFAULT_PROJECT_DURATION = 344    #  In 2 month total working days is 43  the multplying by 8 number of hours have to work 
TOTAL_NUMBER_OF_HOUR_IN_DAY = 8
TOTAL_WORKING_DAYS_IN_WEEK = 5
AVERAGE_WEEKS_IN_MONTH = 4.33
DEFAULT_MONTHS = '3'
FUNCTIONAL_INTERVIEW_CLEARED = 2
FLEXIFIT_INTERVIEW_CLEARED = 2
JOB_ID_NOT_MATCHED = 'Please provide a valid job id'
SCHEDULED = 1
JOB_CANDIDATE_CLEARED = 3
JOB_CANDIDATE_REJECTED = 4
FEEDBACK_CLEARED = '3'
FEEDBACK_REJECTED = '4'
MAX_CANDIDATES = 5
MAX_DRAFT_CANDIDATES = 3
SCHEDULED = 1
CANDIDATE_JOB_STATUS_SCHEDULED = 1
CANDIDATE_JOB_STATUS_UPDATED = '2'
CUSTOM_STATUS_JOB_LIST = '2'
EXISTING_STATUS_JOB_LIST = '1'
DEFAULT_JOB_DURATION = '3'
CANDIDATE_JOB_STATUS_IN_REVIEW = 2
CONTRACT_PENDING = '8'
CANDIDATE_JOB_READY_STATE = '12'
POSITION_FILLED_REJECTED = 5
JOB_CANDIDATE_INTERVIEW_SCHEDULED = '4'
JOB_CREATED = '1'
JOB_SHORTLISTED = '2'
SLOT_BOOKING_EXCLUDE_THIS_DAYS = [ "Saturday", "Sunday"] 
INTERVIEW_SLOTS_BOOKING_STATUS = 1
# Status represents the following stages: (1 - Created), (4 - Candidate Interview Scheduled), (8 -ContractPending)
EMPLOYER_JOB_STATUS_ACTIVE_STATE = [ "1", "4", "8"]
INTERVIEW_SCHEDULED = '1'
INTERVIEW_CLEARED = '2'
INTERVIEW_REJECTED = '3'
CANDIDATE_SELECTED_TEMPLATE = 'candidate_selected.html'
CANDIDATE_SELECTED_SUBJECT = 'Congratulations !! Employer has Selected a Candidate'
TOTAL_SLOT_TO_BE_SELECTED = 2
WITHIN_A_DAY = 1
HIGHEST_PRIORITY = 101
# In job indivudual Details,excluding  candidate   which in this state  (5, "Position Filled Rejected") for timestamp 
ALLOWING_ONLY_SELECTED_AND_REJECTED = [3,4]
TIME_FORMAT_DEFINITION_FOR_JOB_DETAILS = '%Y-%m-%d %H:%M:%S'
EMPLOYER_SUPPORT_TEMPLATE = 'employer_support.html'
EMPLOYER_SUPPORT_SUBJECT = 'Enquiry from Employer'