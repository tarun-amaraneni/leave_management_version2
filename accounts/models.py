from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('EMPLOYEE', 'Employee'),
        ('MANAGER', 'Manager'),
        ('CEO', 'CEO'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"




from django.db import models
from django.contrib.auth.models import User

class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELED', 'Canceled'),
    )

    LEAVE_TYPE_CHOICES = (
        ('Vacation', 'Vacation'),
        ('Sick Leave', 'Sick Leave'),
        ('Work From Home', 'Work From Home'),
    )

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approvals')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
    comment_by_manager = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.status})"






from django.db import models

class Holiday(models.Model):
    HOLIDAY_CHOICES = (
        ('Y', 'Holiday'),
        ('N', 'Non-Holiday'),
    )

    holiday_date = models.DateField(primary_key=True)  # Primary key
    holiday_day = models.CharField(max_length=10)      # Day of the week, e.g., Monday
    holiday_indicator = models.CharField(
        max_length=1,
        choices=HOLIDAY_CHOICES,
        default='N'
    )
    holiday_reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'holiday'
        verbose_name = 'Holiday'
        verbose_name_plural = 'Holidays'
        ordering = ['holiday_date']

    def __str__(self):
        return f"{self.holiday_date} - {self.holiday_reason or 'No Reason'}"
