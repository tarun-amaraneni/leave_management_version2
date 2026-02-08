from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from .models import UserProfile
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.conf import settings
import os
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            profile = UserProfile.objects.get(user=user)

            if profile.role == 'MANAGER':
                return redirect('manager_dashboard')
            elif profile.role == 'EMPLOYEE':
                return redirect('employee_dashboard')
            else:
                return redirect('ceo_dashboard')

    return render(request, 'auth/login.html')

from django.contrib.auth.decorators import login_required


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from collections import defaultdict
from datetime import timedelta
from .models import LeaveRequest

TOTAL_ENTITLEMENT = int(os.environ.get("TOTAL_ENTITLEMENT", 12))




from datetime import timedelta
from .models import Holiday

def calculate_leave_days(start_date, end_date):
    """
    Count leave days excluding:
    - Holidays where holiday_indicator = 'Y'
    """

    holiday_dates = set(
        Holiday.objects.filter(
            holiday_indicator='Y',
            holiday_date__range=(start_date, end_date)
        ).values_list('holiday_date', flat=True)
    )

    days = 0
    current = start_date

    while current <= end_date:
        if current not in holiday_dates:
            days += 1
        current += timedelta(days=1)

    return days


@never_cache
@login_required
def employee_dashboard(request):
    holidays = Holiday.objects.filter(holiday_indicator='Y').values_list('holiday_date', flat=True)
    holiday_dates = [h.isoformat() for h in holidays]  # convert to 'YYYY-MM-DD' strings

    user = request.user

    # --- ENTITLEMENTS LOGIC (reuse your existing function) ---
    approved_leaves = LeaveRequest.objects.filter(
        employee=user,
        status='APPROVED'
    )

    leave_days_map = defaultdict(int)
    for leave in approved_leaves:
        days = calculate_leave_days(leave.start_date, leave.end_date)
        leave_days_map[leave.leave_type] += days

    entitlements = []
    for leave_type, label in LeaveRequest.LEAVE_TYPE_CHOICES:
        applied_days = leave_days_map.get(leave_type, 0)
        remaining = max(TOTAL_ENTITLEMENT - applied_days, 0)
        used_percent = int((applied_days / TOTAL_ENTITLEMENT) * 100) if TOTAL_ENTITLEMENT else 0

        entitlements.append({
            'type': label,
            'total': TOTAL_ENTITLEMENT,
            'applied': applied_days,
            'remaining': remaining,
            'used_percent': used_percent
        })

    # Pass entitlements to dashboard template
    return render(request, 'employee/dashboard.html', {
        'entitlements': entitlements,
         "holiday_dates": holiday_dates,
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from collections import defaultdict
from datetime import timedelta
from .models import LeaveRequest

TOTAL_ENTITLEMENT = settings.TOTAL_ENTITLEMENT


from datetime import timedelta
from .models import Holiday

def calculate_leave_days(start_date, end_date):
    """
    Count leave days excluding:
    - Holidays where holiday_indicator = 'Y'
    """

    holiday_dates = set(
        Holiday.objects.filter(
            holiday_indicator='Y',
            holiday_date__range=(start_date, end_date)
        ).values_list('holiday_date', flat=True)
    )

    days = 0
    current = start_date

    while current <= end_date:
        if current not in holiday_dates:
            days += 1
        current += timedelta(days=1)

    return days

@never_cache
@login_required
def manager_dashboard(request):
    user = request.user

    # --- ENTITLEMENTS LOGIC (reuse your existing function) ---
    approved_leaves = LeaveRequest.objects.filter(
        employee=user,
        status='APPROVED'
    )

    leave_days_map = defaultdict(int)
    for leave in approved_leaves:
        days = calculate_leave_days(leave.start_date, leave.end_date)
        leave_days_map[leave.leave_type] += days

    entitlements = []
    for leave_type, label in LeaveRequest.LEAVE_TYPE_CHOICES:
        applied_days = leave_days_map.get(leave_type, 0)
        remaining = max(TOTAL_ENTITLEMENT - applied_days, 0)
        used_percent = int((applied_days / TOTAL_ENTITLEMENT) * 100) if TOTAL_ENTITLEMENT else 0

        entitlements.append({
            'type': label,
            'total': TOTAL_ENTITLEMENT,
            'applied': applied_days,
            'remaining': remaining,
            'used_percent': used_percent
        })

    # Pass entitlements to dashboard template
    return render(request, 'manager/dashboard.html', {
        'entitlements': entitlements
    })


# view for Apply Leave
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import LeaveRequest, UserProfile

TOTAL_ENTITLEMENT = settings.TOTAL_ENTITLEMENT



from datetime import timedelta
from .models import Holiday

from datetime import timedelta
from .models import Holiday

def calculate_leave_days(start_date, end_date):
    """
    Count leave days excluding:
    - Holidays where holiday_indicator = 'Y'
    """

    holiday_dates = set(
        Holiday.objects.filter(
            holiday_indicator='Y',
            holiday_date__range=(start_date, end_date)
        ).values_list('holiday_date', flat=True)
    )

    days = 0
    current = start_date

    while current <= end_date:
        if current not in holiday_dates:
            days += 1
        current += timedelta(days=1)

    return days

@never_cache
@login_required
def leave_request_view(request):
    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        # 1️⃣ Basic validation
        if not all([leave_type, start_date, end_date, reason]):
            messages.error(request, "All fields are required.")
            return redirect('employee_dashboard')

        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)

        # 2️⃣ Date validation
        if end_date < start_date:
            messages.error(request, "End date cannot be before start date.")
            return redirect('employee_dashboard')

        # 3️⃣ Requested leave days
        requested_days = calculate_leave_days(start_date, end_date)

        if requested_days <= 0:
            messages.error(request, "Invalid leave duration.")
            return redirect('employee_dashboard')

        # 4️⃣ Calculate already used entitlement (APPROVED only)
        approved_leaves = LeaveRequest.objects.filter(
            employee=request.user,
            leave_type=leave_type,
            status='APPROVED'
        )

        used_days = sum(
            calculate_leave_days(l.start_date, l.end_date)
            for l in approved_leaves
        )

        remaining_days = max(TOTAL_ENTITLEMENT - used_days, 0)


        # 5️⃣ Entitlement check ❌
        if requested_days > remaining_days:
            messages.error(
                request,
                f"Leave exceeds entitlement. Remaining balance: {remaining_days} day(s)."
            )
            return redirect('employee_dashboard')

        # 6️⃣ Assign manager
        try:
            manager = request.user.userprofile.manager
        except UserProfile.DoesNotExist:
            manager = None

        # 7️⃣ Create leave request ✅
        LeaveRequest.objects.create(
            employee=request.user,
            manager=manager,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='PENDING'
        )

        messages.success(
            request,
            f"Leave request submitted for {requested_days} day(s)."
        )
        return redirect('employee_dashboard')

    return redirect('employee_dashboard')



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import LeaveRequest

@never_cache
@login_required
def my_leaves(request):
    leaves = LeaveRequest.objects.filter(employee=request.user).order_by('-submitted_at')
    return render(request, 'employee/my_leaves.html', {'leaves': leaves})




# ////
from datetime import date, timedelta
import calendar
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import LeaveRequest
from django.db.models import Q


@never_cache
@login_required
def leave_calendar(request, year=None, month=None):
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    # First and last day of the month
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    # Get leaves that overlap this month AND belong to the logged-in user
    leaves = LeaveRequest.objects.filter(
        Q(start_date__lte=last_day) & Q(end_date__gte=first_day),
        employee=request.user  # <-- filter by logged-in user
    )

    # Map each date to list of leaves
    leave_dict = {}
    for leave in leaves:
        current = leave.start_date
        while current <= leave.end_date:
            # Only map dates that are in the current calendar month
            if first_day <= current <= last_day:
                leave_dict.setdefault(current, []).append(leave)
            current += timedelta(days=1)

    # Calendar days
    cal = calendar.Calendar(firstweekday=0)
    month_days = list(cal.itermonthdates(year, month))
    weeks = [month_days[i:i+7] for i in range(0, len(month_days), 7)]

    # Prepare parallel structure
    calendar_data = []
    for week in weeks:
        week_data = []
        for day in week:
            week_data.append({
                'date': day,
                'leaves': leave_dict.get(day, [])
            })
        calendar_data.append(week_data)

    # Previous and next month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    context = {
        'year': year,
        'month': month,
        'calendar_data': calendar_data,
        'weekdays': ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    return render(request, 'employee/leave_calendar.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from collections import defaultdict
from datetime import timedelta
from .models import LeaveRequest
from collections import defaultdict
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from .models import LeaveRequest

TOTAL_ENTITLEMENT = settings.TOTAL_ENTITLEMENT



from datetime import timedelta
from .models import Holiday

def calculate_leave_days(start_date, end_date):
    """
    Count leave days excluding:
    - Holidays where holiday_indicator = 'Y'
    """

    holiday_dates = set(
        Holiday.objects.filter(
            holiday_indicator='Y',
            holiday_date__range=(start_date, end_date)
        ).values_list('holiday_date', flat=True)
    )

    days = 0
    current = start_date

    while current <= end_date:
        if current not in holiday_dates:
            days += 1
        current += timedelta(days=1)

    return days

@never_cache
@login_required
def entitlements_view(request):
    user = request.user

    approved_leaves = LeaveRequest.objects.filter(
        employee=user,
        status='APPROVED'
    )

    # leave_type → total days (excluding Sundays)
    leave_days_map = defaultdict(int)

    for leave in approved_leaves:
        days = calculate_leave_days(leave.start_date, leave.end_date)
        leave_days_map[leave.leave_type] += days

    entitlements = []

    for leave_type, label in LeaveRequest.LEAVE_TYPE_CHOICES:
        applied_days = leave_days_map.get(leave_type, 0)
        remaining = max(TOTAL_ENTITLEMENT - applied_days, 0)

        used_percent = int((applied_days / TOTAL_ENTITLEMENT) * 100) if TOTAL_ENTITLEMENT else 0

        entitlements.append({
            'type': label,
            'total': TOTAL_ENTITLEMENT,
            'applied': applied_days,
            'remaining': remaining,
            'used_percent': used_percent
        })

    return render(request, 'employee/entitlements.html', {
        'entitlements': entitlements
    })



from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  # change if your login URL name is different








# manager
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from .models import LeaveRequest, UserProfile




from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@never_cache
@login_required
def manager_leave_list(request):
    profile = request.user.userprofile
    # if profile.role != 'MANAGER':
    #     return render(request, '403.html')

    # Get filters from request
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '')
    leave_type = request.GET.get('leave_type', '')

    leaves = LeaveRequest.objects.filter(manager=request.user)

    # Apply search filter
    if search:
        leaves = leaves.filter(employee__username__icontains=search)

    # Apply status filter
    if status:
        leaves = leaves.filter(status=status)

    # Apply leave_type filter
    if leave_type:
        leaves = leaves.filter(leave_type=leave_type)

    # Dynamically calculate counts for **currently filtered leaves**
    pending_count = leaves.filter(status='PENDING').count()
    approved_count = leaves.filter(status='APPROVED').count()
    rejected_count = leaves.filter(status='REJECTED').count()

    context = {
        "leaves": leaves.order_by('-submitted_at'),
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "status_choices": LeaveRequest.STATUS_CHOICES,
        "leave_type_choices": LeaveRequest.LEAVE_TYPE_CHOICES,
    }

    return render(request, 'manager/leave_list.html', context)


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages


@never_cache
@login_required
def leave_action(request, leave_id, action):
    profile = request.user.userprofile

    if profile.role != 'MANAGER':
        messages.error(request, "Unauthorized access.")
        return redirect('manager_dashboard')

    leave = get_object_or_404(
        LeaveRequest,
        id=leave_id,
        manager=request.user,
        status='PENDING'
    )

    if action == 'approve':
        leave.status = 'APPROVED'
        messages.success(request, "Leave approved successfully.")

    elif action == 'reject':
        leave.status = 'REJECTED'
        messages.success(request, "Leave rejected successfully.")

    else:
        messages.error(request, "Invalid action.")

    leave.save()
    return redirect('manager_leave_list')







# manager
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required
def view_members(request):
    current_user = request.user

    # Fetch employees under this manager
    members = UserProfile.objects.filter(manager=current_user)

    context = {
        'members': members
    }
    return render(request, 'manager/view_members.html', context)



from datetime import date, timedelta
import calendar
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Q, Count
from .models import LeaveRequest, UserProfile
from django.contrib.auth.models import User

from datetime import date, timedelta
import calendar
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.contrib.auth.models import User
from .models import LeaveRequest

@never_cache
@login_required
def manager_leave_calendar(request, year=None, month=None):
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    # First and last day of the month
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    # Employees under current manager
    employees = User.objects.filter(userprofile__manager=request.user)

    # Leaves for these employees overlapping this month (ignore rejected)
    leaves = LeaveRequest.objects.filter(
        Q(start_date__lte=last_day) & Q(end_date__gte=first_day),
        employee__in=employees
    ).exclude(status__iexact='REJECTED')  # ignore rejected leaves

    # Map each date -> approved/pending counts
    leave_dict = {}
    for leave in leaves:
        current = leave.start_date
        while current <= leave.end_date:
            if first_day <= current <= last_day:
                day_counts = leave_dict.setdefault(current, {'approved': 0, 'pending': 0})
                status = leave.status.upper()
                if status == 'APPROVED':
                    day_counts['approved'] += 1
                elif status == 'PENDING':
                    day_counts['pending'] += 1
            current += timedelta(days=1)

    # Prepare calendar
    cal = calendar.Calendar(firstweekday=0)
    month_days = list(cal.itermonthdates(year, month))
    weeks = [month_days[i:i+7] for i in range(0, len(month_days), 7)]

    calendar_data = []
    for week in weeks:
        week_data = []
        for day in week:
            counts = leave_dict.get(day, {'approved': 0, 'pending': 0})
            week_data.append({
                'date': day,
                'approved_count': counts['approved'],
                'pending_count': counts['pending'],
            })
        calendar_data.append(week_data)

    # Previous/Next month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    context = {
        'year': year,
        'month': month,
        'calendar_data': calendar_data,
        'weekdays': ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }

    return render(request, 'manager/manager_leave_calendar.html', context)


