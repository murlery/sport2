from rest_framework import viewsets, permissions, status 
from django.contrib.auth import get_user_model
from django.db import transaction  # <-- Добавьте эту строку
# Models
# -----------------------------
from sportSchool.models import (
    User, Department, Coach, Group, Athlete, Attendance,
    TrainingType, TrainingPlan, TrainingHour,
    Competition, CompetitionResult,
    AdministrativeDoc, RankAssignmentOrder, AthleteRankAssignment,
    Statistics
)

# -----------------------------
# Serializers
# -----------------------------
from sportSchool.serializers import (
    UserSerializer, DepartmentSerializer, CoachSerializer, GroupSerializer,
    AthleteSerializer, AttendanceSerializer, TrainingTypeSerializer,
    TrainingPlanSerializer, TrainingHourSerializer,
    CompetitionSerializer, CompetitionResultSerializer,
    AdministrativeDocSerializer,
    RankAssignmentOrderSerializer, AthleteRankAssignmentSerializer,
    StatisticsSerializer
)

from rest_framework.views import APIView 
from rest_framework.response import Response 
from django.views.decorators.csrf import ensure_csrf_cookie 
from django.utils.decorators import method_decorator 
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
User = get_user_model()


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
import calendar
from datetime import date
import random
from sportSchool.models import TrainingPlan, TrainingHour, TrainingType, Group
from sportSchool.api import TrainingPlanSerializer

import os, mimetypes, traceback
from django.http import FileResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
import traceback

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import Coach
from .signals import send_training_plan_reminder

# Добавьте это в начало файла, если еще нет
logger = logging.getLogger(__name__)
# -----------------------------
# Users (сотрудники)
# -----------------------------
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = User.objects.all()
        role = self.request.query_params.get("role")

        if role:
            qs = qs.filter(role=role)

        return qs


# -----------------------------
# Авторизация
# -----------------------------


