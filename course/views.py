import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Q, Sum
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import (
    Module, Section, Topic, InteractiveElement,
    Assignment, AssignmentResult, UserProgress, User, CalendarEvent,
)
from django import forms as django_forms
from django.contrib.auth.forms import UserCreationForm


# ============================================================
# Forms (merged from forms.py)
# ============================================================

class UserRegistrationForm(UserCreationForm):
    """Registration form with extended fields."""

    email = django_forms.EmailField(
        required=True,
        label='Электронная почта',
        widget=django_forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = django_forms.CharField(
        max_length=150, label='Имя',
        widget=django_forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = django_forms.CharField(
        max_length=150, label='Фамилия',
        widget=django_forms.TextInput(attrs={'class': 'form-control'})
    )
    patronymic = django_forms.CharField(
        max_length=150, required=False, label='Отчество',
        widget=django_forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'patronymic',
            'email', 'password1', 'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].label = 'Логин'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'


class LoginForm(django_forms.Form):
    """Login form."""

    username = django_forms.CharField(
        label='Логин',
        widget=django_forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Введите логин'
        })
    )
    password = django_forms.CharField(
        label='Пароль',
        widget=django_forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Введите пароль'
        })
    )


class AssignmentForm(django_forms.Form):
    """Form for submitting assignment answers."""

    answer = django_forms.CharField(
        label='Ваш ответ',
        widget=django_forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Введите ваш ответ...'
        }),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.assignment = kwargs.pop('assignment', None)
        super().__init__(*args, **kwargs)

        if self.assignment and self.assignment.options:
            # Multiple choice
            choices = []
            for i, opt in enumerate(self.assignment.options):
                if isinstance(opt, dict):
                    choices.append((str(i), opt.get('text', opt.get('value', ''))))
                else:
                    choices.append((str(i), str(opt)))

            self.fields['answer'] = django_forms.ChoiceField(
                choices=choices,
                label='Выберите ответ',
                widget=django_forms.RadioSelect(attrs={'class': 'form-check-input'}),
            )


# ============================================================
# Context processor (merged from context_processors.py)
# ============================================================

def course_context(request):
    """Provide global context for all templates."""
    modules = Module.objects.all().order_by('order_number')
    return {
        'all_modules': modules,
        'course_title': 'Микропроцессорные системы',
        'course_subtitle': 'Интерактивный курс по архитектуре и программированию микропроцессоров',
    }


# ============================================================
# Views
# ============================================================


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.STUDENT
            user.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def index(request):
    """Main page with course map."""
    modules = Module.objects.all().order_by('order_number')
    total_topics = Topic.objects.count()
    completed_topics = 0
    if request.user.is_authenticated:
        completed_topics = UserProgress.objects.filter(
            user=request.user, is_completed=True
        ).count()

    # Compute progress per module
    module_progress = []
    for mod in modules:
        mod_topics = Topic.objects.filter(section__module=mod).count()
        mod_done = 0
        if request.user.is_authenticated:
            mod_done = mod.completed_topics_for(request.user)
        module_progress.append({
            'module': mod,
            'total': mod_topics,
            'completed': mod_done,
            'percent': int((mod_done / mod_topics * 100)) if mod_topics > 0 else 0,
        })

    context = {
        'module_progress': module_progress,
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'overall_percent': int((completed_topics / total_topics * 100)) if total_topics > 0 else 0,
    }
    return render(request, 'index.html', context)


