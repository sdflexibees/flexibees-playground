import os
import pandas as pd
from apps.common.models import RoleMapping ,SkillMapping
from apps.admin_app.models import Role,Skill,Function

# This is supportive function of (role_mapping_creation_scripts) , This function only check and create skill mapping objects
def skill_mapping_script(exel_function_name, exel_role_name, exel_skills_name, function_db_object, error_details, mapping_table_info, skill_error_details, role_mapping_with_function, skill_not_in_sheet):
    
    try:
        try:
            skill_db_object = Skill.objects.get(tag_name__icontains=exel_skills_name) 
        except Exception as x:
            skill_db_object = Skill.objects.get(tag_name=exel_skills_name)

        #  Checking if the current role and skill mapping exists in the SkillMapping table; if not, creating it
        if skill_db_object.id not  in skill_not_in_sheet:
            skill_not_in_sheet.append(skill_db_object.id)
        skill_in_function = set(SkillMapping.objects.filter(skill__tag_name=skill_db_object.tag_name).exclude(role_mapping__function__pk=function_db_object.id ).values_list('role_mapping__function__tag_name', flat=True))

        if skill_in_function:
            mapping_table_info[3].append("Skill Exist In diffrent Function "+str(skill_in_function ) )

            skill_error_details[0].append(exel_function_name)
            skill_error_details[1].append(exel_role_name)
            skill_error_details[2].append(exel_skills_name)
            skill_error_details[3].append("Skill Exist In diffrent Function "+str(skill_in_function ) )
        else:
            # Checking if the current role and skill mapping exists in the SkillMapping table; if not, creating it
            skill_role_mapping_obj = SkillMapping.objects.filter(role_mapping__pk = role_mapping_with_function.id ,skill__id = skill_db_object.id )

            if skill_role_mapping_obj.exists():
                mapping_table_info[3].append(str("Mapping already exist"))
            else:
                SkillMapping.objects.create(role_mapping = role_mapping_with_function, skill = skill_db_object)
                mapping_table_info[3].append(str("Mapping created"))
    except Exception as x:
        mapping_table_info[3].append(str(x))
        skill_error_details[0].append(exel_function_name)
        skill_error_details[1].append(exel_role_name)
        skill_error_details[2].append(exel_skills_name)
        skill_error_details[3].append(str(x))
        error_details.append(["Skill Exception Details",exel_function_name,exel_role_name,exel_skills_name,str(x)])


# This is supportive function of (mapping_conversion) , This function only check and create role mapping objects
def role_mapping_creation_scripts(exel_function_name, exel_role_name, exel_skills_name, function_db_object, role_db_object, role_mapping_object, error_details, mapping_table_info, role_error_details, skill_error_details, skill_not_in_sheet):
    
    # Here we are checking if the current role and function mapping exists  in RoleMapping table .
    if role_mapping_object.exists():
        mapping_table_info[3].append("Role Exist In diffrent Function "+str(role_mapping_object.values_list('function__tag_name', flat=True)))
        role_error_details[0].append(exel_function_name)
        role_error_details[1].append(exel_role_name)
        role_error_details[2].append("Role Exist In diffrent Function "+str(role_mapping_object.values_list('function__tag_name', flat=True)))    
    else:
        try:
            # Checking if the current role and function mapping exists in the RoleMapping table; if not, creating it
            role_mapping_with_function = RoleMapping.objects.filter(function__pk=function_db_object.id ,role__pk=role_db_object.id )
            if role_mapping_with_function.exists()!=True :
                role_mapping_with_function = RoleMapping.objects.create(function=function_db_object ,role=role_db_object )
            else:
                role_mapping_with_function=list(role_mapping_with_function)[0]           
            skill_mapping_script(exel_function_name, exel_role_name, exel_skills_name, function_db_object, error_details, mapping_table_info, skill_error_details, role_mapping_with_function, skill_not_in_sheet)

        except Exception as x:

            error_details.append(["Role Exception Details",exel_function_name,exel_role_name,exel_skills_name,str(x)])
            role_error_details[0].append(exel_function_name)
            role_error_details[1].append(exel_role_name)
            role_error_details[2].append(str(x))
            mapping_table_info[3].append(str(x))


