from django.shortcuts import render

# Create your views here.
# sportSchool/views.py (добавьте в конец файла)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import Coach, TrainingPlan


@api_view(['POST'])
def notify_all_coaches(request):
    """Отправка напоминания всем тренерам без плана"""
    try:
        month = request.data.get('month')
        year = request.data.get('year')
        department_id = request.data.get('department_id')
        
        print(f"Получены данные: month={month}, year={year}, department_id={department_id}")
        
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
        
        print(f"Найдено тренеров: {coaches.count()}")
        
        # Находим тренеров без плана
        coaches_without_plan = []
        skipped_coaches = []
        
        for coach in coaches:
            # Проверяем email
            if not coach.user.email:
                skipped_coaches.append(f"{coach.user.last_name} {coach.user.first_name} (нет email)")
                continue
            
            # Проверяем есть ли у тренера группы
            groups = coach.groups.all()
            if not groups.exists():
                skipped_coaches.append(f"{coach.user.last_name} {coach.user.first_name} (нет групп)")
                continue
            
            # Проверяем есть ли план
            has_plan = TrainingPlan.objects.filter(
                group__coach=coach,
                date__year=year,
                date__month=month
            ).exists()
            
            if not has_plan:
                coaches_without_plan.append(coach)
        
        print(f"Тренеров без плана: {len(coaches_without_plan)}")
        
        if not coaches_without_plan:
            return Response({
                'message': 'Все тренеры уже сформировали планы',
                'sent': 0,
                'total': 0,
                'skipped': skipped_coaches
            }, status=status.HTTP_200_OK)
        
        # Отправляем уведомления
        success_count = 0
        month_names = {
            1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
            5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
            9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'
        }
        month_name = month_names.get(month, str(month))
        
        for coach in coaches_without_plan:
            try:
                subject = f"Напоминание: сформируйте тренировочный план на {month_name}"
                message = f"""
Здравствуйте, {coach.user.last_name} {coach.user.first_name}!

У вас отсутствует тренировочный план на {month_name} {year} года.

Пожалуйста, сформируйте план в системе.

---
С уважением,
Методист
                """
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[coach.user.email],
                    fail_silently=False,
                )
                success_count += 1
                print(f"✅ Уведомление отправлено {coach.user.email}")
            except Exception as e:
                print(f"❌ Ошибка отправки {coach.user.email}: {e}")
        
        return Response({
            'message': f'Отправлено {success_count} из {len(coaches_without_plan)} уведомлений',
            'sent': success_count,
            'total': len(coaches_without_plan),
            'skipped': skipped_coaches
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def notify_single_coach(request):
    """Отправка напоминания одному тренеру"""
    try:
        coach_id = request.data.get('coach_id')
        month = request.data.get('month')
        year = request.data.get('year')
        
        if not coach_id or not month or not year:
            return Response(
                {'error': 'Необходимо указать coach_id, month и year'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        coach = Coach.objects.get(id=coach_id)
        
        if not coach.user.email:
            return Response(
                {'error': 'У тренера нет email адреса'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        month_names = {
            1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
            5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
            9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'
        }
        month_name = month_names.get(int(month), str(month))
        
        subject = f"Напоминание: сформируйте тренировочный план на {month_name}"
        message = f"""
Здравствуйте, {coach.user.last_name} {coach.user.first_name}!

У вас отсутствует тренировочный план на {month_name} {year} года.

Пожалуйста, сформируйте план в системе.

---
С уважением,
Методист
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[coach.user.email],
            fail_silently=False,
        )
        
        return Response({
            'message': f'Уведомление отправлено тренеру {coach.user.last_name} {coach.user.first_name}'
        }, status=status.HTTP_200_OK)
        
    except Coach.DoesNotExist:
        return Response(
            {'error': 'Тренер не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Ошибка: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )