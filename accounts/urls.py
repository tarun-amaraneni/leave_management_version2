from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('employee/leave-request/', views.leave_request_view, name='leave_request'),
    path('employee/my-leaves/', views.my_leaves, name='my_leaves'),
    path('employee/leave-calendar/', views.leave_calendar, name='leave_calendar'),


    path('employee/leave-calendar/', views.leave_calendar, name='leave_calendar'),
    path('employee/leave-calendar/<int:year>/<int:month>/', views.leave_calendar, name='leave_calendar'),
    path('entitlements/', views.entitlements_view, name='entitlements'),
    path('logout/', views.logout_view, name='logout'),



    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/leaves/', views.manager_leave_list, name='manager_leave_list'),
    path('manager/leave/<int:leave_id>/<str:action>/', views.leave_action, name='leave_action'),
    path('view-members/', views.view_members, name='view_members'),

   # Current month by default
    path('manager_leave_calendar/', views.manager_leave_calendar, name='manager_leave_calendar'),

    # Specific year/month
    path('manager_leave_calendar/<int:year>/<int:month>/', views.manager_leave_calendar, name='manager_leave_calendar'),


    path(
    "manager/leave-day-details/",
    views.manager_leave_day_details,
    name="manager_leave_day_details"
),



# urls.py
    path(
    "manager/leave-action/",
    views.leave_action_with_comment,
    name="leave_action_with_comment"
),
 
 path('leave/<int:leave_id>/cancel/', views.cancel_leave, name='cancel_leave'),

    
]
