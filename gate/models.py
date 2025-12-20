from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Student(models.Model):
    YEAR_CHOICES = [
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year'),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    enrollment_number = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=120)
    photo = models.ImageField(upload_to="student_photos/", blank=True, null=True)

    course = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(choices=YEAR_CHOICES, default=1)

    hostel_name = models.CharField(max_length=50, blank=True)
    room_number = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    guardian_name = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=15, blank=True)

    is_inside = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["enrollment_number"]
        permissions = [
            ("can_toggle_status", "Can toggle gate IN/OUT"),
            ("can_approve_leave", "Can approve leave requests"),
        ]

    def __str__(self):
        return f"{self.enrollment_number} - {self.full_name}"


class MovementLog(models.Model):
    IN = "IN"
    OUT = "OUT"
    DIRECTION_CHOICES = [(IN, "IN"), (OUT, "OUT")]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="logs")
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.student.enrollment_number} {self.direction}"


class LeaveRequest(models.Model):
    OUTPASS = "Outpass"
    LEAVE = "Leave"
    TYPE_CHOICES = [(OUTPASS, "Outpass"), (LEAVE, "Leave")]

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_EXPIRED = "expired"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_EXPIRED, "Expired"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="leave_requests")
    request_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    reason = models.TextField()
    destination = models.CharField(max_length=200, blank=True)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()

    supervisor_approved = models.BooleanField(default=False)
    supervisor = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="supervisor_actions"
    )
    supervisor_approved_at = models.DateTimeField(null=True, blank=True)

    warden_approved = models.BooleanField(default=False)
    warden = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="warden_actions"
    )
    warden_approved_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    rejection_reason = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.to_date <= self.from_date:
            raise ValidationError("End date must be after start date")

    @property
    def is_active(self):
        now = timezone.now()
        return self.status == self.STATUS_APPROVED and self.from_date <= now <= self.to_date

