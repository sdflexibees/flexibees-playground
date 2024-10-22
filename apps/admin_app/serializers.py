from rest_framework.serializers import ModelSerializer, CharField, ImageField, Serializer, DictField, ListField, \
    SerializerMethodField

from .models import AdminUser, Function, Skill, Domain, Role, Configuration, Tags, Language, Dropdown, AppVersion
from apps.candidate.models import SelfAssessment


class AdminLoginSerializer(ModelSerializer):
    admin_role = CharField(default='super_admin')

    class Meta:
        model = AdminUser
        fields = ('email', 'password', 'admin_role')


class AdminUserDetailSerializer(ModelSerializer):

    class Meta:
        model = AdminUser
        exclude = ('active', 'created', 'modified', 'password')


class ChangePasswordSerializer(ModelSerializer):
    old_password = CharField(required=True)
    new_password = CharField(required=True)

    class Meta:
        model = AdminUser
        fields = ('old_password', 'new_password',)


class FunctionSerializer(ModelSerializer):
    name = CharField(source='tag_name')

    class Meta:
        model = Function
        fields = ('id', 'name')


class SkillSerializer(ModelSerializer):
    name = CharField(source='tag_name')

    class Meta:
        model = Skill
        fields = ('id', 'name', 'function')


class SkillListingSerializer(ModelSerializer):
    name = CharField(source='tag_name')
    function = CharField(source='function.tag_name')

    class Meta:
        model = Skill
        fields = ('id', 'name', 'function')


class AdminProfileUpdateSerializer(ModelSerializer):

    class Meta:
        model = AdminUser
        fields = ('profile_pic', 'description', 'phone', 'first_name', 'last_name', 'country_code',)


class DomainSerializer(ModelSerializer):
    name = CharField(source='tag_name')

    class Meta:
        model = Domain
        fields = ('id', 'name')


class RoleSerializer(ModelSerializer):
    name = CharField(source='tag_name')

    class Meta:
        model = Role
        fields = ('id', 'name')


class TagsSerializer(ModelSerializer):

    class Meta:
        model = Tags
        exclude = ('active', 'created', 'modified')


class ConfigurationSerializer(ModelSerializer):
    tags = TagsSerializer(many=True)

    class Meta:
        model = Configuration
        fields = ('id', 'title', 'tags', 'dropdown')


class ConfigurationCreateSerializer(ModelSerializer):

    class Meta:
        model = Configuration
        fields = ('id', 'title', 'tags', 'dropdown')


class MediaUploadSerializer(Serializer):
    media = ImageField()
    media_type = CharField(default='image')

    class Meta:
        model = AdminUser
        fields = ('media', 'media_type')


class AdminSerializer(ModelSerializer):

    class Meta:
        model = AdminUser
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'level', 'skills', 'roles', 'published',
                  'functions', 'country_code', 'active_projects')
        read_only_fields = ('id',)


class AdminListSerializer(AdminSerializer):
    skills = SkillSerializer(many=True)
    functions = FunctionSerializer(many=True)


class AdminCreateSerializer(ModelSerializer):

    class Meta:
        model = AdminUser
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'level', 'skills', 'roles', 'published',
                  'password', 'functions', 'country_code',)
        read_only_fields = ('id',)


class SearchListSerializer(ModelSerializer):
    search_term = CharField(default='')
    filter_data = DictField(default={'search_term': '', 'filter_data': {}})

    class Meta:
        model = AdminUser
        fields = ('search_term', 'filter_data')


class AdminInfoSerializer(ModelSerializer):

    class Meta:
        model = AdminUser
        fields = ('id', 'first_name',)


class LanguageSerializer(ModelSerializer):

    class Meta:
        model = Language
        fields = ('id', 'name',)


class RecruiterListSerializer(ModelSerializer):
    skills = SkillSerializer(many=True)
    must_have_skills = SerializerMethodField('fetch_must_have')
    assigned = SerializerMethodField('fetch_assigned')
    previous_recruiter = SerializerMethodField('fetch_previous')

    def fetch_previous(self, instance):
        previous = self.context.get('previous')
        if previous:
            return instance.id == previous
        return False

    def fetch_assigned(self, instance):
        assigned = self.context.get('assigned')
        if assigned:
            return instance.id == assigned
        return False

    def fetch_must_have(self, instance):
        must_have_skills = self.context.get('must_have_skills', [])
        return not set(must_have_skills).isdisjoint(instance.skills.all().values_list('id', flat=True))

    class Meta:
        model = AdminUser
        fields = ('id', 'first_name', 'email', 'country_code', 'phone', 'skills', 'active_projects',
                  'must_have_skills', 'assigned', 'previous_recruiter', 'published', 'level')


class DropdownSerializer(Serializer):
    dropdowns = ListField(required=True)

    class Meta:
        model = Dropdown
        fields = ('dropdowns',)


class SelfAssessmentListSerializer(ModelSerializer):
    skills = SerializerMethodField('fetch_skills')

    def fetch_skills(self, instance):
        must_have_skills = self.context.get('must_have_skills')
        return [
            {
                'skill': SkillSerializer(
                    Skill.objects.get(id=skill['skill'])
                ).data,
                'level': skill['level'],
                'must_have': skill['skill'] in must_have_skills,
            }
            for skill in instance.skills
        ]

    class Meta:
        model = SelfAssessment
        fields = ('skills',)


class AppVersionSerializer(ModelSerializer):

    class Meta:
        model = AppVersion
        exclude = ('active', 'created', 'modified',)