def topic_detail(request, topic_id):
    """Main learning interface - shows topic content with navigation."""
    topic = get_object_or_404(
        Topic.objects.select_related('section__module'),
        pk=topic_id
    )
    section = topic.section
    module = section.module

    # Get all sequential topics for this module
    all_topics = list(
        Topic.objects.filter(section__module=module)
        .select_related('section')
        .order_by('section__order_number', 'order_number')
    )

    prev_topic = topic.prev_topic()
    next_topic = topic.next_topic()

    # Interactive elements for this topic
    interactive_elements = topic.interactive_elements.all()

    # Track user visit (only for authenticated users)
    # Topic is NOT marked as completed here — completion only happens
    # after passing the module test (see module_test_view).
    if request.user.is_authenticated:
        UserProgress.objects.get_or_create(
            user=request.user,
            topic=topic,
        )

    # Build breadcrumbs
    breadcrumbs = [
        {'title': 'Главная', 'url': '/'},
        {'title': str(module), 'url': '#'},
        {'title': section.title, 'url': '#'},
        {'title': topic.title, 'url': ''},
    ]

    # Build sidebar tree data
    modules_data = Module.objects.all().order_by('order_number')
    sidebar_data = []
    for mod in modules_data:
        sections = mod.sections.all().order_by('order_number')
        sections_data = []
        for sec in sections:
            topics = sec.topics.all().order_by('order_number')
            topics_data = []
            for t in topics:
                completed = False
                if request.user.is_authenticated:
                    completed = UserProgress.objects.filter(
                        user=request.user, topic=t, is_completed=True
                    ).exists()
                topics_data.append({
                    'topic': t,
                    'completed': completed,
                    'active': t.pk == topic.pk,
                })
            sections_data.append({
                'section': sec,
                'topics': topics_data,
            })
        sidebar_data.append({
            'module': mod,
            'sections': sections_data,
        })

    # Build all topics list with progress for sequential nav
    all_topics_with_progress = []
    for t in all_topics:
        completed = False
        if request.user.is_authenticated:
            completed = UserProgress.objects.filter(
                user=request.user, topic=t, is_completed=True
            ).exists()
        all_topics_with_progress.append({
            'topic': t,
            'completed': completed,
            'active': t.pk == topic.pk,
        })

    context = {
        'topic': topic,
        'section': section,
        'module': module,
        'prev_topic': prev_topic,
        'next_topic': next_topic,
        'all_topics': all_topics_with_progress,
        'interactive_elements': interactive_elements,
        'breadcrumbs': breadcrumbs,
        'sidebar_data': sidebar_data,
    }
    return render(request, 'topic.html', context)


@login_required
def dashboard(request):
    """Student dashboard with progress and results."""
    user = request.user

    # Overall stats
    total_topics = Topic.objects.count()
    completed_topics = UserProgress.objects.filter(
        user=user, is_completed=True
    ).count()
    overall_percent = int((completed_topics / total_topics * 100)) if total_topics > 0 else 0

    # Per-module stats
    modules = Module.objects.all().order_by('order_number')
    module_stats = []
    for mod in modules:
        mod_topics = Topic.objects.filter(section__module=mod).count()
        mod_done = mod.completed_topics_for(user)
        mod_assignments = Assignment.objects.filter(topic__section__module=mod).count()
        mod_results = AssignmentResult.objects.filter(
            user=user, assignment__topic__section__module=mod
        ).count()
        module_stats.append({
            'module': mod,
            'total_topics': mod_topics,
            'completed_topics': mod_done,
            'percent': int((mod_done / mod_topics * 100)) if mod_topics > 0 else 0,
            'total_assignments': mod_assignments,
            'completed_assignments': mod_results,
        })

    # Recent results
    recent_results = AssignmentResult.objects.filter(
        user=user
    ).select_related('assignment__topic').order_by('-completed_at')[:20]

    # Summary scores
    total_score = AssignmentResult.objects.filter(user=user).aggregate(
        total=Sum('score')
    )['total'] or 0
    max_score = Assignment.objects.aggregate(
        total=Sum('max_score')
    )['total'] or 1

    context = {
        'overall_percent': overall_percent,
        'completed_topics': completed_topics,
        'total_topics': total_topics,
        'module_stats': module_stats,
        'recent_results': recent_results,
        'total_score': total_score,
        'max_score': max_score,
        'score_percent': int(total_score / max_score * 100),
    }
    return render(request, 'dashboard.html', context)


