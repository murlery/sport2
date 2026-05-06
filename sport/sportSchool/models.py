from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# -----------------------------
# Отделение
# -----------------------------
class Department(models.Model):
    name = models.CharField("Название отделения", max_length=100)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Отделение"
        verbose_name_plural = "Отделения"

    def __str__(self):
        return self.name

from django.contrib.auth.models import AbstractUser

# -----------------------------
# Кастомная модель пользователя
# -----------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('coach', 'Тренер'),
        ('manager', 'Руководитель'),
        ('methodist', 'Методист'),
    ]
    middle_name = models.CharField("Отчество", max_length=50, blank=True)
    role = models.CharField("Роль", max_length=20, choices=ROLE_CHOICES)
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


# -----------------------------
# Тренер
# -----------------------------
class Coach(models.Model):
    user = models.OneToOneField(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    department = models.ForeignKey(Department, verbose_name="Отделение", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Тренер"
        verbose_name_plural = "Тренеры"

    def __str__(self):
        if self.user:
            return f"{self.user.last_name} {self.user.first_name} {self.user.middle_name} ({self.department.name})"
        return f"Coach #{self.id}"


class Group(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Начальная подготовка'),
        ('training', 'Учебно-тренировочный'),
        ('improvement', 'Совершенствование спортивного мастерства'),
        ('high', 'Высшее спортивное мастерство'),
    ]

    name = models.CharField("Название группы", max_length=100)
    department = models.ForeignKey(Department, verbose_name="Отделение", on_delete=models.CASCADE)
    
    level = models.CharField(
        "Уровень группы",
        max_length=20,
        choices=LEVEL_CHOICES,
        default='beginner'  # можно задать значение по умолчанию
    )
    coach = models.ForeignKey(
        Coach,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Тренер группы",
        related_name="groups"
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.name
# -----------------------------
# Спортсмен
# -----------------------------
class Athlete(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    last_name = models.CharField("Фамилия", max_length=50)
    first_name = models.CharField("Имя", max_length=50)
    middle_name = models.CharField("Отчество", max_length=50, blank=True)
    group = models.ForeignKey(Group, verbose_name="Группа", on_delete=models.CASCADE, related_name="athletes")
    
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="Пол")

    class Meta:
        verbose_name = "Спортсмен"
        verbose_name_plural = "Спортсмены"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сохраняем текущий объект
        
        # После сохранения обновляем last_rank у спортсмена
        latest_assignment = AthleteRankAssignment.objects.filter(
            athlete=self
        ).order_by('-assignment_date', '-id').first()  # берём последнюю по дате
        if latest_assignment:
            self.athlete.last_rank = latest_assignment.assigned_rank
            self.athlete.save(update_fields=['last_rank'])



# -----------------------------
# Вид тренировки
# -----------------------------
class TrainingType(models.Model):
    name = models.CharField("Название вида тренировки", max_length=100)

    class Meta:
        verbose_name = "Вид тренировки"
        verbose_name_plural = "Виды тренировок"

    def __str__(self):
        return self.name
    
#тренировочный план
class TrainingPlan(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='training_plans')
    date = models.DateField()
    total_hours = models.FloatField()

    class Meta:
        verbose_name = "Тренировочный план"
        verbose_name_plural = "Тренировочные планы"
        unique_together = ("group", "date")
# -----------------------------
# Тренировочные часы (обновленная структура)
# -----------------------------
class TrainingHour(models.Model):
    training_plan = models.ForeignKey(
        TrainingPlan,
        on_delete=models.CASCADE,
        related_name="training_hours"
    )
    training_type = models.ForeignKey(TrainingType, on_delete=models.CASCADE)
    hours = models.FloatField()

    class Meta:
        verbose_name = "Тренировочные часы"
        verbose_name_plural = "Тренировочные часы"
        unique_together = ("training_plan", "training_type")


# -----------------------------
# Посещаемость
# -----------------------------
class Attendance(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    training_plan = models.ForeignKey(
        TrainingPlan,
        on_delete=models.CASCADE,
        related_name="attendance"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('present', 'Присутствовал'),
            ('absent', 'Отсутствовал')
        ]
    )
    absence_reason = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Посещаемость"
        verbose_name_plural = "Посещаемость"
        unique_together = ("athlete", "training_plan")


class Competition(models.Model):
    name = models.CharField("Название соревнования", max_length=100)
    date = models.DateField("Дата проведения")
    location = models.CharField("Место проведения", max_length=100)
    level = models.CharField("Уровень", max_length=50)
    coach = models.ForeignKey('Coach', verbose_name="Тренер", on_delete=models.CASCADE, null=True, blank=True, related_name='competitions')
    protocol = models.FileField("Протокол соревнований", upload_to='protocols/', blank=True, null=True)
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=[
            ('draft', 'Черновик'),
            ('submitted', 'Отправлен'),
            ('approved', 'Утвержден'),
            ('returned', 'На доработку'),
        ],
        default='draft'
    )
    review_comment = models.TextField("Комментарий методиста", blank=True)

    class Meta:
        verbose_name = "Соревнование"
        verbose_name_plural = "Соревнования"

    def __str__(self):
        return f"{self.name} ({self.date})"

# -----------------------------
# Результаты соревнований
# -----------------------------
class CompetitionResult(models.Model):
    competition = models.ForeignKey(Competition, verbose_name="Соревнование", on_delete=models.CASCADE)
    athlete = models.ForeignKey(Athlete, verbose_name="Спортсмен", on_delete=models.CASCADE)
    coach = models.ForeignKey(Coach, verbose_name="Тренер", on_delete=models.CASCADE)
    place = models.IntegerField("Место", null=True, blank=True)
   
    weight_category = models.CharField("Весовая категория", max_length=50, blank=True)
    is_participant = models.BooleanField("Участник без места", default=False)

    class Meta:
        verbose_name = "Результат соревнования"
        verbose_name_plural = "Результаты соревнований"

    def __str__(self):
        return f"{self.athlete} - {self.competition} - {self.place}"


# -----------------------------
# Приказ о присвоении разряда (Many-to-Many связь)
# -----------------------------
class RankAssignmentOrder(models.Model):
    order_number = models.CharField("Номер приказа", max_length=50)
    order_date = models.DateField("Дата приказа")
    document = models.FileField("Файл приказа", upload_to='rank_orders/', blank=True, null=True)
   
    
    # Связь со спортсменами через промежуточную модель
    athletes = models.ManyToManyField(
        Athlete,
        through='AthleteRankAssignment',
        verbose_name="Спортсмены",
        related_name='rank_orders'
    )

    class Meta:
        verbose_name = "Приказ о присвоении разряда"
        verbose_name_plural = "Приказы о присвоении разрядов"

    def __str__(self):
        return f"Приказ {self.order_number} от {self.order_date}"


# -----------------------------
# Промежуточная модель для связи спортсмен-приказ
# -----------------------------
class AthleteRankAssignment(models.Model):
    athlete = models.ForeignKey(
    Athlete,
    verbose_name="Спортсмен",
    on_delete=models.CASCADE,
    related_name='rank_assignments'
)
    rank_order = models.ForeignKey(RankAssignmentOrder, verbose_name="Приказ", on_delete=models.CASCADE)
    assigned_rank = models.CharField("Присвоенный разряд", max_length=50)
    assignment_date = models.DateField("Дата присвоения", null=True, blank=True)
    
    class Meta:
        verbose_name = "Присвоение разряда спортсмену"
        verbose_name_plural = "Присвоения разрядов спортсменам"
        unique_together = ['athlete', 'rank_order']

    def __str__(self):
        return f"{self.athlete} - {self.assigned_rank} ({self.assignment_date})"


# -----------------------------
# Административные документы
# -----------------------------
class AdministrativeDoc(models.Model):
    doc_type = models.CharField("Тип документа", max_length=100)
    created_by = models.ForeignKey(User, verbose_name="Создано пользователем", on_delete=models.CASCADE)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    file_path = models.FileField("Файл", upload_to='docs/')

    class Meta:
        verbose_name = "Административный документ"
        verbose_name_plural = "Административные документы"

    def __str__(self):
        return f"{self.doc_type} ({self.created_at})"


# -----------------------------
# Статистика
# -----------------------------
class Statistics(models.Model):
    department = models.ForeignKey(Department, verbose_name="Отделение", on_delete=models.CASCADE)
    quarter = models.IntegerField("Квартал")
    month = models.IntegerField("Месяц")
    year = models.IntegerField("Год")
    competition_count = models.IntegerField("Количество соревнований", default=0)
    participant_count = models.IntegerField("Количество участников", default=0)
    victories_count = models.IntegerField("Количество побед", default=0)
    prize_count = models.IntegerField("Количество призовых мест", default=0)

    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"
        unique_together = ['department', 'month', 'year']

    def __str__(self):
        return f"Статистика {self.department} - {self.month}/{self.year}"


