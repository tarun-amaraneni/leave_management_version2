# Leave Management System

## Project Overview
The Leave Management System is a Django-based web application for managing employee leave requests. Employees can submit leave requests, track entitlements, and view their leave history. Managers can approve or reject requests, monitor team leaves, and view leave calendars.

---

## Features

### Employee
- Submit leave requests with validation for dates and entitlements.  
- View dashboard with leave entitlements, used, remaining, and percentage used.  
- View submitted leaves with status (Pending, Approved, Rejected).  
- Monthly leave calendar highlighting approved and pending leaves.  
- Entitlements page for detailed leave type tracking.

### Manager
- View dashboard with team leave entitlements and usage.  
- Filter and manage leave requests by employee, type, or status.  
- Approve or reject leave requests with optional comments.  
- Team leave calendar with daily approved/pending counts.  
- View employees under their management.

### Authentication
- Role-based login for EMPLOYEE, MANAGER, and CEO.  
- Redirect to appropriate dashboard based on role.  
- Logout functionality with confirmation messages.

---

## Views Overview

| View | Role | Description |
|------|------|-------------|
| `login_view` | All | Authenticate users and redirect based on role |
| `logout_view` | All | Logout users |
| `employee_dashboard` | Employee | Shows leave entitlements and dashboard data |
| `manager_dashboard` | Manager | Shows dashboard for team leave entitlements |
| `leave_request_view` | Employee | Submit leave request with validation |
| `my_leaves` | Employee | List all leaves of the logged-in employee |
| `leave_calendar` | Employee | Monthly calendar with leaves |
| `entitlements_view` | Employee | Display leave entitlements by type |
| `manager_leave_list` | Manager | List all leave requests for approval/rejection |
| `leave_action` | Manager | Approve or reject a leave request |
| `leave_action_with_comment` | Manager | Approve/reject with comment |
| `view_members` | Manager | List employees reporting to the manager |
| `manager_leave_calendar` | Manager | Team leave calendar with approved/pending counts |
| `manager_leave_day_details` | Manager | Show employees on leave for a selected day |

---

## Project Structure

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tarun-amaraneni/leave_management.git
cd leave_management
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