from datetime import datetime
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.contrib.auth.models import User
from .models import LeaveRequest


@never_cache
@login_required
def manager_leave_day_details(request):
    date_str = request.GET.get("date")
    status = request.GET.get("status")

    if not date_str or not status:
        return JsonResponse({"data": []})

    selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # employees under this manager
    employees = User.objects.filter(userprofile__manager=request.user)

    leaves = LeaveRequest.objects.filter(
        employee__in=employees,
        status=status,
        start_date__lte=selected_date,
        end_date__gte=selected_date,
    )

    data = []
    for leave in leaves:
        data.append({
            "name": leave.employee.get_full_name() or leave.employee.username,
            "from": leave.start_date.strftime("%d-%m-%Y"),
            "to": leave.end_date.strftime("%d-%m-%Y"),
            "reason": leave.reason,
        })

    return JsonResponse({"data": data})






from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import LeaveRequest

@login_required
@require_POST
def leave_action_with_comment(request):
    leave_id = request.POST.get("leave_id")
    action = request.POST.get("action")
    comment = request.POST.get("comment")

    leave = get_object_or_404(
        LeaveRequest,
        id=leave_id,
        manager=request.user
    )

    if action == "approve":
        leave.status = "APPROVED"
    elif action == "reject":
        leave.status = "REJECTED"

    leave.comment_by_manager = comment
    leave.save()

    return redirect("manager_leave_list")  # adjust URL name if needed




from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import LeaveRequest

@login_required
@require_POST
def cancel_leave(request, leave_id):
    leave = get_object_or_404(
        LeaveRequest,
        id=leave_id,
        employee=request.user
    )

    if leave.status not in ['PENDING', 'APPROVED']:
        messages.error(request, "This leave cannot be canceled.")
        return redirect('my_leaves')

    leave.status = 'CANCELED'
    leave.save()

    messages.success(request, "Leave request canceled successfully.")
    return redirect('my_leaves')