class LoginView(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Получаем или создаем токен
        token, created = Token.objects.get_or_create(user=user)
        
        # Сериализуем пользователя
        user_serializer = UserSerializer(user)
        
        return Response({
            'token': token.key,
            'user': user_serializer.data
        })

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Удаляем токен пользователя
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass  # Если токена нет - ничего не делаем
        
        return Response({"detail": "ok"})
    
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# -----------------------------
# Department
# -----------------------------
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

# -----------------------------
# Coach
# -----------------------------
class CoachViewSet(viewsets.ModelViewSet):
    queryset = Coach.objects.all()
    serializer_class = CoachSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Coach.objects.all()
        user = self.request.user
        if getattr(user, "role", None) == "coach":
            return qs.filter(user=user)
        department_id = self.request.query_params.get("department")
        if department_id:
            qs = qs.filter(department_id=department_id)
        user_id = self.request.query_params.get("user")
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

# -----------------------------
# Group
# -----------------------------
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Group.objects.all()
        user = self.request.user
        if getattr(user, "role", None) == "coach":
            coach = Coach.objects.filter(user=user).first()
            if coach:
                qs = qs.filter(coach=coach)
            else:
                qs = qs.none()
        else:
            department_id = self.request.query_params.get("department")
            coach_id = self.request.query_params.get("coach")
            if department_id:
                qs = qs.filter(department_id=department_id)
            if coach_id:
                qs = qs.filter(coach_id=coach_id)
        return qs

# -----------------------------
# Athlete
# -----------------------------
class AthleteViewSet(viewsets.ModelViewSet):
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Athlete.objects.all()
        user = self.request.user
        if getattr(user, "role", None) == "coach":
            coach = Coach.objects.filter(user=user).first()
            if coach:
                qs = qs.filter(group__coach=coach)
            else:
                qs = qs.none()
        else:
            department = self.request.query_params.get("department")
            group_id = self.request.query_params.get("group")
            coach_id = self.request.query_params.get("coach")
            if department:
                qs = qs.filter(group__department_id=department)
            if group_id:
                qs = qs.filter(group_id=group_id)
            if coach_id:
                qs = qs.filter(group__coach_id=coach_id)
        return qs

# -----------------------------
# TrainingType
# -----------------------------
class TrainingTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainingType.objects.all()
    serializer_class = TrainingTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

# -----------------------------
# TrainingPlan & TrainingHour
# -----------------------------


class TrainingHourViewSet(viewsets.ModelViewSet):
    queryset = TrainingHour.objects.all()
    serializer_class = TrainingHourSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = TrainingHour.objects.all()
        training_plan_id = self.request.query_params.get("training_plan")
        if training_plan_id:
            qs = qs.filter(training_plan_id=training_plan_id)
        return qs

# -----------------------------
# Attendance
# -----------------------------
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Attendance.objects.all()
        training_plan_id = self.request.query_params.get("training_plan")
        athlete_id = self.request.query_params.get("athlete")
        if training_plan_id:
            qs = qs.filter(training_plan_id=training_plan_id)
        if athlete_id:
            qs = qs.filter(athlete_id=athlete_id)
        return qs

# -----------------------------
# Competition & CompetitionResult
# -----------------------------
from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
import os, mimetypes, traceback
from django.conf import settings

class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='download-protocol')
    def download_protocol(self, request, pk=None):
        """
        Скачивание протокола соревнования
        """
        try:
            competition = self.get_object()

            if not competition.protocol:
                return Response({"error": "Протокол не прикреплен"}, status=status.HTTP_404_NOT_FOUND)

            file_path = os.path.join(settings.MEDIA_ROOT, competition.protocol.name)

            if not os.path.exists(file_path):
                return Response({"error": "Файл не найден на сервере"}, status=status.HTTP_404_NOT_FOUND)

            # MIME-тип по реальному файлу
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

            file_handle = open(file_path, 'rb')
            response = FileResponse(file_handle, content_type=mime_type)
            filename = os.path.basename(file_path)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = os.path.getsize(file_path)

            return response

        except Exception as e:
            print(f"!!! EXCEPTION in download_protocol: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": f"Внутренняя ошибка сервера: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CompetitionResultViewSet(viewsets.ModelViewSet):
    queryset = CompetitionResult.objects.all()
    serializer_class = CompetitionResultSerializer
    permission_classes = [permissions.IsAuthenticated]

# -----------------------------
# AdministrativeDoc
# -----------------------------
class AdministrativeDocViewSet(viewsets.ModelViewSet):
    queryset = AdministrativeDoc.objects.all().order_by('-created_at')
    serializer_class = AdministrativeDocSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)



import os
import mimetypes
import traceback
from django.http import FileResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings

class RankAssignmentOrderViewSet(viewsets.ModelViewSet):
    queryset = RankAssignmentOrder.objects.all()
    serializer_class = RankAssignmentOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='download')
    def download_document(self, request, pk=None):
        try:
            order = self.get_object()

            if not order.document:
                return Response({"error": "Документ не прикреплен"}, status=status.HTTP_404_NOT_FOUND)

            file_path = os.path.join(settings.MEDIA_ROOT, order.document.name)

            if not os.path.exists(file_path):
                return Response({"error": "Файл не найден на сервере"}, status=status.HTTP_404_NOT_FOUND)

            # MIME-тип определяется автоматически по реальному файлу
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

            file_handle = open(file_path, 'rb')
            response = FileResponse(file_handle, content_type=mime_type)
            filename = os.path.basename(file_path)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = os.path.getsize(file_path)

            return response

        except Exception as e:
            print(f"!!! EXCEPTION in download_document: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": f"Внутренняя ошибка сервера: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AthleteRankAssignmentViewSet(viewsets.ModelViewSet):
    queryset = AthleteRankAssignment.objects.all()
    serializer_class = AthleteRankAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]


# -----------------------------
# Statistics
# -----------------------------
class StatisticsViewSet(viewsets.ModelViewSet):
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Statistics.objects.all()
        department_id = self.request.query_params.get("department")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")

        if department_id:
            qs = qs.filter(department_id=department_id)
        if month:
            qs = qs.filter(month=month)
        if year:
            qs = qs.filter(year=year)

        return qs







