import json
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class User(AbstractUser):
    """Extended user model with role field."""

    class Role(models.TextChoices):
        STUDENT = 'student', _('Студент')
        TEACHER = 'teacher', _('Преподаватель')

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name='Роль',
    )
    patronymic = models.CharField(
        max_length=150, blank=True, verbose_name='Отчество'
    )
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, verbose_name='Аватар'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_full_name(self):
        full = super().get_full_name()
        if self.patronymic:
            full = f'{self.last_name} {self.first_name} {self.patronymic}'.strip()
        return full or self.username


class Module(models.Model):
    """Educational module - top level of course structure."""

    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    icon = models.CharField(
        max_length=50,
        default='bi-cpu',
        verbose_name='Иконка (Bootstrap Icons)',
    )
    order_number = models.PositiveIntegerField(
        default=0, verbose_name='Порядковый номер', db_index=True
    )

    class Meta:
        ordering = ['order_number']
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'

    def __str__(self):
        return f'Модуль {self.order_number}. {self.title}'

    def get_absolute_url(self):
        return reverse('module_detail', args=[self.pk])

    def section_count(self):
        return self.sections.count()

    def total_topics(self):
        return sum(s.topics.count() for s in self.sections.all())

    def completed_topics_for(self, user):
        if not user.is_authenticated:
            return 0
        topic_ids = Topic.objects.filter(
            section__module=self
        ).values_list('id', flat=True)
        return UserProgress.objects.filter(
            user=user, topic_id__in=topic_ids, is_completed=True
        ).count()


class Section(models.Model):
    """Section within a module."""

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='Модуль',
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    order_number = models.PositiveIntegerField(
        default=0, verbose_name='Порядковый номер', db_index=True
    )

    class Meta:
        ordering = ['order_number']
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('section_detail', args=[self.pk])

    def topic_count(self):
        return self.topics.count()


class Topic(models.Model):
    """Learning topic - the actual content page."""

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='topics',
        verbose_name='Раздел',
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    theoretical_content = models.TextField(
        blank=True, verbose_name='Теоретический материал'
    )
    reading_time = models.PositiveIntegerField(
        default=10,
        help_text='Время чтения в минутах',
        verbose_name='Время чтения (мин)',
    )
    order_number = models.PositiveIntegerField(
        default=0, verbose_name='Порядковый номер', db_index=True
    )

    class Meta:
        ordering = ['order_number']
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('topic_detail', args=[self.pk])

    def prev_topic(self):
        """Get the previous topic in course sequence."""
        all_topics = Topic.objects.filter(
            section__module=self.section.module
        ).select_related('section').order_by(
            'section__order_number', 'order_number'
        )
        topics_list = list(all_topics)
        for i, t in enumerate(topics_list):
            if t.pk == self.pk and i > 0:
                return topics_list[i - 1]
        return None

    def next_topic(self):
        """Get the next topic in course sequence."""
        all_topics = Topic.objects.filter(
            section__module=self.section.module
        ).select_related('section').order_by(
            'section__order_number', 'order_number'
        )
        topics_list = list(all_topics)
        for i, t in enumerate(topics_list):
            if t.pk == self.pk and i < len(topics_list) - 1:
                return topics_list[i + 1]
        return None


class InteractiveElement(models.Model):
    """Interactive element linked to a topic."""

    class ElementType(models.TextChoices):
        SIMULATOR = 'simulator', _('Симулятор')
        ANIMATION = 'animation', _('Анимация')
        THREE_D = '3d', _('3D-модель')

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='interactive_elements',
        verbose_name='Тема',
    )
    element_type = models.CharField(
        max_length=20,
        choices=ElementType.choices,
        verbose_name='Тип элемента',
    )
    title = models.CharField(max_length=255, blank=True, verbose_name='Название')
    url = models.URLField(blank=True, verbose_name='URL (внешний/внутренний)')
    configurations = models.JSONField(
        default=dict, blank=True, verbose_name='Конфигурация'
    )

    class Meta:
        verbose_name = 'Интерактивный элемент'
        verbose_name_plural = 'Интерактивные элементы'

    def __str__(self):
        return f'{self.get_element_type_display()}: {self.title or self.topic.title}'


class Assignment(models.Model):
    """Assignment / test question linked to a topic."""

    class TaskType(models.TextChoices):
        TEST = 'test', _('Тест')
        TASK = 'task', _('Задача')
        PRACTICAL = 'practical', _('Практическое задание')

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Тема',
    )
    task_text = models.TextField(verbose_name='Текст задания')
    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.TEST,
        verbose_name='Тип задания',
    )
    correct_answer = models.TextField(
        blank=True, verbose_name='Правильный ответ'
    )
    max_score = models.PositiveIntegerField(
        default=10, verbose_name='Максимальный балл'
    )
    # For multiple choice - JSON list of options
    options = models.JSONField(
        default=list, blank=True, verbose_name='Варианты ответов (JSON)'
    )

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'

    def __str__(self):
        return f'{self.task_type}: {self.task_text[:50]}...'


class AssignmentResult(models.Model):
    """Student's result for an assignment."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignment_results',
        verbose_name='Пользователь',
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Задание',
    )
    user_answer = models.TextField(blank=True, verbose_name='Ответ пользователя')
    is_correct = models.BooleanField(default=False, verbose_name='Верно')
    score = models.PositiveIntegerField(default=0, verbose_name='Баллы')
    completed_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата выполнения'
    )

    class Meta:
        verbose_name = 'Результат задания'
        verbose_name_plural = 'Результаты заданий'
        ordering = ['-completed_at']

    def __str__(self):
        return f'{self.user.username} - {self.assignment.task_text[:30]}... - {"✓" if self.is_correct else "✗"}'


class CalendarEvent(models.Model):
    """Admin-managed calendar event for the course calendar."""

    title = models.CharField(max_length=255, verbose_name='Название события')
    description = models.TextField(blank=True, verbose_name='Описание')
    date = models.DateField(verbose_name='Дата')
    module = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='calendar_events',
        verbose_name='Связанный модуль',
    )
    color = models.CharField(
        max_length=20, default='accent',
        verbose_name='Цвет (accent/success/danger/warning/info/primary)',
    )
    is_important = models.BooleanField(default=False, verbose_name='Важное событие')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Событие календаря'
        verbose_name_plural = 'События календаря'
        ordering = ['date', 'title']

    def __str__(self):
        return f'{self.date}: {self.title}'


class UserProgress(models.Model):
    """Track user's progress through topics."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name='Пользователь',
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name='Тема',
    )
    is_completed = models.BooleanField(default=False, verbose_name='Завершено')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Прогресс пользователя'
        verbose_name_plural = 'Прогресс пользователей'
        unique_together = ['user', 'topic']

    def __str__(self):
        return f'{self.user.username} - {self.topic.title}: {"✓" if self.is_completed else "○"}'