@login_required
@require_POST
def submit_assignment(request, assignment_id):
    """AJAX endpoint for submitting assignment answers."""
    assignment = get_object_or_404(Assignment, pk=assignment_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    user_answer = data.get('answer', '').strip()

    if not user_answer:
        return JsonResponse({'error': 'Ответ не может быть пустым'}, status=400)

    # Check answer (simple exact match for now)
    correct = user_answer.lower() == assignment.correct_answer.lower()

    # Calculate score
    score = assignment.max_score if correct else 0

    # If multiple choice, check index match
    if assignment.options and assignment.correct_answer.isdigit():
        correct_idx = int(assignment.correct_answer)
        options = assignment.options
        if isinstance(options, list) and correct_idx < len(options):
            correct_text = options[correct_idx]
            if isinstance(correct_text, dict):
                correct_text = correct_text.get('text', correct_text.get('value', ''))
            correct = user_answer.lower() == str(correct_idx) or user_answer.lower() == correct_text.lower()
            score = assignment.max_score if correct else 0

    # Save result
    result = AssignmentResult.objects.create(
        user=request.user,
        assignment=assignment,
        user_answer=user_answer,
        is_correct=correct,
        score=score,
    )

    return JsonResponse({
        'is_correct': correct,
        'score': score,
        'max_score': assignment.max_score,
        'correct_answer': assignment.correct_answer if not correct else None,
    })


@login_required
@require_POST
def toggle_topic_complete(request, topic_id):
    """Toggle topic completion status."""
    topic = get_object_or_404(Topic, pk=topic_id)
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        topic=topic,
    )
    progress.is_completed = not progress.is_completed
    progress.save()
    return JsonResponse({'is_completed': progress.is_completed})


# ---- Admin Dashboard Views ----

@staff_member_required
def admin_dashboard(request):
    """Admin panel dashboard."""
    total_users = User.objects.count()
    total_students = User.objects.filter(role=User.Role.STUDENT).count()
    total_teachers = User.objects.filter(role=User.Role.TEACHER).count()
    total_modules = Module.objects.count()
    total_topics = Topic.objects.count()
    total_assignments = Assignment.objects.count()

    # Student completion stats
    students = User.objects.filter(role=User.Role.STUDENT)
    student_stats = []
    for student in students:
        completed = UserProgress.objects.filter(
            user=student, is_completed=True
        ).count()
        total = Topic.objects.count()
        student_total_score = AssignmentResult.objects.filter(user=student).aggregate(
            total=Sum('score')
        )['total'] or 0
        student_stats.append({
            'student': student,
            'completed': completed,
            'total': total,
            'percent': int((completed / total * 100)) if total > 0 else 0,
            'total_score': student_total_score,
        })

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_modules': total_modules,
        'total_topics': total_topics,
        'total_assignments': total_assignments,
        'student_stats': student_stats,
    }
    return render(request, 'admin_dashboard.html', context)


@staff_member_required
def admin_module_list(request):
    modules = Module.objects.all().order_by('order_number')
    return render(request, 'admin/module_list.html', {'modules': modules})


@staff_member_required
def admin_module_edit(request, module_id=None):
    """Create or edit a module."""
    from django.shortcuts import redirect
    from .models import Module

    if module_id:
        module = get_object_or_404(Module, pk=module_id)
    else:
        module = None

    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        order_number = request.POST.get('order_number', 0)

        if module:
            module.title = title
            module.description = description
            module.order_number = order_number
            module.save()
            messages.success(request, 'Модуль обновлен')
        else:
            Module.objects.create(
                title=title,
                description=description,
                order_number=order_number,
            )
            messages.success(request, 'Модуль создан')
        return redirect('admin_dashboard')

    return render(request, 'admin/module_form.html', {'module': module})