class TrainingPlanViewSet(viewsets.ModelViewSet):
    queryset = TrainingPlan.objects.all().prefetch_related("training_hours")
    serializer_class = TrainingPlanSerializer

    # -----------------------------
    # Фильтрация по группе и месяцу
    # -----------------------------
    def get_queryset(self):
        queryset = super().get_queryset()

        group_id = self.request.query_params.get("group_id")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")

        if group_id:
            queryset = queryset.filter(group_id=group_id)

        if month and year:
            queryset = queryset.filter(
                date__month=int(month),
                date__year=int(year)
            )

        return queryset.order_by("date")

    # -----------------------------
    # Генерация плана на месяц
    # -----------------------------
    @action(detail=False, methods=['post'], url_path='generate')
    @transaction.atomic
    def generate(self, request):
        data = request.data

        # --- 1. Валидация обязательных полей ---
        required_fields = ["group_id", "year", "month", "weekdays", "total_hours", "training_types"]
        for field in required_fields:
            if field not in data:
                return Response({"error": f"Отсутствует поле {field}"}, status=status.HTTP_400_BAD_REQUEST)

        group = get_object_or_404(Group, id=data["group_id"])
        year = int(data["year"])
        month = int(data["month"])
        weekdays = list(map(int, data["weekdays"]))
        total_hours = float(data["total_hours"])
        training_types_data = data["training_types"]

        if not training_types_data:
            return Response({"error": "Не указаны виды тренировок"}, status=status.HTTP_400_BAD_REQUEST)

        # --- Подготовка видов тренировок ---
        training_types = []
        sum_hours_requested = 0
        for item in training_types_data:
            if "id" not in item or "hours" not in item:
                return Response({"error": "Неверная структура training_types"}, status=status.HTTP_400_BAD_REQUEST)
            tt = get_object_or_404(TrainingType, id=item["id"])
            hours = float(item["hours"])
            training_types.append({"obj": tt, "hours": hours})
            sum_hours_requested += hours

        # --- Генерация дней месяца по выбранным дням недели ---
        _, days_in_month = calendar.monthrange(year, month)
        training_dates = [date(year, month, day) for day in range(1, days_in_month + 1)
                          if date(year, month, day).weekday() in weekdays]

        if not training_dates:
            return Response({"error": "Нет выбранных тренировочных дней в месяце"}, status=status.HTTP_400_BAD_REQUEST)

        # --- Валидация максимально возможных часов ---
        max_possible_hours = total_hours * len(training_dates)
        if sum_hours_requested > max_possible_hours + 0.01:
            return Response({
                "error": f"Сумма часов по видам ({sum_hours_requested}) превышает максимально возможные ({max_possible_hours}) "
                         f"для выбранного месяца с {len(training_dates)} тренировочными днями."
            }, status=status.HTTP_400_BAD_REQUEST)

        # --- Создаём структуры для распределения ---
        day_plans = {d: [] for d in training_dates}
        day_hours = {d: 0.0 for d in training_dates}

        # --- Разбиваем виды тренировок на 1-часовые слоты ---
        hour_slots = []
        for tt in training_types:
            # Разбиваем часы на 1-часовые единицы
            for _ in range(int(tt["hours"])):
                hour_slots.append(tt["obj"])

        random.shuffle(hour_slots)

        # --- Распределение часов по дням ---
        for tt_obj in hour_slots:
            random.shuffle(training_dates)  # перемешиваем дни для случайного распределения
            for d in training_dates:
                if day_hours[d] < total_hours:
                    existing = next((x for x in day_plans[d] if x["obj"].id == tt_obj.id), None)
                    if existing:
                        existing["hours"] += 1
                    else:
                        day_plans[d].append({"obj": tt_obj, "hours": 1})
                    day_hours[d] += 1
                    break  # распределили час, переходим к следующему

        # --- Создание планов в БД ---
        first_day = date(year, month, 1)
        last_day = date(year, month, days_in_month)
        TrainingPlan.objects.filter(group=group, date__range=(first_day, last_day)).delete()

        created_count = 0
        for d in training_dates:
            daily_trainings = day_plans[d]
            daily_total_hours = sum(t["hours"] for t in daily_trainings)
            plan = TrainingPlan.objects.create(group=group, date=d, total_hours=daily_total_hours)
            for t in daily_trainings:
                TrainingHour.objects.create(training_plan=plan, training_type=t["obj"], hours=t["hours"])
            created_count += 1

        return Response({
            "status": "ok",
            "message": f"Создано {created_count} тренировочных планов",
            "distribution": {
                str(d): [{"type": t["obj"].name, "hours": t["hours"]} for t in day_plans[d]]
                for d in training_dates
            },
            "total_requested_hours": sum_hours_requested,
            "max_possible_hours": max_possible_hours,
            "training_days_count": len(training_dates)
        }, status=status.HTTP_201_CREATED)



