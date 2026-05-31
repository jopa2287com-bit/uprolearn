from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Main pages
    path('', views.index, name='index'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Module test
    path('module/<int:module_id>/test/', views.module_test_view, name='module_test'),

    # Additional pages
    path('calendar/', views.calendar_view, name='calendar'),
    path('materials/', views.materials_view, name='materials'),

    # AJAX endpoints
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('topic/<int:topic_id>/toggle/', views.toggle_topic_complete, name='toggle_topic_complete'),

    # Admin panel
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/modules/', views.admin_module_list, name='admin_module_list'),
    path('admin-panel/module/create/', views.admin_module_edit, name='admin_module_create'),
    path('admin-panel/module/<int:module_id>/edit/', views.admin_module_edit, name='admin_module_edit'),
    path('admin-panel/section/create/', views.admin_section_edit, name='admin_section_create'),
    path('admin-panel/section/<int:section_id>/edit/', views.admin_section_edit, name='admin_section_edit'),
    path('admin-panel/topic/create/', views.admin_topic_edit, name='admin_topic_create'),
    path('admin-panel/topic/<int:topic_id>/edit/', views.admin_topic_edit, name='admin_topic_edit'),
    path('admin-panel/students/', views.admin_students, name='admin_students'),
    path('admin-panel/assignments/', views.admin_assignments, name='admin_assignments'),
    path('admin-panel/assignment/create/', views.admin_assignment_edit, name='admin_assignment_create'),
    path('admin-panel/assignment/<int:assignment_id>/edit/', views.admin_assignment_edit, name='admin_assignment_edit'),
    path('admin-panel/student/<int:student_id>/reset-progress/', views.admin_reset_student_progress, name='admin_reset_student_progress'),
    path('admin-panel/calendar-events/', views.admin_calendar_events, name='admin_calendar_events'),
    path('admin-panel/calendar-event/create/', views.admin_calendar_event_edit, name='admin_calendar_event_create'),
    path('admin-panel/calendar-event/<int:event_id>/edit/', views.admin_calendar_event_edit, name='admin_calendar_event_edit'),
    path('admin-panel/delete/<str:model_name>/<int:obj_id>/', views.admin_delete_object, name='admin_delete_object'),

    # Django admin
    path('django-admin/', admin.site.urls),
]