@staff_member_required
def admin_section_edit(request, section_id=None):
    """Create or edit a section."""
    if section_id:
        section = get_object_or_404(Section, pk=section_id)
    else:
        section = None

    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        module = get_object_or_404(Module, pk=module_id) if module_id else None
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        order_number = request.POST.get('order_number', 0)

        if section:
            section.module = module
            section.title = title
            section.description = description
            section.order_number = order_number
            section.save()
            messages.success(request, 'Раздел обновлен')
        else:
            Section.objects.create(
                module=module, title=title,
                description=description, order_number=order_number,
            )
            messages.success(request, 'Раздел создан')
        return redirect('admin_dashboard')

    modules = Module.objects.all().order_by('order_number')
    return render(request, 'admin/section_form.html', {
        'section': section,
        'modules': modules,
    })


@staff_member_required
def admin_topic_edit(request, topic_id=None):
    """Create or edit a topic."""
    if topic_id:
        topic = get_object_or_404(Topic, pk=topic_id)
    else:
        topic = None

    if request.method == 'POST':
        section_id = request.POST.get('section_id')
        section = get_object_or_404(Section, pk=section_id) if section_id else None
        title = request.POST.get('title', '')
        theoretical_content = request.POST.get('theoretical_content', '')
        reading_time = request.POST.get('reading_time', 10)
        order_number = request.POST.get('order_number', 0)

        if topic:
            topic.section = section
            topic.title = title
            topic.theoretical_content = theoretical_content
            topic.reading_time = reading_time
            topic.order_number = order_number
            topic.save()
            messages.success(request, 'Тема обновлена')
        else:
            Topic.objects.create(
                section=section, title=title,
                theoretical_content=theoretical_content,
                reading_time=reading_time, order_number=order_number,
            )
            messages.success(request, 'Тема создана')
        return redirect('admin_dashboard')

    sections = Section.objects.all().order_by('module__order_number', 'order_number')
    return render(request, 'admin/topic_form.html', {
        'topic': topic,
        'sections': sections,
    })


@staff_member_required
def admin_students(request):
    """View all students and their progress."""
    students = User.objects.filter(role=User.Role.STUDENT).order_by('last_name')
    student_data = []
    for student in students:
        total_topics = Topic.objects.count()
        completed = UserProgress.objects.filter(
            user=student, is_completed=True
        ).count()
        total_assignments = Assignment.objects.count()
        done_assignments = AssignmentResult.objects.filter(user=student).count()
        total_score = AssignmentResult.objects.filter(user=student).aggregate(
            total=Sum('score')
        )['total'] or 0
        student_data.append({
            'student': student,
            'completed_topics': completed,
            'total_topics': total_topics,
            'percent': int((completed / total_topics * 100)) if total_topics > 0 else 0,
            'done_assignments': done_assignments,
            'total_assignments': total_assignments,
            'total_score': total_score,
        })

    return render(request, 'admin/students.html', {'student_data': student_data})


@staff_member_required
def admin_assignments(request):
    """View all assignments and manage them."""
    assignments = Assignment.objects.all().select_related('topic').order_by(
        'topic__section__module__order_number',
        'topic__section__order_number',
        'topic__order_number',
    )
    return render(request, 'admin/assignments.html', {
        'assignments': assignments,
    })


@staff_member_required
def admin_assignment_edit(request, assignment_id=None):
    """Create or edit an assignment."""
    if assignment_id:
        assignment = get_object_or_404(Assignment, pk=assignment_id)
    else:
        assignment = None

    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        topic = get_object_or_404(Topic, pk=topic_id) if topic_id else None
        task_text = request.POST.get('task_text', '')
        task_type = request.POST.get('task_type', 'test')
        correct_answer = request.POST.get('correct_answer', '')
        max_score = request.POST.get('max_score', 10)
        options_raw = request.POST.get('options', '[]')

        try:
            options = json.loads(options_raw)
        except json.JSONDecodeError:
            options = []

        if assignment:
            assignment.topic = topic
            assignment.task_text = task_text
            assignment.task_type = task_type
            assignment.correct_answer = correct_answer
            assignment.max_score = max_score
            assignment.options = options
            assignment.save()
            messages.success(request, 'Задание обновлено')
        else:
            Assignment.objects.create(
                topic=topic, task_text=task_text,
                task_type=task_type, correct_answer=correct_answer,
                max_score=max_score, options=options,
            )
            messages.success(request, 'Задание создано')
        return redirect('admin_assignments')

    topics = Topic.objects.all().order_by(
        'section__module__order_number', 'section__order_number', 'order_number'
    )
    return render(request, 'admin/assignment_form.html', {
        'assignment': assignment,
        'topics': topics,
    })


