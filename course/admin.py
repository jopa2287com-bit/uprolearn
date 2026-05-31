from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, Module, Section, Topic,
    InteractiveElement, Assignment, AssignmentResult, UserProgress, CalendarEvent,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'get_full_name', 'email', 'role',
        'is_staff', 'is_active', 'date_joined'
    )
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'patronymic', 'avatar')}),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Полное имя'


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ('title', 'order_number')


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    fields = ('title', 'order_number', 'reading_time')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'title', 'section_count')
    list_display_links = ('title',)
    ordering = ('order_number',)
    search_fields = ('title', 'description')
    inlines = [SectionInline]

    def section_count(self, obj):
        return obj.sections.count()
    section_count.short_description = 'Разделов'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'title', 'module', 'topic_count')
    list_filter = ('module',)
    ordering = ('module__order_number', 'order_number')
    search_fields = ('title', 'description')
    inlines = [TopicInline]

    def topic_count(self, obj):
        return obj.topics.count()
    topic_count.short_description = 'Тем'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'reading_time', 'order_number')
    list_filter = ('section__module', 'section')
    ordering = ('section__module__order_number', 'section__order_number', 'order_number')
    search_fields = ('title', 'theoretical_content')
    fieldsets = (
        ('Основное', {
            'fields': ('section', 'title', 'order_number', 'reading_time')
        }),
        ('Содержание', {
            'fields': ('theoretical_content',),
            'classes': ('wide',),
        }),
    )


@admin.register(InteractiveElement)
class InteractiveElementAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'element_type', 'url_short')
    list_filter = ('element_type', 'topic__section__module')
    search_fields = ('title', 'url')

    def url_short(self, obj):
        if obj.url:
            return format_html('<a href="{}" target="_blank">Открыть</a>', obj.url)
        return '-'
    url_short.short_description = 'URL'


class AssignmentResultInline(admin.TabularInline):
    model = AssignmentResult
    extra = 0
    readonly_fields = ('user', 'user_answer', 'is_correct', 'score', 'completed_at')
    can_delete = False
    max_num = 0


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('task_short', 'topic', 'task_type', 'max_score')
    list_filter = ('task_type', 'topic__section__module')
    search_fields = ('task_text',)
    inlines = [AssignmentResultInline]

    def task_short(self, obj):
        return obj.task_text[:60] + ('...' if len(obj.task_text) > 60 else '')
    task_short.short_description = 'Задание'


@admin.register(AssignmentResult)
class AssignmentResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'assignment', 'is_correct', 'score', 'completed_at')
    list_filter = ('is_correct', 'assignment__task_type')
    search_fields = ('user__username',)
    readonly_fields = ('completed_at',)
    date_hierarchy = 'completed_at'


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'module', 'color', 'is_important')
    list_filter = ('is_important', 'color', 'date')
    search_fields = ('title', 'description')
    date_hierarchy = 'date'
    ordering = ('-date',)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'is_completed', 'updated_at')
    list_filter = ('is_completed', 'topic__section__module')
    search_fields = ('user__username', 'topic__title')
    date_hierarchy = 'updated_at'
