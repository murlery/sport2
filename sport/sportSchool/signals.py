# sportSchool/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Competition, User


@receiver(pre_save, sender=Competition)
def track_old_status(sender, instance, **kwargs):
    """
    Сохраняем старый статус перед обновлением
    """
    if instance.pk:
        instance._old_status = Competition.objects.get(pk=instance.pk).status
    else:
        instance._old_status = None


@receiver(post_save, sender=Competition)
def send_report_notification(sender, instance, **kwargs):
    """
    Сигнал срабатывает после сохранения отчета
    """
    # Для новых объектов не отправляем
    if kwargs.get('created', False):
        return
    
    # Получаем старый статус
    old_status = getattr(instance, '_old_status', None)
    
    # Если статус не изменился - не отправляем
    if old_status == instance.status:
        return
    
    # ===== 1. Отправка методисту (когда статус стал "submitted") =====
    if instance.status == 'submitted':
        # Находим всех методистов с email
        methodists = User.objects.filter(role='methodist').exclude(email='')
        
        if methodists.exists():
            # Получаем данные тренера
            coach = instance.coach
            coach_name = f"{coach.user.last_name} {coach.user.first_name}"
            department_name = coach.department.name if coach.department else "Не указано"
            
            # Формируем письмо
            subject = f"Новый отчет от {department_name}"
            
            message = f"""
{department_name}
Тренер {coach_name} отправил вам отчет по соревнованиям "{instance.name}"

Дата: {instance.date}
Место: {instance.location}
Уровень: {instance.level}

Для проверки отчета войдите в систему.
            """
            
            # Список email методистов
            emails = list(methodists.values_list('email', flat=True))
            
            # Отправляем письмо
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=emails,
                    fail_silently=False,
                )
                print(f"✅ Уведомление отправлено методистам: {emails}")
            except Exception as e:
                print(f"❌ Ошибка отправки методистам: {e}")
    
    # ===== 2. Отправка тренеру (когда статус стал "approved" или "returned") =====
    elif instance.status in ['approved', 'returned']:
        # Получаем данные тренера
        coach = instance.coach
        if not coach or not coach.user.email:
            print(f"❌ У тренера нет email")
            return
        
        coach_email = coach.user.email
        coach_name = f"{coach.user.last_name} {coach.user.first_name}"
        department_name = coach.department.name if coach.department else "Не указано"
        
        # Формируем письмо в зависимости от статуса
        if instance.status == 'approved':
            subject = f"✅ Ваш отчет утвержден - {instance.name}"
            
            message = f"""
Здравствуйте, {coach_name}!

Ваш отчет по соревнованиям "{instance.name}" ПРОШЕЛ проверку и УТВЕРЖДЕН методистом.

📋 Детали отчета:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 Название: {instance.name}
📅 Дата проведения: {instance.date}
📍 Место проведения: {instance.location}
🎯 Уровень: {instance.level}
🏢 Отделение: {department_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Статус: УТВЕРЖДЕН ✅

Спасибо за качественно подготовленный отчет!

---
С уважением,
Методист спортивной школы
Это сообщение отправлено автоматически, пожалуйста, не отвечайте на него.
            """
        
        else:  # status == 'returned'
            subject = f"⚠️ Ваш отчет отправлен на доработку - {instance.name}"
            comment = instance.review_comment or "Без комментария"
            
            message = f"""
Здравствуйте, {coach_name}!

Ваш отчет по соревнованиям "{instance.name}" направлен на ДОРАБОТКУ.

📋 Детали отчета:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 Название: {instance.name}
📅 Дата проведения: {instance.date}
📍 Место проведения: {instance.location}
🎯 Уровень: {instance.level}
🏢 Отделение: {department_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 Комментарий методиста:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{comment}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Пожалуйста, исправьте замечания и отправьте отчет повторно.

---
С уважением,
Методист спортивной школы
Это сообщение отправлено автоматически, пожалуйста, не отвечайте на него.
            """
        
        # Отправляем письмо тренеру
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[coach_email],
                fail_silently=False,
            )
            print(f"✅ Уведомление отправлено тренеру {coach_name} на {coach_email}")
        except Exception as e:
            print(f"❌ Ошибка отправки тренеру {coach_name}: {e}")