@staff_member_required
@require_POST
def admin_reset_student_progress(request, student_id):
    """Reset all progress and results for a student."""
    student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)

    deleted_progress = UserProgress.objects.filter(user=student).count()
    UserProgress.objects.filter(user=student).delete()

    deleted_results = AssignmentResult.objects.filter(user=student).count()
    AssignmentResult.objects.filter(user=student).delete()

    messages.success(
        request,
        f'Прогресс студента {student.get_full_name() or student.username} сброшен: '
        f'удалено {deleted_progress} записей прогресса и {deleted_results} результатов заданий.'
    )
    return redirect('admin_students')


@staff_member_required
@require_POST
def admin_delete_object(request, model_name, obj_id):
    """Generic delete endpoint for admin."""
    models_map = {
        'module': Module,
        'section': Section,
        'topic': Topic,
        'assignment': Assignment,
        'interactive_element': InteractiveElement,
        'calendar_event': CalendarEvent,
    }
    model = models_map.get(model_name)
    if not model:
        return JsonResponse({'error': 'Invalid model'}, status=400)

    obj = get_object_or_404(model, pk=obj_id)
    obj.delete()
    messages.success(request, 'Объект удален')
    return redirect('admin_dashboard')


import calendar as cal_module
from datetime import date


def calendar_view(request):
    """Calendar page with classic monthly calendar grid.
    Shows CalendarEvent objects managed by admin.
    """
    today = date.today()

    # Get requested year/month, default to current
    year = request.GET.get('year', today.year)
    month = request.GET.get('month', today.month)
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        year = today.year
        month = today.month

    # Clamp month
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Build calendar grid
    cal = cal_module.TextCalendar()
    month_days = cal.monthdayscalendar(year, month)

    # Month name in Russian
    month_names = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь',
    }
    month_name_ru = month_names.get(month, '')

    # Determine prev/next month
    if month == 1:
        prev_month = date(year - 1, 12, 1)
    else:
        prev_month = date(year, month - 1, 1)
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    prev_label = month_names.get(prev_month.month, '')
    next_label = month_names.get(next_month.month, '')

    # Get CalendarEvent objects for this month
    month_events = CalendarEvent.objects.filter(
        date__year=year,
        date__month=month,
    ).select_related('module').order_by('date', 'title')

    # Group events by date
    events_map = {}
    for event in month_events:
        if event.date not in events_map:
            events_map[event.date] = []
        events_map[event.date].append(event)

    modules = Module.objects.all().order_by('order_number')

    # Build week rows for the template
    week_rows = []
    for week in month_days:
        days = []
        for day_num in week:
            if day_num == 0:
                days.append(None)
            else:
                d = date(year, month, day_num)
                events = events_map.get(d, [])
                is_today = (d == today)
                is_past = (d < today)
                days.append({
                    'day': day_num,
                    'date': d,
                    'events': events,
                    'is_today': is_today,
                    'is_past': is_past,
                })
        week_rows.append(days)

    total_events = month_events.count()

    context = {
        'year': year,
        'month': month,
        'month_name': month_name_ru,
        'prev_year': prev_month.year,
        'prev_month': prev_month.month,
        'prev_label': prev_label,
        'next_year': next_month.year,
        'next_month': next_month.month,
        'next_label': next_label,
        'week_rows': week_rows,
        'total_events': total_events,
        'total_modules': modules.count(),
        'modules': modules,
    }
    return render(request, 'calendar.html', context)


