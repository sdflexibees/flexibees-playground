# Admin Levels
ADMIN_LEVEL_CHOICES = (
    (1, 'Beginner'),
    (2, 'Intermediate'),
    (3, 'Expert'),
)

LIFESTYLE_RESPONSES_CHOICES = (
        ('1_a', 'Studying part time'),
        ('1_b', 'Studying full time'),
        ('1_c', 'Just graduated'),
        ('1_d', 'On a break'),
        ('1_e', 'Currently working full-time'),
        ('1_f', 'Currently working part-time'),
        ('1_g', 'Currently looking for work'),
        ('2_a', 'I live alone'),
        ('2_b', 'I live with friends'),
        ('2_c', 'I live in a nuclear family'),
        ('2_d', 'I live in a joint family'),
        ('3_2_c_a', 'I live with Parents'),
        ('3_2_c_b', 'I live with Spouse'),
        ('3_2_c_c', 'I live with Child'),
        ('3_2_c_d', 'I live with Spouse and Child'),
        ('3_e', 'I live with Others'),
        ('3_2_d_a', 'I live with Paternal/ Maternal Relatives'),
        ('3_2_d_b', 'I live with Spouse/ Maternal/ Paternal Relatives'),
        ('3_2_d_c', 'I live with Child / Maternal/ Paternal Relatives'),
        ('3_2_d_d', 'I live with Spouse and Child/ Maternal/ Paternal Relatives'),
        ('4_a', 'My-self'),
        ('4_b', 'Part time help'),
        ('4_c', 'Full time help'),
        ('4_d', 'Full time live-in-help'),
    )
# Employer Apps
CUSTUM_ROLES_SKILLS_STATUS = (
    ("1", "pending"),
    ("2", "approved"),
    ("3", "rejected"),
)
EMPLOYER_COMPANY_SIZE = (
    ("1","1 to 10"),
    ("2","11 to 50"),
    ("3","51 to 400"),
    ("4","401 to 1000"),
    ("5","above 1000"),

)
EMPLOYER_TARGET_AUDIENCE = (
    ("1","B2B"),
    ("2","B2C"),
    ("3","others"),

)
EMPLOYER_SOURCE = (
    ("1","Social media"),
    ("2","Referral"),
    ("3","Search engines"),
    ("4","others"),

)
EMPLOYER_STATUS = (
    ("1","Employer Created"),
    ("2","Profile Related"),
    ("3","Created Job"),
    ("4","Selection in Progress"),
    ("5","Job in Progress"),
    ("6","Completed"),
)
EMPLOYER_JOB_STATUS = (
    ("1", "Created"),
    ("2", "Candidate Shortlisted"),
    ("3", "Candidate Shown Interest"),
    ("4", "Candidate Interview Scheduled"),
    ("5", "Interview Cleared"),
    ("6", "Finally Selected"),
    ("7", "Project Confirmed"),
    ("8", "Contract Pending"),
    ("9", "Contract Pending from Client"),
    ("10", "Contract Pending from Candidate"),
    ("11", "Offered"),
    ("12", "Accepted"),
    ("13", "In Project"),
    ("14", "Project Canceled"),
    ("15", "Pending Renewal"),
    ("16", "Withdrawn"),
    ("17", "Dropped Off"),
    ("18", "Termination"),
    ("19", "Client in Limbo/Dropped Off"),
)

JOB_DRAFT_STATUS = (
    ("1","Pending"),
    ("2","Published"),
)
USER_TYPE_CHOICES = (
    ("1","Employer"),
)
CANDIDATE_STATES = (
    ("1", "Signed Up"),
    ("2", "Profile Completed"),
    ("3", "Ready For Functional"),
    ("4", "Functional Interview Scheduled"),
    ("5", "Functional Interview Completed"),
    ("6", "Functional Interview Failed"),
    ("7", "Ready For Flexifit"),
    ("8", "Flexifit Scheduled"),
    ("9", "Flexifit Interview Failed"),
    ("10", "Flexifit Completed"),
    ("11", "Ready for Client"),
    ("12", "Job Ready"),
    ("13", "Job Interested"),
    ("14", "Client Interview Scheduled"),
    ("15", "Client Interview Completed"),
    ("16", "Project Selected"),
    ("17", "Project Confirmed"),
    ("18", "Offered"),
    ("19", "Accepted"),
    ("20", "Project Started"),
    ("21", "Project In Progress"),
    ("22", "Project Suspended"),
    ("23", "Project Completed"),
    ("24", "Dormant"),
    ("25", "Unsubscribe/Delete"),
)
PROJECT_STATES = (
    ("1", "Finally Selected"),
    ("2", "Project Confirmed"),
    ("3", "Contract Pending"),
    ("4", "Offered"),
    ("5", "Accepted"),
    ("6", "Project Canceled"),
    ("7", "In Project"),
    ("8", "Completed"),
    ("9", "Pending Renewal"),
    ("10", "Withdrawn"),
    ("11", "Dropped off"),
)

CLIENT_STATES = (
    ("1", "Signed In"),
    ("2", "Profile Completed"),
    ("3", "Active"),
    ("4", "Sleeping"),
    ("5", "Dormant"),
    ("6", "Inactive"),
    ("7", "Withdrawn"),
)

FEEDBACK_STATUS =(
    ("1", "Pending"),
    ("2", "Approved"),
    ("3", "Rejected"),
)
CANDIDATE_JOB_STATUS = (
    (1,"Scheduled"),
    (2,"In Review"),
    (3,"Selected"),
    (4,"Rejected"),
    (5, "Position Filled Rejected"),
    (6,"Notification Sent"),
)

INTERVIEW_STATUS =(
    ("1", "Scheduled"),
    ("2", "Cleared"),
    ("3", "Rejected"),
)
CANDIDATE_JOINING_STATUS = (
    ("1","NOW"),
    ("2","LATER"),
)
EMPLOYER_OPERATED_GLOBALLY = (
    ("1", "Domestic"),
    ("2", "International")
)
EMPLOYER_JOB_PRICING_CURRENCY = (
    ("1", "INR"),("2","USD")
)