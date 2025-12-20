from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta

# Import Models
from .models import Student, MovementLog, LeaveRequest

# Import Forms
from .forms import (
    LeaveRequestForm,
    StudentForm,
    CSVUploadForm,
    StudentProfileForm,
)

# =========================================================
# POST LOGIN REDIRECT
# =========================================================
@login_required
def post_login_redirect(request):
    if hasattr(request.user, "student"):
        return redirect("student_profile")
    return redirect("home")

# =========================================================
# HOME (ADMIN / STAFF ONLY)
# =========================================================
@login_required
def home(request):
    if hasattr(request.user, "student"):
        return redirect("student_profile")

    context = {
        "inside_count": Student.objects.filter(is_inside=True).count(),
        "outside_count": Student.objects.filter(is_inside=False).count(),
        "recent_logs": MovementLog.objects.select_related("student")[:10],
    }
    return render(request, "gate/home.html", context)

# =========================================================
# STUDENT PROFILE
# =========================================================
@login_required
def student_profile(request):
    if not hasattr(request.user, "student"):
        return redirect("home")

    student = request.user.student

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("student_profile")
    else:
        form = StudentProfileForm(instance=student)

    return render(request, "gate/student_profile.html", {"student": student, "form": form})

# =========================================================
# STUDENT DASHBOARD
# =========================================================
@login_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    now = timezone.now()
    today = now.date()

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            # Check for existing pending requests
            if LeaveRequest.objects.filter(student=student, status=LeaveRequest.STATUS_PENDING).exists():
                messages.warning(request, "You already have a pending request. Please wait for approval.")
                return redirect("student_dashboard")

            leave = form.save(commit=False)
            leave.student = student
            # Use the Model Constant
            leave.request_type = LeaveRequest.LEAVE 
            leave.status = LeaveRequest.STATUS_PENDING
            leave.save()

            messages.success(request, "Leave request submitted successfully.")
            return redirect("student_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LeaveRequestForm()

    # Active Leave (Long term)
    active_leave = LeaveRequest.objects.filter(
        student=student,
        request_type=LeaveRequest.LEAVE,
        status=LeaveRequest.STATUS_APPROVED,
        from_date__lte=now,
        to_date__gte=now
    ).first()

    # Active Outpass (Today only)
    active_outpass = LeaveRequest.objects.filter(
        student=student,
        request_type=LeaveRequest.OUTPASS,
        status=LeaveRequest.STATUS_APPROVED,
        from_date__date=today
    ).first()

    expired_outpass = None
    if active_outpass and active_outpass.to_date < now:
        expired_outpass = active_outpass
        active_outpass = None

    # History
    two_days_ago = now - timedelta(days=2)
    recent_requests = LeaveRequest.objects.filter(student=student, created_at__gte=two_days_ago).order_by("-created_at")

    context = {
        "student": student,
        "form": form,
        "recent_requests": recent_requests,
        "active_leave": active_leave,
        "active_outpass": active_outpass,
        "expired_outpass": expired_outpass,
        "now": now,
    }
    return render(request, "gate/student_dashboard.html", context)

# =========================================================
# APPLY FOR OUTPASS (ONE CLICK)
# =========================================================
@login_required
@require_http_methods(["POST"])
def apply_outpass(request):
    if not hasattr(request.user, "student"):
        return redirect("home")

    student = request.user.student
    now = timezone.now()
    today = now.date()

    # Check for duplicate requests today
    if LeaveRequest.objects.filter(
        student=student,
        request_type=LeaveRequest.OUTPASS,
        from_date__date=today,
        status__in=[LeaveRequest.STATUS_PENDING, LeaveRequest.STATUS_APPROVED]
    ).exists():
        messages.warning(request, "You already have an active or pending outpass today.")
        return redirect("student_profile")

    # Set expiry to 8:00 PM
    expiry_time = now.replace(hour=20, minute=0, second=0, microsecond=0)

    LeaveRequest.objects.create(
        student=student,
        request_type=LeaveRequest.OUTPASS, # Use Model Constant
        reason="Outpass Request",
        from_date=now,
        to_date=expiry_time,
        status=LeaveRequest.STATUS_PENDING
    )

    messages.success(request, "Outpass request sent.")
    return redirect("student_profile")

# =========================================================
# GATE CHECK (SEARCH)
# =========================================================
@login_required
def check(request):
    query = request.POST.get("enrollment_number") or request.GET.get("enr")
    query = query.strip() if query else None

    student = None
    results = None
    active_leave = None
    searched = False

    if query:
        searched = True
        try:
            student = Student.objects.get(enrollment_number__iexact=query)
        except Student.DoesNotExist:
            results = Student.objects.filter(
                Q(enrollment_number__icontains=query) | Q(full_name__icontains=query)
            )[:20]
            if results.count() == 1:
                student = results.first()
                results = None

        if student:
            now = timezone.now()
            active_leave = LeaveRequest.objects.filter(
                student=student,
                status=LeaveRequest.STATUS_APPROVED,
                from_date__lte=now,
                to_date__gte=now
            ).first()

    return render(request, "gate/check.html", {
        "searched": searched,
        "student": student,
        "results": results,
        "active_leave": active_leave,
    })

# =========================================================
# GATE TOGGLE
# =========================================================
@login_required
@permission_required("gate.can_toggle_status", raise_exception=True)
@require_http_methods(["POST"])
def toggle_status(request):
    enrollment = request.POST.get("enrollment_number", "").strip()
    note = request.POST.get("note", "").strip()
    student = get_object_or_404(Student, enrollment_number=enrollment)
    now = timezone.now()

    if student.is_inside:
        # Check permissions before letting OUT
        has_permission = LeaveRequest.objects.filter(
            student=student,
            status=LeaveRequest.STATUS_APPROVED,
            from_date__lte=now,
            to_date__gte=now
        ).exists()

        if not has_permission:
            messages.error(request, "No active approved leave or outpass.")
            return redirect(f"/gate/check/?enr={student.enrollment_number}")

        student.is_inside = False
        direction = MovementLog.OUT
    else:
        # Letting IN
        student.is_inside = True
        direction = MovementLog.IN
        
        # Expire Outpass on return
        LeaveRequest.objects.filter(
            student=student,
            request_type=LeaveRequest.OUTPASS,
            status=LeaveRequest.STATUS_APPROVED
        ).update(status=LeaveRequest.STATUS_EXPIRED, to_date=now)

    student.save()
    MovementLog.objects.create(
        student=student,
        direction=direction,
        recorded_by=request.user,
        note=note
    )

    messages.success(request, f"{student.full_name} marked {direction}.")
    return redirect(f"/gate/check/?enr={student.enrollment_number}")

# =========================================================
# APPROVAL DASHBOARD (UPDATED)
# =========================================================
@login_required
@permission_required("gate.can_approve_leave", raise_exception=True)
def approval_dashboard(request):
    # Get filters from URL, default to 'pending' and 'all' types
    status_filter = request.GET.get("status", "pending") 
    
    # 1. Base Query
    requests_qs = LeaveRequest.objects.select_related("student").order_by("-created_at")

    # 2. Apply Status Filter
    if status_filter != "all":
        requests_qs = requests_qs.filter(status=status_filter)

    # 3. Role Based Logic
    if request.user.groups.filter(name="Supervisor").exists():
        requests_qs = requests_qs.filter(status=LeaveRequest.STATUS_PENDING)

    # 4. Calculate Counts for the Dashboard Cards
    pending_count = LeaveRequest.objects.filter(status=LeaveRequest.STATUS_PENDING).count()
    approved_count = LeaveRequest.objects.filter(status=LeaveRequest.STATUS_APPROVED).count()
    rejected_count = LeaveRequest.objects.filter(status=LeaveRequest.STATUS_REJECTED).count()

    context = {
        "requests": requests_qs,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "status_filter": status_filter,
    }

    return render(request, "gate/approval_dashboard.html", context)

# =========================================================
# APPROVE / REJECT ACTIONS
# =========================================================
@login_required
@permission_required("gate.can_approve_leave", raise_exception=True)
@require_http_methods(["POST"])
def approve_leave(request, request_id):
    leave = get_object_or_404(LeaveRequest, id=request_id)
    
    if not leave.supervisor_approved:
        leave.supervisor_approved = True
        leave.supervisor = request.user
        leave.supervisor_approved_at = timezone.now()
    elif not leave.warden_approved:
        leave.warden_approved = True
        leave.warden = request.user
        leave.warden_approved_at = timezone.now()
        leave.status = LeaveRequest.STATUS_APPROVED
    
    leave.save()
    messages.success(request, "Request approved.")
    return redirect("approval_dashboard")

@login_required
@permission_required("gate.can_approve_leave", raise_exception=True)
@require_http_methods(["POST"])
def reject_leave(request, request_id):
    leave = get_object_or_404(LeaveRequest, id=request_id)
    leave.status = LeaveRequest.STATUS_REJECTED
    leave.rejection_reason = request.POST.get("rejection_reason", "No reason provided")
    leave.save()
    messages.warning(request, "Request rejected.")
    return redirect("approval_dashboard")

# =========================================================
# ADMIN HELPERS (ADD STUDENT, CSV, ETC)
# =========================================================
@login_required
def add_student(request):
    if request.user.groups.filter(name="Guard").exists():
        messages.error(request, "Access Denied.")
        return redirect("home")

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added.")
            return redirect("home")
    else:
        form = StudentForm()
    return render(request, "gate/add_student.html", {"form": form})

@login_required
def import_students_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            import csv, io
            reader = csv.reader(io.StringIO(request.FILES["file"].read().decode("utf-8")))
            for row in reader:
                if len(row) < 2 or "enrollment" in row[0].lower(): continue
                Student.objects.update_or_create(
                    enrollment_number=row[0].strip(),
                    defaults={"full_name": row[1].strip()}
                )
            messages.success(request, "CSV Imported.")
            return redirect("home")
    else:
        form = CSVUploadForm()
    return render(request, "gate/import_students_csv.html", {"form": form})

@login_required
def inside_list(request):
    return render(request, "gate/list.html", {"students": Student.objects.filter(is_inside=True), "title": "Inside Campus"})

@login_required
def outside_list(request):
    return render(request, "gate/list.html", {"students": Student.objects.filter(is_inside=False), "title": "Outside Campus"})

@csrf_exempt
@require_http_methods(["POST"])
def api_check(request):
    enr = request.POST.get("enrollment_number", "").strip()
    try:
        s = Student.objects.get(enrollment_number__iexact=enr)
        return JsonResponse({"found": True, "name": s.full_name, "is_inside": s.is_inside})
    except Student.DoesNotExist:
        return JsonResponse({"found": False}, status=404)