@staff_member_required
def admin_calendar_events(request):
    """Admin page for managing calendar events."""
    events = CalendarEvent.objects.all().select_related('module').order_by('-date', 'title')
    return render(request, 'admin/calendar_events.html', {
        'events': events,
    })


@staff_member_required
def admin_calendar_event_edit(request, event_id=None):
    """Create or edit a calendar event."""
    if event_id:
        event = get_object_or_404(CalendarEvent, pk=event_id)
    else:
        event = None

    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        date_str = request.POST.get('date', '')
        module_id = request.POST.get('module_id')
        color = request.POST.get('color', 'accent')
        is_important = request.POST.get('is_important') == 'on'

        module = None
        if module_id:
            module = get_object_or_404(Module, pk=module_id)

        try:
            event_date = date.fromisoformat(date_str)
        except (ValueError, TypeError):
            messages.error(request, 'Неверный формат даты')
            modules = Module.objects.all().order_by('order_number')
            return render(request, 'admin/calendar_event_form.html', {
                'event': event,
                'modules': modules,
            })

        if event:
            event.title = title
            event.description = description
            event.date = event_date
            event.module = module
            event.color = color
            event.is_important = is_important
            event.save()
            messages.success(request, 'Событие обновлено')
        else:
            CalendarEvent.objects.create(
                title=title,
                description=description,
                date=event_date,
                module=module,
                color=color,
                is_important=is_important,
            )
            messages.success(request, 'Событие создано')
        return redirect('admin_calendar_events')

    from datetime import date
    modules = Module.objects.all().order_by('order_number')
    colors = [
        ('accent', 'Акцент (синий)'),
        ('success', 'Зелёный'),
        ('danger', 'Красный'),
        ('warning', 'Жёлтый'),
        ('info', 'Голубой'),
        ('primary', 'Тёмно-синий'),
        ('secondary', 'Серый'),
    ]
    return render(request, 'admin/calendar_event_form.html', {
        'event': event,
        'modules': modules,
        'colors': colors,
        'today': date.today(),
    })


@login_required
def module_test_view(request, module_id):
    """Module test page — shows all assignments for a module as a comprehensive test."""
    module = get_object_or_404(Module, pk=module_id)
    assignments = Assignment.objects.filter(
        topic__section__module=module
    ).order_by('topic__order_number', 'pk')

    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST

        answers = data.get('answers', {})
        results = []
        total_score = 0
        max_score = 0

        for assignment in assignments:
            max_score += assignment.max_score
            user_answer = answers.get(str(assignment.pk), '').strip()

            if not user_answer:
                results.append({
                    'id': assignment.pk,
                    'is_correct': False,
                    'score': 0,
                    'max_score': assignment.max_score,
                    'correct_answer': assignment.correct_answer,
                    'message': 'Нет ответа',
                })
                continue

            # Check answer
            correct = user_answer.lower() == assignment.correct_answer.lower()

            # If multiple choice, check index match
            if assignment.options and assignment.correct_answer.isdigit():
                correct_idx = int(assignment.correct_answer)
                options = assignment.options
                if isinstance(options, list) and correct_idx < len(options):
                    correct_text = options[correct_idx]
                    if isinstance(correct_text, dict):
                        correct_text = correct_text.get('text', correct_text.get('value', ''))
                    correct = (user_answer.lower() == str(correct_idx) or
                               user_answer.lower() == correct_text.lower())

            score = assignment.max_score if correct else 0
            total_score += score

            # Save result
            AssignmentResult.objects.create(
                user=request.user,
                assignment=assignment,
                user_answer=user_answer,
                is_correct=correct,
                score=score,
            )

            results.append({
                'id': assignment.pk,
                'is_correct': correct,
                'score': score,
                'max_score': assignment.max_score,
                'correct_answer': assignment.correct_answer if not correct else None,
            })

        # Mark all topics in this module as completed
        topics = Topic.objects.filter(section__module=module)
        for module_topic in topics:
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                topic=module_topic,
                defaults={'is_completed': True},
            )
            if not progress.is_completed:
                progress.is_completed = True
                progress.save()

        return JsonResponse({
            'results': results,
            'total_score': total_score,
            'max_score': max_score,
            'percent': int((total_score / max_score * 100)) if max_score > 0 else 0,
        })

    # Get user's previous results for this module's assignments
    user_results = {}
    if request.user.is_authenticated:
        previous = AssignmentResult.objects.filter(
            user=request.user,
            assignment__topic__section__module=module
        ).select_related('assignment').order_by('-completed_at')
        for pr in previous:
            if pr.assignment_id not in user_results:
                user_results[pr.assignment_id] = {
                    'is_correct': pr.is_correct,
                    'score': pr.score,
                }

    context = {
        'module': module,
        'assignments': assignments,
        'user_results': user_results,
        'total_questions': assignments.count(),
    }
    return render(request, 'module_test.html', context)