# This function is used to convert exel file data into mapping obj on the base on the function , role and skills provided in the exel file
# In return statement  function will provide   summary of output file with error details (logs). 
def mapping_conversion(path ,output_path,filename ):

    # Path varibale is used to take input file path
    # output_path is used to take output file path
    # filename is used to take output file name
    read_mapping_file = pd.read_excel(path)
    error_details=[]
    # This is use to store summary of output file (logs) (mapping_table_info ,role_error_details,skill_error_details,function_not_in_sheet)
    mapping_table_info =[['Function'],['Role'],['Skills'],['Remarks']]
    role_error_details=[['Function'],['Role'],['Error']]
    skill_error_details=[['Function'],['Role'],['Skills'],['Error']]
    function_not_in_sheet=['Function']    
    # Role not in sheet
    role_not_in_sheet=[]
    skill_not_in_sheet=[]
    # Iterating all rows in the exel sheet from user input file
    for exel_sheet in read_mapping_file.iterrows():
        try:
            exel_function_name=exel_sheet[1]['Functions']
            exel_role_name=exel_sheet[1]['Roles']
            exel_skills_name=exel_sheet[1]['Skills']

            mapping_table_info[0].append(exel_function_name)
            mapping_table_info[1].append(exel_role_name)
            mapping_table_info[2].append(exel_skills_name)

            function_db_object = Function.objects.get(tag_name=exel_function_name)
            try:
                try:
                    role_db_object = Role.objects.get(tag_name__icontains=exel_role_name)
                except Exception as x:
                    role_db_object = Role.objects.get(tag_name=exel_role_name)
                if role_db_object.id not in role_not_in_sheet :
                    role_not_in_sheet.append(role_db_object.id)
                # For checking Function and Role is Not Exists in diffrent Role Mapping function
                role_mapping_object = RoleMapping.objects.filter(role__pk=role_db_object.id).exclude(function__id=function_db_object.id)
                role_mapping_creation_scripts(exel_function_name, exel_role_name, exel_skills_name, function_db_object, role_db_object, role_mapping_object, error_details, mapping_table_info, role_error_details, skill_error_details, skill_not_in_sheet)

            except Exception as x:
                role_error_details[0].append(exel_function_name)
                role_error_details[1].append(exel_role_name)
                role_error_details[2].append(str(x))
                mapping_table_info[3].append(str(x))
                error_details.append(['Role Exception ',exel_function_name, exel_role_name, exel_skills_name, str(x)])     
        except Exception as x:
            error_details.append(["Main Exception",exel_function_name,str(x)])

    function_which_not_exist_in_sheet = list(Function.objects.exclude(tag_name__in=list(read_mapping_file['Functions'].unique())))
    function_not_in_sheet = function_not_in_sheet + function_which_not_exist_in_sheet
    # z_index_data.xlsx     Example of File Name 
    output_folder_path = os.path.join(output_path ,filename)
    
    # Here I am fetching all Roles, which is not  present in  sheet and exists in the database.
    role_not_in_sheet = list(Role.objects.exclude(pk__in=role_not_in_sheet).values_list('tag_name',flat=True))
    # Here I am fetching all Skills, which is not present in the sheet and exists in the database.
    skill_not_in_sheet = list(Skill.objects.exclude(pk__in=skill_not_in_sheet).values_list('tag_name',flat=True))

    skill_error_details = pd.DataFrame(skill_error_details).T
    role_error_details = (pd.DataFrame(role_error_details).T)

    skill_error_details =skill_error_details.drop_duplicates()
    role_error_details = role_error_details.drop_duplicates()

    with pd.ExcelWriter(output_folder_path, engine='openpyxl') as writer:
        (pd.DataFrame(mapping_table_info ).T).to_excel(writer, sheet_name='List Of All Mapping', index=False)
        (pd.DataFrame(error_details)).to_excel(writer, sheet_name='Error Master', index=False)
        role_error_details.to_excel(writer, sheet_name='Role Function Mapping Error', index=False)
        skill_error_details.to_excel(writer, sheet_name='Skill and Role Mapping Error', index=False)
        (pd.DataFrame(function_not_in_sheet)).to_excel(writer, sheet_name='Function Not In Sheet', index=False)
        (pd.DataFrame(role_not_in_sheet , columns=["Roles"])).to_excel(writer, sheet_name='Roles Not In Sheet', index=False),
        (pd.DataFrame(skill_not_in_sheet , columns=["Skilles"])).to_excel(writer, sheet_name='Sills Not In Sheet', index=False),
    return output_folder_path
