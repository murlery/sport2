from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from sportSchool.models import *

User = get_user_model()

# -----------------------------
# User
# -----------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'middle_name', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Дополнительно', {'fields': ('role',)}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'last_name', 'first_name', 'middle_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'middle_name', 'email')
    ordering = ('username',)

# -----------------------------
# Department
# -----------------------------
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# -----------------------------
# Coach
# -----------------------------
@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ("user", "department")
    list_filter = ("department",)
    search_fields = ("user__username", "user__first_name", "user__last_name")

# -----------------------------
# Group
# -----------------------------
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'level', 'coach')
    list_filter = ('department', 'level')
    search_fields = ('name',)

# -----------------------------
# Athlete
# -----------------------------
@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'group', 'birth_date', 'gender')
    list_filter = ('group__department', 'gender')
    search_fields = ('last_name', 'first_name', 'middle_name')

# -----------------------------
# TrainingType
# -----------------------------
@admin.register(TrainingType)
class TrainingTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# -----------------------------
# TrainingPlan
# -----------------------------
@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = ('group', 'date', 'total_hours')
    list_filter = ('group__department', 'date')
    search_fields = ('group__name',)

# -----------------------------
# TrainingHour
# -----------------------------
@admin.register(TrainingHour)
class TrainingHourAdmin(admin.ModelAdmin):
    list_display = ('training_plan', 'training_type', 'hours')
    list_filter = ('training_plan__group', 'training_type')
    search_fields = ('training_plan__group__name', 'training_type__name')

# -----------------------------
# Attendance
# -----------------------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'training_plan', 'status', 'absence_reason')
    list_filter = ('training_plan__group', 'training_plan__date', 'status')
    search_fields = ('athlete__last_name', 'athlete__first_name')

# -----------------------------
# Competition
# -----------------------------
@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'level', 'coach')
    list_filter = ('level', 'date')
    search_fields = ('name', 'location')

# -----------------------------
# CompetitionResult
# -----------------------------
@admin.register(CompetitionResult)
class CompetitionResultAdmin(admin.ModelAdmin):
    list_display = ('competition', 'athlete', 'coach', 'place', 'weight_category', 'is_participant')
    list_filter = ('competition__level', 'coach')
    search_fields = ('athlete__last_name', 'athlete__first_name')

# -----------------------------
# AdministrativeDoc
# -----------------------------
@admin.register(AdministrativeDoc)
class AdministrativeDocAdmin(admin.ModelAdmin):
    list_display = ('doc_type', 'created_by', 'created_at', 'file_path')
    list_filter = ('created_at',)
    search_fields = ('doc_type',)

# -----------------------------
# RankAssignmentOrder & AthleteRankAssignment
# -----------------------------
class AthleteRankAssignmentInline(admin.TabularInline):
    model = AthleteRankAssignment
    extra = 1
    fields = ('athlete', 'assigned_rank', 'assignment_date')

@admin.register(RankAssignmentOrder)
class RankAssignmentOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'order_date')
    
    search_fields = ('order_number',)
    inlines = [AthleteRankAssignmentInline]

@admin.register(AthleteRankAssignment)
class AthleteRankAssignmentAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'rank_order', 'assigned_rank', 'assignment_date')
    list_filter = ('rank_order',)
    search_fields = ('athlete__last_name', 'athlete__first_name')

# -----------------------------
# Statistics
# -----------------------------
@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('department', 'quarter', 'month', 'year', 'competition_count', 'participant_count', 'victories_count', 'prize_count')
    list_filter = ('department', 'quarter', 'month', 'year')