def materials_view(request):
    """Supplementary materials page."""
    modules = Module.objects.all().order_by('order_number')
    
    # Supplementary resources by module
    resources = [
        {
            'title': 'Учебники и пособия',
            'icon': 'book',
            'items': [
                {'name': 'Таненбаум Э. Архитектура компьютера. — 6-е изд.', 'type': 'book', 'url': '#'},
                {'name': 'Паттерсон Д., Хеннесси Дж. Архитектура компьютера и проектирование компьютерных систем', 'type': 'book', 'url': '#'},
                {'name': 'Харрис Д., Харрис С. Цифровая схемотехника и архитектура компьютера', 'type': 'book', 'url': '#'},
                {'name': 'Столлингс У. Структурная организация и архитектура компьютерных систем', 'type': 'book', 'url': '#'},
            ]
        },
        {
            'title': 'Онлайн-ресурсы',
            'icon': 'globe',
            'items': [
                {'name': 'RISC-V International — официальная документация ISA', 'type': 'link', 'url': 'https://riscv.org/'},
                {'name': 'Godbolt Compiler Explorer — онлайн-компилятор', 'type': 'link', 'url': 'https://godbolt.org/'},
                {'name': 'CPU-OS Simulator — симулятор процессора', 'type': 'link', 'url': '#'},
                {'name': 'Digital Logic Sim — симулятор цифровых схем', 'type': 'link', 'url': '#'},
            ]
        },
        {
            'title': 'Инструменты для практики',
            'icon': 'tools',
            'items': [
                {'name': 'RARS — RISC-V Assembler and Runtime Simulator', 'type': 'tool', 'url': '#'},
                {'name': 'Logisim — редактор цифровых схем', 'type': 'tool', 'url': '#'},
                {'name': 'SPIM — симулятор MIPS', 'type': 'tool', 'url': '#'},
                {'name': 'QEMU — эмулятор процессоров', 'type': 'tool', 'url': 'https://www.qemu.org/'},
            ]
        },
        {
            'title': 'Дополнительные лекции по модулям',
            'icon': 'camera-video',
            'items': [
                {'name': 'Модуль 1-2: Введение и архитектура (видеолекции)', 'type': 'video', 'url': '#'},
                {'name': 'Модуль 3: Конвейерная обработка (видеолекции)', 'type': 'video', 'url': '#'},
                {'name': 'Модуль 4: Память и ввод-вывод (видеолекции)', 'type': 'video', 'url': '#'},
                {'name': 'Модуль 5: Программирование на ассемблере (видеолекции)', 'type': 'video', 'url': '#'},
                {'name': 'Модуль 6: Современные процессоры (видеолекции)', 'type': 'video', 'url': '#'},
            ]
        },
    ]
    
    context = {
        'resources': resources,
        'modules': modules,
    }
    return render(request, 'materials.html', context)
