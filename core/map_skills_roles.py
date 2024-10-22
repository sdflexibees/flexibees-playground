import csv
import datetime
import re

from apps.admin_app.models import Skill, Role
from apps.candidate.models import Candidate

with open('/Users/appiness/Projects/flexibees_candidate/core/Go_live_legacy.csv') as csv_file:
    print('FIle opened')
    csv_reader = csv.reader(csv_file)
    line_count = 0
    bulk_candidates = []
    for row in csv_reader:
        if line_count == 0:
            email = row.index('Email')
            legacy_skills = row.index('Skill Set')
            last_role = row.index('Last Role')
            prior_role = row.index('Prior Roles')
            line_count += 1
        else:
            skills = re.split('; |, |\*|\n', row[legacy_skills])
            roles = re.split('; |, |\*|\n', row[last_role] + ',' + row[prior_role])
            skills_list = []
            roles_list = []
            for skill in skills:
                try:
                    skills_list.append(Skill.objects.get(tag_name__iexact=skill).id)
                except:
                    pass
            # if len(skills_list) != 0:
            #     try:
            #         c = Candidate.objects.get(email__iexact=row[email])
            #     except:
            #         pass
            #     print(row[email], skills_list)
            for role in roles:
                try:
                    roles_list.append(Role.objects.get(tag_name__iexact=role).id)
                except:
                    pass
            if len(roles_list) != 0 or len(skills_list) != 0:
                try:
                    c = Candidate.objects.get(email__iexact=row[email])
                    c.skills.add(*skills_list)
                    c.roles.add(*roles_list)
                except:
                    pass
                print(row[email], roles_list, skills_list)
        line_count += 1
        print(line_count)
    print(f'Processed {line_count} lines.')