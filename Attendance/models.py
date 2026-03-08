from django.conf import settings
from django.db import models


class AttendanceStatus(models.TextChoices):
    P = "P", "Present"
    A = "A", "Absent"
    L = "L", "Late"
    WO = "WO", "Weekly Off"


class Attendance(models.Model):
    """Processed daily attendance per employee. Derived from BiometricLog + shift rules."""

    employee = models.ForeignKey(
        "Employee.Employee",
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    date = models.DateField(db_index=True)
    first_in = models.DateTimeField(null=True, blank=True)
    last_out = models.DateTimeField(null=True, blank=True)
    working_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    late_minutes = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(
        max_length=4,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.A,
    )
    processed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance"
        ordering = ["-date", "employee"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "date"],
                name="attendance_employee_date_unique",
            )
        ]
        verbose_name_plural = "attendances"

    def __str__(self):
        return f"{self.employee.name} - {self.date} ({self.get_status_display()})"


class AttendanceRunStatus(models.TextChoices):
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"


class AttendanceRun(models.Model):
    """Tracks each attendance processing run per office (for reprocessing and audit)."""

    office = models.ForeignKey(
        "Organization.Office",
        on_delete=models.CASCADE,
        related_name="attendance_runs",
    )
    from_datetime = models.DateTimeField()
    to_datetime = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=AttendanceRunStatus.choices,
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_run"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.office.name} {self.from_datetime}–{self.to_datetime} ({self.status})"


class RegularizationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending Approval"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class AttendanceRegularization(models.Model):
    """Request to correct/override a processed attendance record."""

    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name="regularizations",
    )
    employee = models.ForeignKey(
        "Employee.Employee",
        on_delete=models.CASCADE,
        related_name="regularizations",
    )
    date = models.DateField(db_index=True)

    new_status = models.CharField(max_length=4, choices=AttendanceStatus.choices)
    new_first_in = models.DateTimeField(null=True, blank=True)
    new_last_out = models.DateTimeField(null=True, blank=True)
    reason = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=RegularizationStatus.choices,
        default=RegularizationStatus.PENDING,
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="regularization_requests",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="regularization_reviews",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_regularization"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee.name} – {self.date} ({self.get_status_display()})"
