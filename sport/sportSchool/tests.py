# sportSchool/tests.py
from django.test import TestCase
from django.core import mail
from sportSchool.models import User, Coach, Department, Competition


class EmailNotificationTest(TestCase):
    
    def setUp(self):
        # Создаем отделение
        self.department = Department.objects.create(name="Спортивная школа")
        
        # Создаем методиста с email
        self.methodist = User.objects.create_user(
            username='methodist',
            email='methodist@test.ru',
            password='123',
            role='methodist'
        )
        
        # Создаем тренера с email
        self.coach_user = User.objects.create_user(
            username='coach',
            email='coach@test.ru',
            password='123',
            role='coach'
        )
        self.coach = Coach.objects.create(
            user=self.coach_user,
            department=self.department
        )
        
        # Создаем отчет (черновик)
        self.report = Competition.objects.create(
            name="Чемпионат города",
            date="2024-12-01",
            location="Дворец спорта",
            level="Городской",
            coach=self.coach,
            status='draft'
        )
        
        # Очищаем исходящие письма
        mail.outbox = []
    
    def test_email_to_methodist_when_submitted(self):
        """Письмо методисту при отправке отчета"""
        self.report.status = 'submitted'
        self.report.save()
        
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('methodist@test.ru', email.to)
        self.assertIn('Новый отчет', email.subject)
    
    def test_email_to_coach_when_approved(self):
        """Письмо тренеру при утверждении отчета"""
        # Сначала отправляем отчет
        self.report.status = 'submitted'
        self.report.save()
        mail.outbox = []  # Очищаем
        
        # Методист утверждает
        self.report.status = 'approved'
        self.report.review_comment = "Отличный отчет!"
        self.report.save()
        
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('coach@test.ru', email.to)
        self.assertIn('утвержден', email.subject)
    
    def test_email_to_coach_when_returned(self):
        """Письмо тренеру при отправке на доработку"""
        # Сначала отправляем отчет
        self.report.status = 'submitted'
        self.report.save()
        mail.outbox = []  # Очищаем
        
        # Методист отправляет на доработку
        self.report.status = 'returned'
        self.report.review_comment = "Нужно добавить протокол"
        self.report.save()
        
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('coach@test.ru', email.to)
        self.assertIn('доработку', email.subject)
        self.assertIn('Нужно добавить протокол', email.body)
    
    def test_no_email_when_status_unchanged(self):
        """Нет письма при изменении других полей"""
        self.report.name = "Новое название"
        self.report.save()
        
        self.assertEqual(len(mail.outbox), 0)