from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import Coach, TrainingPlan
from datetime import datetime

class CoachNotificationViewSet(viewsets.ViewSet):
    """
    ViewSet для отправки уведомлений тренерам
    """
    
    @action(detail=False, methods=['post'], url_path='notify-training-plan')
    def notify_training_plan(self, request):
        """
        Отправка напоминания одному тренеру
        Ожидает: {"coach_id": 1, "month": 10, "year": 2024}
        """
        coach_id = request.data.get('coach_id')
        month = request.data.get('month')
        year = request.data.get('year')
        
        if not coach_id or not month or not year:
            return Response(
                {'error': 'Необходимо указать coach_id, month и year'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coach = Coach.objects.get(id=coach_id)
        except Coach.DoesNotExist:
            return Response(
                {'error': 'Тренер не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Отправляем уведомление
        success = send_training_plan_reminder(coach, int(month), int(year))
        
        if success:
            return Response(
                {'message': f'Уведомление отправлено тренеру {coach.user.last_name} {coach.user.first_name}'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Не удалось отправить уведомление (возможно у тренера нет email)'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='notify-all-training-plan')
    def notify_all_training_plan(self, request):
        """
        Отправка напоминания ВСЕМ тренерам, у которых нет плана за указанный месяц
        Ожидает: {"month": 10, "year": 2024, "department_id": 1 (опционально), "coach_ids": [1,2,3] (опционально)}
        """
        month = request.data.get('month')
        year = request.data.get('year')
        department_id = request.data.get('department_id')  # опционально - фильтр по отделению
        coach_ids = request.data.get('coach_ids', [])  # опционально - конкретные тренеры
        
        if not month or not year:
            return Response(
                {'error': 'Необходимо указать month и year'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        month = int(month)
        year = int(year)
        
        # Получаем всех тренеров
        coaches = Coach.objects.all()
        
        # Фильтр по отделению
        if department_id:
            coaches = coaches.filter(department_id=department_id)
        
        # Фильтр по конкретным тренерам
        if coach_ids:
            coaches = coaches.filter(id__in=coach_ids)
        
        # Находим тренеров без плана за указанный месяц
        coaches_without_plan = []
        
        for coach in coaches:
            # Проверяем есть ли у тренера группы
            groups = coach.groups.all()
            if not groups.exists():
                # Если нет групп - считаем что план не нужен
                continue
            
            # Проверяем есть ли план хотя бы у одной группы тренера
            has_plan = TrainingPlan.objects.filter(
                group__coach=coach,
                date__year=year,
                date__month=month
            ).exists()
            
            if not has_plan:
                coaches_without_plan.append(coach)
        
        if not coaches_without_plan:
            return Response(
                {'message': 'Все тренеры уже сформировали планы на указанный месяц', 'sent': 0, 'total': 0},
                status=status.HTTP_200_OK
            )
        
        # Отправляем уведомления
        result = send_training_plan_reminder_to_all(coaches_without_plan, month, year)
        
        return Response(
            {
                'message': f'Уведомления отправлены: {result["success_count"]} из {result["total_count"]} тренеров',
                'sent': result['success_count'],
                'total': result['total_count'],
                'failed_coaches': result['failed_coaches']
            },
            status=status.HTTP_200_OK
        )