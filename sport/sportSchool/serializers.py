from rest_framework import serializers
from django.contrib.auth import get_user_model
from sportSchool.models import *

User = get_user_model()

# -----------------------------
# User
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'middle_name', 'email', 'role']

# -----------------------------
# Department
# -----------------------------
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

# -----------------------------
# Coach
# -----------------------------
class CoachSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        source='department',
        queryset=Department.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Coach
        fields = ['id', 'user', 'department', 'department_id']

class GroupSerializer(serializers.ModelSerializer):
    coach = CoachSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        source='coach',
        queryset=Coach.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    department_id = serializers.PrimaryKeyRelatedField(
        source='department',
        queryset=Department.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    athletes_count = serializers.SerializerMethodField()  # добавлено

    class Meta:
        model = Group
        fields = ['id', 'name', 'department', 'department_id', 'level', 'coach', 'coach_id','athletes_count']

    def get_athletes_count(self, obj):
        return obj.athletes.count() # или obj.athletes.count() если related_name='athletes'

# -----------------------------
# Athlete
# -----------------------------
class AthleteSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(
        source='group',
        queryset=Group.objects.all(),
        write_only=True
    )
    attendance_rate = serializers.SerializerMethodField()
    last_rank = serializers.SerializerMethodField()

    class Meta:
        model = Athlete
        fields = [
            'id', 'first_name', 'last_name', 'middle_name',
            'birth_date', 'gender',
            'group', 'group_id', 'attendance_rate', 
    'last_rank'
        ]

    def get_last_rank(self, obj):
        # берём последнее присвоение по дате приказа
        last_assignment = (
            AthleteRankAssignment.objects
            .filter(athlete=obj)
            .select_related('rank_order')  # чтобы не делать extra запрос для order_date
            .order_by('-rank_order__order_date', '-assignment_date')  # сначала по приказу, потом на всякий случай по дате присвоения
            .first()
        )
        return last_assignment.assigned_rank if last_assignment else None

    def get_attendance_rate(self, obj):
        total = Attendance.objects.filter(training_plan__group=obj.group, athlete=obj).count()
        if total == 0:
            return 0
        present = Attendance.objects.filter(training_plan__group=obj.group, athlete=obj, status='present').count()
        return round((present / total) * 100)

# -----------------------------
# TrainingType
# -----------------------------
class TrainingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingType
        fields = ['id', 'name']

# -----------------------------
# TrainingHour & TrainingPlan
# -----------------------------
class TrainingHourSerializer(serializers.ModelSerializer):

    training_type = TrainingTypeSerializer(
        read_only=True
    )

    training_type_id = serializers.PrimaryKeyRelatedField(
        source='training_type',
        queryset=TrainingType.objects.all(),
        write_only=True
    )

    class Meta:
        model = TrainingHour
        fields = [
            'id',
            'training_type',
            'training_type_id',
            'hours'
        ]

class TrainingPlanSerializer(serializers.ModelSerializer):

    group = GroupSerializer(read_only=True)

    group_id = serializers.PrimaryKeyRelatedField(
        source='group',
        queryset=Group.objects.all(),
        write_only=True
    )

    training_hours = TrainingHourSerializer(
        many=True
    )

    class Meta:
        model = TrainingPlan
        fields = [
            'id',
            'group',
            'group_id',
            'date',
            'total_hours',
            'training_hours'
        ]

    def update(self, instance, validated_data):

        training_hours_data = validated_data.pop(
            'training_hours',
            []
        )

        instance.total_hours = validated_data.get(
            'total_hours',
            instance.total_hours
        )

        instance.save()

        # удаляем старые часы
        instance.training_hours.all().delete()

        # создаём новые
        for item in training_hours_data:

            TrainingHour.objects.create(
                training_plan=instance,
                training_type=item['training_type'],
                hours=item['hours']
            )

        return instance

# -----------------------------
# Attendance
# -----------------------------
class AttendanceSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(read_only=True)
    athlete_id = serializers.PrimaryKeyRelatedField(
        source='athlete',
        queryset=Athlete.objects.all(),
        write_only=True
    )
    training_plan = TrainingPlanSerializer(read_only=True)
    training_plan_id = serializers.PrimaryKeyRelatedField(
        source='training_plan',
        queryset=TrainingPlan.objects.all(),
        write_only=True
    )

    class Meta:
        model = Attendance
        fields = ['id', 'athlete', 'athlete_id', 'training_plan', 'training_plan_id', 'status', 'absence_reason']

# -----------------------------
# Competition & CompetitionResult
# -----------------------------
class CompetitionResultSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(read_only=True)
    athlete_id = serializers.PrimaryKeyRelatedField(
        source='athlete',
        queryset=Athlete.objects.all(),
        write_only=True
    )
    coach = CoachSerializer(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        source='coach',
        queryset=Coach.objects.all(),
        write_only=True
    )

    class Meta:
        model = CompetitionResult
        fields = [
            'id', 'competition', 'athlete', 'athlete_id',
            'coach', 'coach_id', 'place', 'weight_category', 'is_participant'
        ]

class CompetitionSerializer(serializers.ModelSerializer):
    coach = CoachSerializer(read_only=True)
    coach_id = serializers.PrimaryKeyRelatedField(
        source='coach',
        queryset=Coach.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    results = CompetitionResultSerializer(many=True, read_only=True, source='competitionresult_set')
    protocol = serializers.FileField(use_url=True) 

    class Meta:
        model = Competition
        fields = ['id', 'name', 'date', 'location', 'level', 'coach', 'coach_id', 'protocol', 'status', 'review_comment', 'results']

# -----------------------------
# AdministrativeDoc
# -----------------------------
class AdministrativeDocSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = AdministrativeDoc
        fields = ['id', 'doc_type', 'file_path', 'created_by', 'created_at'] 

# -----------------------------
# RankAssignmentOrder & AthleteRankAssignment Serializers
# -----------------------------
class AthleteRankAssignmentSerializer(serializers.ModelSerializer):
    athlete = AthleteSerializer(read_only=True)
    athlete_id = serializers.PrimaryKeyRelatedField(
        source='athlete',
        queryset=Athlete.objects.all(),
        write_only=True
    )
    rank_order = serializers.PrimaryKeyRelatedField(
        queryset=RankAssignmentOrder.objects.all(),
        write_only=True
    )

    class Meta:
        model = AthleteRankAssignment
        fields = ['id', 'athlete', 'athlete_id', 'rank_order', 'assigned_rank', 'assignment_date']


class RankAssignmentOrderSerializer(serializers.ModelSerializer):
    athletes = AthleteRankAssignmentSerializer(
        source='athleterankassignment_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = RankAssignmentOrder
        fields = ['id', 'order_number', 'order_date', 'document', 'athletes']
# -----------------------------
# Statistics
# -----------------------------
class StatisticsSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        source='department',
        queryset=Department.objects.all(),
        write_only=True
    )

    class Meta:
        model = Statistics
        fields = [
            'id',
            'department',
            'department_id',
            'quarter',
            'month',
            'year',
            'competition_count',
            'participant_count',
            'victories_count',
            'prize_count'
        ]
